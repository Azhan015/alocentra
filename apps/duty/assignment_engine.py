import random
from datetime import timedelta
from .models import AssignmentResult, DutySessionRoom, FacultyDutyAssignment

def generate_assignments(session):
    rooms = list(session.session_rooms.all())
    assignments = list(session.faculty_assignments.filter(is_reliever=False))
    relievers = list(session.faculty_assignments.filter(is_reliever=True))
    
    if not session.date_from or not session.date_to:
        return
        
    current_date = session.date_from
    days = []
    while current_date <= session.date_to:
        if current_date.weekday() != 6: # Skip Sundays
            days.append(current_date)
        current_date += timedelta(days=1)
        
    slots = []
    for d in days:
        for r in rooms:
            slots.append((d, r.room))
            
    available_pool = []
    for a in assignments:
        available_pool.extend([a.faculty] * a.no_of_duties)
    
    random.shuffle(available_pool)
        
    results = []
    for date, room in slots:
        if not available_pool:
            break
        
        assigned = False
        for i, fac in enumerate(available_pool):
            already_assigned = any(r.faculty == fac and r.date == date for r in results)
            if not already_assigned:
                chosen_fac = available_pool.pop(i)
                res = AssignmentResult(session=session, date=date, room=room, faculty=chosen_fac)
                results.append(res)
                assigned = True
                break
                
        # If we couldn't find a faculty without a clash, just force assign the first available one
        # to guarantee the room is covered, though ideally we'd want to backtrack.
        if not assigned and available_pool:
             chosen_fac = available_pool.pop(0)
             res = AssignmentResult(session=session, date=date, room=room, faculty=chosen_fac)
             results.append(res)
                
    AssignmentResult.objects.bulk_create(results)
    
    reliever_results = []
    
    # Track how many duties each reliever has been assigned
    reliever_counts = {r_assign.faculty_id: 0 for r_assign in relievers}
    
    for date in days:
        if len(rooms) > 0:
            for r_assign in relievers:
                # Check if this reliever has reached their requested maximum
                if reliever_counts[r_assign.faculty_id] < r_assign.reliever_room_count:
                    room_obj = rooms[0].room
                    reliever_results.append(AssignmentResult(session=session, date=date, room=room_obj, faculty=r_assign.faculty, is_reliever=True))
                    reliever_counts[r_assign.faculty_id] += 1
    
    AssignmentResult.objects.bulk_create(reliever_results)
