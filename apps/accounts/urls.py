from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('auth/register/', views.register_view, name='register'),
    path('auth/login/', views.login_view, name='login'),
    path('auth/logout/', views.logout_view, name='logout'),
    path('auth/set-password/<str:token>/', views.set_password_view, name='set_password'),
    path('users/', views.users_view, name='users'),
    path('users/add/', views.add_user, name='add_user'),
    path('users/<str:id>/delete/', views.delete_user, name='delete_user'),
]
