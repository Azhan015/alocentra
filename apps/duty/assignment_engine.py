import logging
import random
from datetime import timedelta
from django.db import transaction
from django.db.models import Count
from .models import DutyAssignment
from apps.timetable.models import TimetableCell

logger = logging.getLogger(__name__)


def _session_days(session):
    days = []
    current_date = session.date_from
    while current_date <= session.date_to:
        if current_date.weekday() != 6:
            days.append(current_date)
        current_date += timedelta(days=1)
    return days


def _timetable_exam_dates(timetable):
    """
    Return actual exam dates for the timetable.
    A date is considered an exam day if at least one timetable cell on that date
    has an assigned course (i.e. course is not null).
    """
    if not timetable:
        return []
    dates = list(
        TimetableCell.objects.filter(timetable=timetable, course__isnull=False)
        .values_list('date', flat=True)
        .distinct()
    )
    dates = sorted(dates)
    # Timetable builder skips Sundays, but keep this guard for safety.
    return [d for d in dates if d.weekday() != 6]


def evaluate_shortage(session):
    """
    Return coverage gaps for both invigilator and reliever expectations.
    - invigilator: every (date, room) must have at least one non-reliever assignment
    - reliever: every (date, room) should have at least one reliever assignment
    """
    rooms = [sr.room for sr in session.session_rooms.select_related('room').all()]
    if session.timetable:
        days = _timetable_exam_dates(session.timetable)
    else:
        days = _session_days(session) if session.date_from and session.date_to else []
    
    # Get exams per day to calculate required slots
    exams_per_day = getattr(session.timetable, 'exams_per_day', 1) if session.timetable else 1
    
    inv_map = {
        (row['date'], row['room_id'])
        for row in DutyAssignment.objects.filter(session=session, is_reliever=False).values('date', 'room_id')
    }
    rel_map = {
        (row['date'], row['room_id'])
        for row in DutyAssignment.objects.filter(session=session, is_reliever=True).values('date', 'room_id')
    }
    inv_short = []
    rel_short = []
    for d in days:
        for room in rooms:
            # Each room needs assignments for each exam slot per day
            for slot_num in range(exams_per_day):
                key = (d, room.id)
                if key not in inv_map:
                    inv_short.append((d, room.room_no))
                if key not in rel_map:
                    rel_short.append((d, room.room_no))
    return {'invigilator': inv_short, 'reliever': rel_short}


