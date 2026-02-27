import secrets
from django.utils import timezone
from .models import CustomUser
from django.core.exceptions import PermissionDenied
from functools import wraps

def generate_token():
    return secrets.token_hex(32)

def is_token_valid(token_obj):
    if token_obj.is_used:
        return False
    if token_obj.expires_at < timezone.now():
        return False
    return True

def coe_registered_processor(request):
    return {'coe_registered': CustomUser.objects.filter(is_coe=True).exists()}

def permission_required_custom(perm_name):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                from django.shortcuts import redirect
                return redirect('login')
            if request.user.is_coe:
                return view_func(request, *args, **kwargs)
            
            if hasattr(request.user, 'permissions'):
                has_perm = getattr(request.user.permissions, perm_name, False)
                if has_perm:
                    return view_func(request, *args, **kwargs)
                    
            from django.http import JsonResponse
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':
                return JsonResponse({"success": False, "message": "You do not have permission to do this."}, status=403)
            raise PermissionDenied
        return _wrapped_view
    return decorator

def get_user_permissions(user):
    if user.is_coe:
        return {
            'can_view_rooms': True,
            'can_add_rooms': True,
            'can_delete_rooms': True,
            'can_view_faculty': True,
            'can_add_faculty': True,
            'can_delete_faculty': True,
            'can_view_duty': True,
            'can_assign_duty': True,
            'can_export_duty': True,
            'can_view_timetable': True,
            'can_edit_timetable': True,
            'can_manage_users': True,
            'can_view_dashboard': True,
        }
    if hasattr(user, 'permissions'):
        p = user.permissions
        return {
            'can_view_rooms': p.can_view_rooms,
            'can_add_rooms': p.can_add_rooms,
            'can_delete_rooms': p.can_delete_rooms,
            'can_view_faculty': p.can_view_faculty,
            'can_add_faculty': p.can_add_faculty,
            'can_delete_faculty': p.can_delete_faculty,
            'can_view_duty': p.can_view_duty,
            'can_assign_duty': p.can_assign_duty,
            'can_export_duty': p.can_export_duty,
            'can_view_timetable': p.can_view_timetable,
            'can_edit_timetable': p.can_edit_timetable,
            'can_manage_users': p.can_manage_users,
            'can_view_dashboard': p.can_view_dashboard,
        }
    return {
        'can_view_rooms': False,
        'can_add_rooms': False,
        'can_delete_rooms': False,
        'can_view_faculty': False,
        'can_add_faculty': False,
        'can_delete_faculty': False,
        'can_view_duty': False,
        'can_assign_duty': False,
        'can_export_duty': False,
        'can_view_timetable': False,
        'can_edit_timetable': False,
        'can_manage_users': False,
        'can_view_dashboard': True,
    }
