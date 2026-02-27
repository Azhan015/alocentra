from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import CustomUser, UserPermission, InvitationToken
from .utils import is_token_valid, permission_required_custom, get_user_permissions, generate_token
from apps.notifications.tasks import send_invitation_email
import json

def register_view(request):
    if request.method == 'POST':
        if CustomUser.objects.filter(is_coe=True).exists():
            messages.error(request, "Registration is closed.")
            return redirect('/')
        
        name = request.POST.get('name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return redirect('/')
            
        if CustomUser.objects.filter(email=email).exists():
            messages.error(request, "Email already exists.")
            return redirect('/')

        user = CustomUser.objects.create_user(
            email=email,
            name=name,
            password=password,
            designation='Controller of Examination',
            role='COE',
            is_coe=True,
            is_active=True,
            password_set=True
        )

        UserPermission.objects.create(
            user=user,
            can_view_rooms=True, can_add_rooms=True, can_delete_rooms=True,
            can_view_faculty=True, can_add_faculty=True, can_delete_faculty=True,
            can_view_duty=True, can_assign_duty=True, can_export_duty=True,
            can_view_timetable=True, can_edit_timetable=True,
            can_manage_users=True, can_view_dashboard=True
        )
        login(request, user, backend='axes.backends.AxesBackend')
        messages.success(request, "Registration successful. Welcome to AloCentra!")
        return redirect('core:dashboard')
        
    return redirect('/')

def login_view(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        remember = request.POST.get('remember')

        user = authenticate(request, email=email, password=password)
        if user is not None:
            if not getattr(user, 'is_active', False):
                messages.error(request, "Your account is not active.")
                return redirect('/')
            login(request, user)
            if not remember:
                request.session.set_expiry(0)
            messages.success(request, f"Welcome back, {user.name}!")
            return redirect('core:dashboard')
        else:
            messages.error(request, "Invalid email or password.")
            return redirect('/')
    return redirect('/')

def logout_view(request):
    if request.method == 'POST':
        logout(request)
        messages.success(request, "You have been logged out.")
    return redirect('/')

def set_password_view(request, token):
    token_obj = get_object_or_404(InvitationToken, token=token)
    
    if not is_token_valid(token_obj):
        messages.error(request, "This invitation link is invalid or has expired.")
        return redirect('/')
        
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
        elif len(password) < 8:
            messages.error(request, "Password must be at least 8 characters.")
        else:
            user = token_obj.user
            user.set_password(password)
            user.is_active = True
            user.password_set = True
            user.save()
            
            token_obj.is_used = True
            token_obj.save()
            
            messages.success(request, "Password set successfully. You can now log in.")
            return redirect('/')
            
    return render(request, 'accounts/set_password.html', {'token': token_obj})

@login_required
@permission_required_custom('can_manage_users')
def users_view(request):
    users = CustomUser.objects.all().order_by('-created_at')
    context = {
        'users_list': users,
        'permissions': get_user_permissions(request.user)
    }
    return render(request, 'accounts/users.html', context)

@login_required
@permission_required_custom('can_manage_users')
@require_POST
def add_user(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        name = data.get('name')
        designation = data.get('designation')
        perms = data.get('permissions', {})
        
        if CustomUser.objects.filter(email=email).exists():
            return JsonResponse({'success': False, 'message': 'User with this email already exists'})
            
        user = CustomUser.objects.create_user(
            email=email, name=name, designation=designation,
            role='STAFF', is_active=False, password_set=False,
            invited_by=request.user
        )
        
        UserPermission.objects.create(
            user=user,
            can_view_rooms=perms.get('can_view_rooms', False),
            can_add_rooms=perms.get('can_add_rooms', False),
            can_delete_rooms=perms.get('can_delete_rooms', False),
            can_view_faculty=perms.get('can_view_faculty', False),
            can_add_faculty=perms.get('can_add_faculty', False),
            can_delete_faculty=perms.get('can_delete_faculty', False),
            can_view_duty=perms.get('can_view_duty', False),
            can_assign_duty=perms.get('can_assign_duty', False),
            can_export_duty=perms.get('can_export_duty', False),
            can_view_timetable=perms.get('can_view_timetable', False),
            can_edit_timetable=perms.get('can_edit_timetable', False),
            can_manage_users=perms.get('can_manage_users', False),
            can_view_dashboard=True
        )
        
        token = generate_token()
        InvitationToken.objects.create(user=user, token=token)
        
        send_invitation_email.delay(user.email, user.name, token, request.build_absolute_uri('/'))
        
        return JsonResponse({'success': True, 'message': 'User invited successfully.'})
    except Exception as e:
        return JsonResponse({'success': False, 'message': str(e)})

@login_required
@permission_required_custom('can_manage_users')
@require_POST
def delete_user(request, id):
    user = get_object_or_404(CustomUser, id=id)
    if user.is_coe:
        return JsonResponse({'success': False, 'message': 'Cannot delete COE.'})
    user.delete()
    return JsonResponse({'success': True, 'message': 'User deleted.'})
