from django.shortcuts import render, redirect
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from apps.accounts.utils import get_user_permissions
from apps.rooms.models import Room
from apps.faculty.models import Faculty
from apps.duty.models import DutySession

class LandingView(TemplateView):
    template_name = 'core/landing.html'

    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            return redirect('core:dashboard')
        return super().get(request, *args, **kwargs)

@login_required
def dashboard_view(request):
    permissions = get_user_permissions(request.user)
    
    room_count = Room.objects.filter(is_active=True).count()
    faculty_count = Faculty.objects.filter(is_active=True).count()
    session_count = DutySession.objects.filter(created_by=request.user).count()

    context = {
        'permissions': permissions,
        'room_count': room_count,
        'faculty_count': faculty_count,
        'session_count': session_count,
    }
    return render(request, 'core/dashboard.html', context)
