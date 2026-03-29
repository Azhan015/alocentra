from django.contrib import admin
from .models import (
    Department,
    Program,
    Specialisation,
    Section,
    Course,
    ExamTimetable,
    TimetableCell,
)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name']


@admin.register(Program)
class ProgramAdmin(admin.ModelAdmin):
    list_display = ['name', 'department', 'total_semesters']


@admin.register(Specialisation)
class SpecialisationAdmin(admin.ModelAdmin):
    list_display = ['name', 'program']


@admin.register(Section)
class SectionAdmin(admin.ModelAdmin):
    list_display = ['program', 'specialisation', 'semester', 'name']


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'program', 'semester', 'specialisation']


@admin.register(ExamTimetable)
class ExamTimetableAdmin(admin.ModelAdmin):
    list_display = ['exam_type', 'date_from', 'date_to', 'created_at']


@admin.register(TimetableCell)
class TimetableCellAdmin(admin.ModelAdmin):
    list_display = ['timetable', 'program', 'semester', 'date', 'course']
