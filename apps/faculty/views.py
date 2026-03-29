from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import permission_required_custom, get_user_permissions
from .models import Faculty
from django.core.paginator import Paginator
from django.views.decorators.http import require_POST
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
        
        Faculty.objects.create(name=name, designation=designation, email=email, department=department, created_by=request.user)
        return JsonResponse({'success': True, 'message': 'Faculty added successfully'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_add_faculty')
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
        faculty.email = request.POST.get('email')
        faculty.department = request.POST.get('department')
        faculty.save()
        return JsonResponse({'success': True, 'message': 'Faculty updated'})

@login_required
@permission_required_custom('can_delete_faculty')
@require_POST
def delete_faculty(request, id):
    faculty = get_object_or_404(Faculty, id=id)
    faculty.is_active = False
    faculty.save()
    return JsonResponse({'success': True, 'message': 'Faculty deleted'})

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
        imported = 0
        skipped = 0
        for f in faculty_data:
            name = str(f.get('name')).strip() if f.get('name') else ''
            designation = str(f.get('designation')).strip() if f.get('designation') else ''
            department = str(f.get('department')).strip() if f.get('department') else ''
            email = str(f.get('email')).strip() if f.get('email') else ''
            
            if not name or not designation:
                continue
            
            # Avoid exact duplicates
            if Faculty.objects.filter(name=name, department=department, is_active=True).exists():
                skipped += 1
            else:
                Faculty.objects.create(name=name, designation=designation, department=department, email=email, created_by=request.user)
                imported += 1
        return JsonResponse({'success': True, 'message': f'Successfully imported {imported} faculty members. {skipped} duplicates skipped.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})
