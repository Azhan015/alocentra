from django.urls import path
from . import views

app_name = 'rooms'

urlpatterns = [
    path('', views.rooms_view, name='rooms'),
    path('add/', views.add_room, name='add_room'),
    path('<int:id>/edit/', views.edit_room, name='edit_room'),
    path('<int:id>/delete/', views.delete_room, name='delete_room'),
    path('bulk-delete/', views.bulk_delete_rooms, name='bulk_delete'),
    path('import/confirm/', views.import_rooms, name='import_confirm'),
]
