from django.contrib import admin
from .models import ExamType, DutySession, DutySessionRoom, FacultyDutyAssignment, AssignmentResult

@admin.register(ExamType)
class ExamTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name', 'duration_hours']

@admin.register(DutySession)
class DutySessionAdmin(admin.ModelAdmin):
    list_display = ['title', 'exam_type', 'status', 'date_from', 'date_to', 'created_at']
    list_filter = ['status', 'exam_type']

admin.site.register(DutySessionRoom)
admin.site.register(FacultyDutyAssignment)
admin.site.register(AssignmentResult)
