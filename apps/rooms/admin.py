from django.contrib import admin
from .models import Room

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_no', 'capacity', 'is_active', 'created_at']
    search_fields = ['room_no']
