from django.urls import path
from . import views

app_name = 'college_settings'

urlpatterns = [
    path('', views.settings_index, name='index'),
    path('fragments/departments/', views.fragment_departments, name='frag_departments'),
    path('fragments/programs/', views.fragment_programs, name='frag_programs'),
    path('fragments/specialisations/', views.fragment_specialisations, name='frag_specialisations'),
    path('fragments/courses/', views.fragment_courses, name='frag_courses'),
    path('fragments/sections/', views.fragment_sections, name='frag_sections'),
    path('fragments/exam-types/', views.fragment_exam_types, name='frag_exam_types'),
    path('api/programs-by-department/', views.api_programs_by_department, name='api_programs_by_dept'),
    path('api/reference/', views.api_settings_reference, name='api_reference'),
    path('departments/add/', views.department_add, name='department_add'),
    path('departments/<int:pk>/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    path('programs/add/', views.program_add, name='program_add'),
    path('programs/<int:pk>/', views.program_edit, name='program_edit'),
    path('programs/<int:pk>/delete/', views.program_delete, name='program_delete'),
    path('specialisations/add/', views.specialisation_add, name='specialisation_add'),
    path('specialisations/<int:pk>/', views.specialisation_edit, name='specialisation_edit'),
    path('specialisations/<int:pk>/delete/', views.specialisation_delete, name='specialisation_delete'),
    path('courses/add/', views.academic_course_add, name='course_add'),
    path('courses/bulk/', views.academic_course_bulk_add, name='course_bulk_add'),
    path('courses/import/', views.course_import_excel, name='courses_import'),
    path('courses/template.xlsx', views.course_template_excel, name='courses_template'),
    path('courses/<int:pk>/', views.academic_course_edit, name='course_edit'),
    path('courses/<int:pk>/delete/', views.academic_course_delete, name='course_delete'),
    path('sections/add/', views.section_add, name='section_add'),
    path('sections/bulk/', views.section_bulk_add, name='section_bulk_add'),
    path('sections/<int:pk>/', views.section_edit, name='section_edit'),
    path('sections/<int:pk>/delete/', views.section_delete, name='section_delete'),
    path('exam-types/add/', views.exam_type_add, name='exam_type_add'),
    path('exam-types/<int:pk>/', views.exam_type_edit, name='exam_type_edit'),
    path('exam-types/<int:pk>/delete/', views.exam_type_delete, name='exam_type_delete'),
]
