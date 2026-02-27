from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import permission_required_custom, get_user_permissions
from .models import ExamTimetable, TimetableCell, Department, Course, Subject
from apps.duty.models import ExamType
import json

@login_required
@permission_required_custom('can_view_timetable')
def timetable_view(request):
    sessions = ExamTimetable.objects.all().order_by('-created_at')
    context = {'sessions': sessions, 'permissions': get_user_permissions(request.user)}
    return render(request, 'timetable/list.html', context)

@login_required
@permission_required_custom('can_edit_timetable')
def timetable_builder(request, id=None):
    if id:
        timetable = get_object_or_404(ExamTimetable, id=id)
    else:
        timetable = None

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            exam_type_id = data.get('exam_type')
            date_from = data.get('date_from')
            date_to = data.get('date_to')
            cells = data.get('cells', [])
            
            if not timetable:
                timetable = ExamTimetable.objects.create(
                    exam_type_id=exam_type_id, date_from=date_from, date_to=date_to, created_by=request.user
                )
            else:
                timetable.exam_type_id = exam_type_id
                timetable.date_from = date_from
                timetable.date_to = date_to
                timetable.save()
                
            TimetableCell.objects.filter(timetable=timetable).delete()
            for c in cells:
                TimetableCell.objects.create(
                    timetable=timetable,
                    course_id=c['course_id'],
                    date=c['date'],
                    subject_id=c.get('subject_id') or None
                )
            return JsonResponse({'success': True, 'id': timetable.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    exam_types = ExamType.objects.all()
    courses = Course.objects.all().select_related('department')
    subjects = list(Subject.objects.all().values('id', 'name', 'code', 'course_id'))
    
    existing_cells = []
    if timetable:
        existing_cells = list(TimetableCell.objects.filter(timetable=timetable).values('course_id', 'date', 'subject_id'))
        
    context = {
        'timetable': timetable,
        'exam_types': exam_types,
        'courses': courses,
        'subjects_json': json.dumps(subjects),
        'existing_cells_json': json.dumps(existing_cells, default=str),
        'permissions': get_user_permissions(request.user)
    }
    return render(request, 'timetable/builder.html', context)
