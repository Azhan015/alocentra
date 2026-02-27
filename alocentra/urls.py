from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('', include('apps.accounts.urls')),
    path('rooms/', include('apps.rooms.urls')),
    path('faculty/', include('apps.faculty.urls')),
    path('duty/', include('apps.duty.urls')),
    path('timetable/', include('apps.timetable.urls')),
    path('notifications/', include('apps.notifications.urls')),
]
