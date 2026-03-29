from django.urls import path
from . import views

app_name = 'timetable'

urlpatterns = [
    path('', views.timetable_view, name='list'),
    path('builder/', views.timetable_builder, name='builder'),
    path('builder/<int:id>/', views.timetable_builder, name='builder_edit'),
    path('builder/<int:id>/export/excel/', views.timetable_export_excel, name='export_excel'),
    path('builder/<int:id>/export/pdf/', views.timetable_export_pdf, name='export_pdf'),
]
