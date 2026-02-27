from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPermission, InvitationToken

class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['email', 'name', 'role', 'is_coe', 'is_active']
    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {'fields': ('name', 'designation', 'role', 'is_coe', 'password_set', 'invited_by')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {'fields': ('name', 'designation', 'role', 'is_coe', 'password_set', 'invited_by')}),
    )
    ordering = ['email']

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserPermission)
admin.site.register(InvitationToken)
