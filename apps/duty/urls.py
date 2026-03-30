from django.urls import path
from . import views

app_name = 'duty'

urlpatterns = [
    path('assign/', views.duty_wizard_start, name='wizard_start'),
    path('assign/timetable/<int:timetable_id>/dates/', views.timetable_dates_api, name='timetable_dates_api'),
    path('assign/step1/', views.duty_wizard_step1, name='wizard_step1'),
    path('assign/step2/', views.duty_wizard_step2, name='wizard_step2'),
    path('assign/step3/', views.duty_wizard_step3, name='wizard_step3'),
    path('results/<int:session_id>/', views.duty_results, name='results'),
    path('history/', views.duty_sessions_list, name='history'),
]
