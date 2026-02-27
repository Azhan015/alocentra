from django.db import models
from django.conf import settings

class Room(models.Model):
    room_no = models.CharField(max_length=20, unique=True)
    capacity = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['room_no']

    def __str__(self):
        return self.room_no