@transaction.atomic
def generate_assignments(session):
    """Build DutyAssignment rows: one invigilator slot per (date, room) and reliever slots."""
    logger.info(
        'generate_assignments start session_id=%s status=%s dates=%s–%s',
        session.id,
        session.status,
        session.date_from,
        session.date_to,
    )

    session_rooms = list(session.session_rooms.select_related('room').all())
    assignments = list(session.faculty_assignments.filter(is_reliever=False).select_related('faculty'))
    relievers = list(session.faculty_assignments.filter(is_reliever=True).select_related('faculty'))

    if not session.date_from or not session.date_to:
        logger.warning('generate_assignments: session %s missing date_from/date_to; skipping.', session.id)
        return

    if not session_rooms:
        logger.warning('generate_assignments: session %s has no rooms selected; skipping.', session.id)
        return

    if not assignments:
        logger.warning(
            'generate_assignments: session %s has no invigilators (step 2); no room assignments created.',
            session.id,
        )

    if session.timetable:
        days = _timetable_exam_dates(session.timetable)
    else:
        days = _session_days(session)
    if not days:
        logger.warning('generate_assignments: session %s has no timetable exam dates; skipping.', session.id)
        return

    slots = []
    # Create multiple slots per date based on timetable's exams_per_day setting
    exams_per_day = getattr(session.timetable, 'exams_per_day', 1) if session.timetable else 1
    
    for d in days:
        for sr in session_rooms:
            # Create multiple slots for this date if exams_per_day > 1
            for slot_num in range(exams_per_day):
                slots.append((d, sr.room, slot_num))  # Add slot_num for tracking

    available_pool = []
    for a in assignments:
        n = max(0, int(a.no_of_duties))
        available_pool.extend([a.faculty] * n)

    random.shuffle(available_pool)
    logger.debug(
        'generate_assignments: slots=%s pool_size=%s rooms=%s days=%s',
        len(slots),
        len(available_pool),
        len(session_rooms),
        len(days),
    )

    DUTY_CAP = 10
    skipped_due_to_cap = set()

    existing_counts = {
        row['faculty_id']: row['c']
        for row in DutyAssignment.objects.filter(session=session, is_reliever=False)
        .values('faculty_id')
        .annotate(c=Count('id'))
    }
    existing_day_faculty = {
        (row['date'], row['faculty_id'])
        for row in DutyAssignment.objects.filter(session=session, is_reliever=False).values('date', 'faculty_id')
    }

    results = []
    for date, room, slot_num in slots:
        if not available_pool:
            break

        assigned = False
        for i, fac in enumerate(available_pool):
            if existing_counts.get(fac.id, 0) >= DUTY_CAP:
                skipped_due_to_cap.add(fac.id)
                continue
            # One invigilating faculty can supervise only one room per day.
            if (date, fac.id) in existing_day_faculty:
                continue
            already_assigned = any(r.faculty_id == fac.id and r.date == date for r in results)
            if not already_assigned:
                chosen_fac = available_pool.pop(i)
                existing_counts[chosen_fac.id] = existing_counts.get(chosen_fac.id, 0) + 1
                existing_day_faculty.add((date, chosen_fac.id))
                results.append(
                    DutyAssignment(session=session, date=date, room=room, faculty=chosen_fac)
                )
                assigned = True
                break

        if not assigned and available_pool:
            # Force-assign the first non-capped faculty (if any)
            forced_idx = None
            for j, fac in enumerate(available_pool):
                if existing_counts.get(fac.id, 0) < DUTY_CAP:
                    if (date, fac.id) in existing_day_faculty:
                        continue
                    forced_idx = j
                    break
                skipped_due_to_cap.add(fac.id)
            if forced_idx is not None:
                chosen_fac = available_pool.pop(forced_idx)
                existing_counts[chosen_fac.id] = existing_counts.get(chosen_fac.id, 0) + 1
                existing_day_faculty.add((date, chosen_fac.id))
                results.append(
                    DutyAssignment(session=session, date=date, room=room, faculty=chosen_fac)
                )

    if results:
        DutyAssignment.objects.bulk_create(results)
        print(f'[duty] bulk_created {len(results)} invigilator DutyAssignment rows for session {session.id}')
    if skipped_due_to_cap:
        msg = f'[duty] skipped {len(skipped_due_to_cap)} faculty due to cap={DUTY_CAP} for session {session.id}'
        logger.warning(msg)
        print(msg)

    reliever_results = []
    # Track per-day rooms already covered by relievers to avoid duplicate room visits on same day.
    day_room_covered = set()
    # Include pre-existing reliever rows for idempotency safety.
    for row in DutyAssignment.objects.filter(session=session, is_reliever=True).values('date', 'room_id'):
        day_room_covered.add((row['date'], row['room_id']))

    for date in days:
        if not session_rooms:
            continue
        # For each reliever, assign distinct rooms on this day up to selected room count.
        for r_assign in relievers:
            assigned_today_for_this_reliever = set()
            for room_wrap in session_rooms:
                if len(assigned_today_for_this_reliever) >= r_assign.reliever_room_count:
                    break
                room_obj = room_wrap.room
                key = (date, room_obj.id)
                if key in day_room_covered:
                    continue
                # Ensure same reliever doesn't get same room twice in a day.
                if room_obj.id in assigned_today_for_this_reliever:
                    continue
                reliever_results.append(
                    DutyAssignment(
                        session=session,
                        date=date,
                        room=room_obj,
                        faculty=r_assign.faculty,
                        is_reliever=True,
                    )
                )
                assigned_today_for_this_reliever.add(room_obj.id)
                day_room_covered.add(key)

    if reliever_results:
        DutyAssignment.objects.bulk_create(reliever_results)
        print(f'[duty] bulk_created {len(reliever_results)} reliever DutyAssignment rows for session {session.id}')

    logger.info(
        'generate_assignments done session_id=%s invigilator_rows=%s reliever_rows=%s',
        session.id,
        len(results),
        len(reliever_results),
    )
    return evaluate_shortage(session)


def get_timetable_exam_dates_for_session(session):
    """Shared helper for views/templates to keep exam-date filtering consistent."""
    if session.timetable:
        return _timetable_exam_dates(session.timetable)
    return _session_days(session) if session.date_from and session.date_to else []
