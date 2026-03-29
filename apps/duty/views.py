import logging
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import permission_required_custom, get_user_permissions
from apps.rooms.models import Room
from apps.faculty.models import Faculty
from apps.timetable.models import ExamTimetable
from .models import ExamType, DutySession, DutySessionRoom, FacultyDutyAssignment, DutyAssignment

logger = logging.getLogger(__name__)


@login_required
@permission_required_custom('can_assign_duty')
def duty_wizard_start(request):
    permissions = get_user_permissions(request.user)
    if request.method == 'POST':
        title = request.POST.get('title')
        timetable_id = request.POST.get('timetable')
        date_from = request.POST.get('date_from')
        date_to = request.POST.get('date_to')
        timetable = get_object_or_404(ExamTimetable, id=timetable_id)

        session = DutySession.objects.create(
            title=title,
            exam_type=timetable.exam_type,
            timetable=timetable,
            date_from=date_from,
            date_to=date_to,
            created_by=request.user,
        )
        request.session['current_duty_session_id'] = session.id
        request.session['current_timetable_id'] = timetable.id
        return redirect('duty:wizard_step1')

    timetables = ExamTimetable.objects.select_related('exam_type').order_by('-created_at')
    context = {'permissions': permissions, 'timetables': timetables}
    return render(request, 'duty/wizard_start.html', context)


@login_required
@permission_required_custom('can_assign_duty')
def timetable_dates_api(request, timetable_id):
    tt = get_object_or_404(ExamTimetable, id=timetable_id)
    return JsonResponse(
        {
            'success': True,
            'date_from': tt.date_from.isoformat() if tt.date_from else '',
            'date_to': tt.date_to.isoformat() if tt.date_to else '',
        }
    )


@login_required
@permission_required_custom('can_assign_duty')
def duty_wizard_step1(request):
    session_id = request.session.get('current_duty_session_id')
    if not session_id:
        return redirect('duty:wizard_start')

    session = get_object_or_404(DutySession, id=session_id)
    rooms = Room.objects.filter(is_active=True).order_by('room_no')

    if request.method == 'POST':
        selected_rooms = request.POST.getlist('rooms')
        DutySessionRoom.objects.filter(session=session).delete()
        for r_id in selected_rooms:
            DutySessionRoom.objects.create(session=session, room_id=r_id)
        return redirect('duty:wizard_step2')

    selected_room_ids = session.session_rooms.values_list('room_id', flat=True)
    context = {
        'session': session,
        'rooms': rooms,
        'selected_room_ids': selected_room_ids,
        'permissions': get_user_permissions(request.user),
    }
    return render(request, 'duty/wizard_step1.html', context)


@login_required
@permission_required_custom('can_assign_duty')
def duty_wizard_step2(request):
    session_id = request.session.get('current_duty_session_id') or request.GET.get('session_id')
    if not session_id:
        return redirect('duty:wizard_start')
    request.session['current_duty_session_id'] = int(session_id)

    session = get_object_or_404(DutySession, id=session_id)
    faculties = Faculty.objects.filter(is_active=True).order_by('name')

    if request.method == 'POST':
        selected_faculties = request.POST.getlist('faculty')
        input_error = None
        parsed = []
        for f_id in selected_faculties:
            raw = request.POST.get(f'duty_count_{f_id}', '1')
            try:
                count = max(1, int(raw))
            except (TypeError, ValueError):
                count = 1
            if count > 10:
                input_error = 'Maximum 10 duties allowed per faculty.'
                break
            parsed.append((f_id, count))
        if input_error:
            assignments = {}
            for f_id, count in parsed:
                assignments[int(f_id)] = count
            context = {
                'session': session,
                'faculties': faculties,
                'assignments': assignments,
                'permissions': get_user_permissions(request.user),
                'input_error': input_error,
            }
            return render(request, 'duty/wizard_step2.html', context)

        FacultyDutyAssignment.objects.filter(session=session).delete()
        for f_id, count in parsed:
            FacultyDutyAssignment.objects.create(session=session, faculty_id=f_id, no_of_duties=count)
        return redirect('duty:wizard_step3')

    assignments = {
        a.faculty_id: a.no_of_duties for a in session.faculty_assignments.filter(is_reliever=False)
    }
    context = {
        'session': session,
        'faculties': faculties,
        'assignments': assignments,
        'permissions': get_user_permissions(request.user),
    }
    return render(request, 'duty/wizard_step2.html', context)


