import json
from datetime import timedelta
from io import BytesIO

from django.contrib.auth.decorators import login_required
from django.http import HttpResponse, JsonResponse
from django.shortcuts import get_object_or_404, render
from apps.accounts.utils import permission_required_custom, get_user_permissions
from openpyxl import Workbook
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Spacer, Paragraph, Table, TableStyle

from apps.duty.models import ExamType
from .models import Course, ExamTimetable, Program, TimetableCell


@login_required
@permission_required_custom('can_view_timetable')
def timetable_view(request):
    sessions = ExamTimetable.objects.all().order_by('-created_at')
    context = {'sessions': sessions, 'permissions': get_user_permissions(request.user)}
    return render(request, 'timetable/list.html', context)


def _grid_rows_for_builder():
    rows = []
    for prog in Program.objects.select_related('department').order_by('department__name', 'name'):
        for sem in range(1, prog.total_semesters + 1):
            rows.append(
                {
                    'program_id': prog.id,
                    'program_name': prog.name,
                    'department_name': prog.department.name,
                    'semester': sem,
                    'row_key': f'{prog.id}-{sem}',
                    'program_type': prog.program_type,
                }
            )
    return rows


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
                    exam_type_id=exam_type_id,
                    date_from=date_from,
                    date_to=date_to,
                    created_by=request.user,
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
                    program_id=c['program_id'],
                    semester=int(c['semester']),
                    date=c['date'],
                    course_id=c.get('course_id') or None,
                )
            return JsonResponse({'success': True, 'id': timetable.id})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    exam_types = ExamType.objects.all().order_by('name')
    grid_rows = _grid_rows_for_builder()
    academic_courses = list(
        Course.objects.select_related('program', 'specialisation')
        .order_by('program_id', 'semester', 'code', 'name')
        .values('id', 'name', 'code', 'program_id', 'semester', 'specialisation_id')
    )

    existing_cells = []
    if timetable:
        for row in TimetableCell.objects.filter(timetable=timetable).values(
            'program_id', 'semester', 'date', 'course_id'
        ):
            existing_cells.append(
                {
                    'program_id': row['program_id'],
                    'semester': row['semester'],
                    'date': row['date'].isoformat() if row['date'] else None,
                    'course_id': row['course_id'],
                }
            )

    context = {
        'timetable': timetable,
        'exam_types': exam_types,
        'grid_rows_json': json.dumps(grid_rows,default=str,ensure_ascii=False),
        'academic_courses_json': json.dumps(academic_courses, default=str,ensure_ascii=False),
        'existing_cells_json': json.dumps(existing_cells, default=str,ensure_ascii=False),
        'permissions': get_user_permissions(request.user),
    }
    return render(request, 'timetable/builder.html', context)


def _timetable_dates_from_cells_or_range(timetable):
    """
    Prefer dates that are present in timetable cells (supports "No Exam" removed dates),
    fallback to full date range if cells are not available.
    """
    dates = sorted(
        {
            row['date']
            for row in TimetableCell.objects.filter(timetable=timetable)
            .values('date')
            .distinct()
        }
    )
    if dates:
        return dates
    # Fallback for old rows that may not have explicit blank cells persisted.
    all_dates = []
    current = timetable.date_from
    while current <= timetable.date_to:
        if current.weekday() != 6:  # skip Sunday
            all_dates.append(current)
        current += timedelta(days=1)
    return all_dates


def _timetable_matrix(timetable):
    cells = list(
        TimetableCell.objects.filter(timetable=timetable)
        .select_related('program', 'course')
        .order_by('program__department__name', 'program__name', 'semester', 'date')
    )
    dates = _timetable_dates_from_cells_or_range(timetable)
    row_keys = sorted({(c.program_id, c.semester) for c in cells}, key=lambda x: (x[0], x[1]))
    # Build label map
    program_ids = [p for p, _ in row_keys]
    programs = {p.id: p for p in Program.objects.filter(id__in=program_ids).select_related('department')}
    labels = {}
    for pid, sem in row_keys:
        p = programs.get(pid)
        if p:
            labels[(pid, sem)] = f'{p.department.name} — {p.name} (Sem {sem})'
        else:
            labels[(pid, sem)] = f'Program {pid} (Sem {sem})'

    # Lookup course text by key
    course_lookup = {}
    for c in cells:
        key = (c.program_id, c.semester, c.date)
        if c.course:
            text = f'{c.course.code} — {c.course.name}' if c.course.code else c.course.name
        else:
            text = '--'
        course_lookup[key] = text

    return dates, row_keys, labels, course_lookup


@login_required
@permission_required_custom('can_view_timetable')
def timetable_export_excel(request, id):
    timetable = get_object_or_404(ExamTimetable, id=id)
    dates, row_keys, labels, course_lookup = _timetable_matrix(timetable)

    wb = Workbook()
    ws = wb.active
    ws.title = 'Timetable'
    ws.append(['Program'] + [d.strftime('%Y-%m-%d') for d in dates])

    for pid, sem in row_keys:
        row = [labels[(pid, sem)]]
        for d in dates:
            row.append(course_lookup.get((pid, sem, d), '--'))
        ws.append(row)

    # mild readability formatting
    ws.column_dimensions['A'].width = 40

    output = BytesIO()
    wb.save(output)
    output.seek(0)
    response = HttpResponse(
        output.getvalue(),
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    )
    response['Content-Disposition'] = f'attachment; filename="timetable_{timetable.id}.xlsx"'
    return response


@login_required
@permission_required_custom('can_view_timetable')
def timetable_export_pdf(request, id):
    timetable = get_object_or_404(ExamTimetable, id=id)
    dates, row_keys, labels, course_lookup = _timetable_matrix(timetable)

    output = BytesIO()
    doc = SimpleDocTemplate(output, pagesize=landscape(A4), leftMargin=20, rightMargin=20, topMargin=20, bottomMargin=20)
    styles = getSampleStyleSheet()
    elements = [
        Paragraph(f'Timetable: {timetable.exam_type.name}', styles['Heading3']),
        Paragraph(f'Date Range: {timetable.date_from} to {timetable.date_to}', styles['Normal']),
        Spacer(1, 10),
    ]

    data = [['Program'] + [d.strftime('%d %b') for d in dates]]
    for pid, sem in row_keys:
        r = [labels[(pid, sem)]]
        for d in dates:
            r.append(course_lookup.get((pid, sem, d), '--'))
        data.append(r)

    table = Table(data, repeatRows=1)
    table.setStyle(
        TableStyle(
            [
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f0f0f0')),
                ('GRID', (0, 0), (-1, -1), 0.4, colors.grey),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('FONTSIZE', (0, 0), (-1, -1), 8),
            ]
        )
    )
    elements.append(table)
    doc.build(elements)
    output.seek(0)
    response = HttpResponse(output.getvalue(), content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="timetable_{timetable.id}.pdf"'
    return response
