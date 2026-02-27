from django.contrib import admin
from .models import Faculty

@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    list_display = ['name', 'designation', 'department', 'is_active']
    search_fields = ['name', 'email', 'department']
    list_filter = ['department', 'is_active']