@login_required
@permission_required_custom('can_assign_duty')
def duty_wizard_step3(request):
    session_id = request.session.get('current_duty_session_id')
    if not session_id:
        return redirect('duty:wizard_start')

    session = get_object_or_404(DutySession, id=session_id)
    assigned_ids = session.faculty_assignments.filter(is_reliever=False).values_list('faculty_id', flat=True)
    faculties = Faculty.objects.filter(is_active=True).exclude(id__in=assigned_ids).order_by('name')

    if request.method == 'POST':
        selected_relievers = request.POST.getlist('relievers')
        FacultyDutyAssignment.objects.filter(session=session, is_reliever=True).delete()
        for f_id in selected_relievers:
            raw_rc = request.POST.get(f'reliever_rooms_{f_id}', '5')
            try:
                room_count = max(1, int(raw_rc))
            except (TypeError, ValueError):
                room_count = 5
            FacultyDutyAssignment.objects.create(
                session=session, faculty_id=f_id, is_reliever=True, reliever_room_count=room_count
            )

        session.status = 'FINALIZED'
        session.save()
        del request.session['current_duty_session_id']
        if 'current_timetable_id' in request.session:
            del request.session['current_timetable_id']
        return redirect('duty:results', session_id=session.id)

    reliever_assignments = {
        a.faculty_id: a.reliever_room_count
        for a in session.faculty_assignments.filter(is_reliever=True)
    }
    context = {
        'session': session,
        'faculties': faculties,
        'reliever_assignments': reliever_assignments,
        'permissions': get_user_permissions(request.user),
    }
    return render(request, 'duty/wizard_step3.html', context)


@login_required
@permission_required_custom('can_view_duty')
def duty_results(request, session_id):
    session = get_object_or_404(DutySession, id=session_id)
    results = DutyAssignment.objects.filter(session=session).select_related('faculty', 'room').order_by(
        'date', 'room__room_no'
    )
    shortage = {'invigilator': [], 'reliever': []}

    if not results.exists() and session.status == 'FINALIZED':
        from .assignment_engine import generate_assignments, evaluate_shortage

        try:
            shortage = generate_assignments(session) or {'invigilator': [], 'reliever': []}
        except Exception:
            logger.exception(
                'Duty assignment generation failed for session id=%s title=%r',
                session.id,
                session.title,
            )
        results = DutyAssignment.objects.filter(session=session).select_related('faculty', 'room').order_by(
            'date', 'room__room_no'
        )
    else:
        from .assignment_engine import evaluate_shortage
        shortage = evaluate_shortage(session)

    combined = []
    seen = set()
    for kind in ('invigilator', 'reliever'):
        for d, room_no in shortage.get(kind, []):
            key = (d, room_no)
            if key in seen:
                continue
            seen.add(key)
            combined.append((d, room_no))
    combined.sort(key=lambda x: (x[0], x[1]))

    context = {
        'session': session,
        'results': results,
        'permissions': get_user_permissions(request.user),
        'shortage_pairs': combined,
        'has_shortage': bool(combined),
    }
    return render(request, 'duty/results.html', context)


@login_required
@permission_required_custom('can_view_duty')
def duty_sessions_list(request):
    sessions = DutySession.objects.filter(created_by=request.user).order_by('-created_at')
    context = {'sessions': sessions, 'permissions': get_user_permissions(request.user)}
    return render(request, 'duty/sessions_list.html', context)
