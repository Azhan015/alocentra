from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import permission_required_custom, get_user_permissions
from .models import Faculty
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST, require_http_methods
import json

@login_required
@permission_required_custom('can_view_faculty')
def faculty_view(request):
    permissions = get_user_permissions(request.user)
    q = request.GET.get('q', '')
    d = request.GET.get('dept', '')
    
    faculty_list = Faculty.objects.filter(is_active=True).order_by('name')
    if q:
        faculty_list = faculty_list.filter(name__icontains=q)
    if d:
        faculty_list = faculty_list.filter(department__icontains=d)
        
    paginator = Paginator(faculty_list, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    departments = (
        Faculty.objects.exclude(department__isnull=True)
        .exclude(department='')
        .values_list('department', flat=True)
        .distinct()
        .order_by('department')
    )

    context = {
        'permissions': permissions,
        'page_obj': page_obj,
        'faculty_count': faculty_list.count(),
        'departments': list(departments),
        'q': q,
        'd': d,
    }
    return render(request, 'faculty/faculty.html', context)

@login_required
@permission_required_custom('can_add_faculty')
@require_POST
def add_faculty(request):
    try:
        name = request.POST.get('name')
        designation = request.POST.get('designation')
        email = request.POST.get('email')
        department = request.POST.get('department')
        if not name or not designation:
            return JsonResponse({'success': False, 'message': 'Name and designation are required'})
        
        # Validate email if provided
        if email and not email.lower().endswith('@sfscollege.in'):
            return JsonResponse({'success': False, 'message': 'Email must be a valid sfscollege.in address'})
        
        # Check for duplicate faculty (name + department)
        duplicate_query = Faculty.objects.filter(name__iexact=name, is_active=True)
        if department:
            duplicate_query = duplicate_query.filter(department__iexact=department)
        elif email:
            # If no department, check by email if provided
            duplicate_query = Faculty.objects.filter(email__iexact=email, is_active=True)
        
        if duplicate_query.exists():
            if department:
                return JsonResponse({'success': False, 'message': f'Faculty "{name}" already exists in department "{department}"'})
            elif email:
                return JsonResponse({'success': False, 'message': f'Faculty with email "{email}" already exists'})
            else:
                return JsonResponse({'success': False, 'message': f'Faculty "{name}" already exists'})
        
        Faculty.objects.create(name=name, designation=designation, email=email, department=department, created_by=request.user)
        return JsonResponse({'success': True, 'message': 'Faculty added successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_add_faculty')
@require_http_methods(['GET', 'POST'])
def edit_faculty(request, id):
    faculty = get_object_or_404(Faculty, id=id, is_active=True)
    if request.method == 'GET':
        return JsonResponse({
            'name': faculty.name, 'designation': faculty.designation, 
            'email': faculty.email, 'department': faculty.department
        })
    elif request.method == 'POST':
        faculty.name = request.POST.get('name')
        faculty.designation = request.POST.get('designation')
        email = request.POST.get('email')
        faculty.department = request.POST.get('department')
        
        # Validate email if provided
        if email and not email.lower().endswith('@sfscollege.in'):
            return JsonResponse({'success': False, 'message': 'Email must be a valid sfscollege.in address'})
        
        faculty.email = email
        faculty.save()
        return JsonResponse({'success': True, 'message': 'Faculty updated'})

@login_required
@permission_required_custom('can_delete_faculty')
@require_POST
def delete_faculty(request, id):
    try:
        updated = Faculty.objects.filter(id=id).update(is_active=False)
        if updated == 0:
            return JsonResponse({'success': False, 'message': 'Faculty not found'})
        return JsonResponse({'success': True, 'message': 'Faculty deleted'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_delete_faculty')
@require_POST
def bulk_delete_faculty(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        Faculty.objects.filter(id__in=ids).update(is_active=False)
        return JsonResponse({'success': True, 'message': f'{len(ids)} faculty deleted'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_add_faculty')
@require_POST
def import_faculty(request):
    try:
        data = json.loads(request.body)
        faculty_data = data.get('faculty', [])
    except Exception as e:
        return JsonResponse({'success': False, 'message': f'Invalid JSON: {str(e)}'})

    imported = 0
    skipped = 0
    errors = []

    for idx, f in enumerate(faculty_data, start=1):
        try:
            # Support both lowercase and title-case keys from Excel parsers
            name = str(f.get('name') or f.get('Name') or '').strip()
            designation = str(f.get('designation') or f.get('Designation') or '').strip()
            department = str(f.get('department') or f.get('Department') or '').strip()
            email_raw = str(f.get('email') or f.get('Email') or '').strip()

            if not name or not designation:
                errors.append({'row': idx, 'reason': 'Missing name or designation'})
                continue

            # Only validate email if one is provided — do NOT skip the row, just clear invalid email
            email = ''
            if email_raw:
                if email_raw.lower().endswith('@sfscollege.in'):
                    email = email_raw
                # If email is provided but invalid domain, import faculty without email

            # Avoid exact duplicates
            if Faculty.objects.filter(name=name, department=department, is_active=True).exists():
                skipped += 1
                continue

            Faculty.objects.create(
                name=name,
                designation=designation,
                department=department,
                email=email if email else None,
                created_by=request.user,
            )
            imported += 1

        except Exception as e:
            errors.append({'row': idx, 'reason': str(e)})

    return JsonResponse({
        'success': True,
        'message': f'Successfully imported {imported} faculty members. {skipped} duplicates skipped. {len(errors)} errors.',
        'imported': imported,
        'skipped': skipped,
        'errors': errors,
    })