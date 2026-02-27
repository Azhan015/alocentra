from django.contrib import admin
from .models import Department, Course, Subject, ExamTimetable, TimetableCell

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'short_name']

@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'section', 'semester']
    list_filter = ['department']

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'course']
    search_fields = ['name', 'code']

@admin.register(ExamTimetable)
class ExamTimetableAdmin(admin.ModelAdmin):
    list_display = ['exam_type', 'date_from', 'date_to', 'created_at']

admin.site.register(TimetableCell)
