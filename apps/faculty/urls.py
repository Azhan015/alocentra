from django.urls import path
from . import views

app_name = 'faculty'

urlpatterns = [
    path('', views.faculty_view, name='faculty'),
    path('add/', views.add_faculty, name='add_faculty'),
    path('<int:id>/edit/', views.edit_faculty, name='edit_faculty'),
    path('<int:id>/delete/', views.delete_faculty, name='delete_faculty'),
    path('bulk-delete/', views.bulk_delete_faculty, name='bulk_delete'),
    path('import/confirm/', views.import_faculty, name='import_confirm'),
]
