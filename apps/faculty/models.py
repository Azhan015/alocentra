from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
import re

class Faculty(models.Model):
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=100)
    email = models.EmailField(null=True, blank=True)
    department = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name
    
    def clean(self):
        if self.email:
            # Validate email ends with @sfscollege.in
            if not self.email.lower().endswith('@sfscollege.in'):
                raise ValidationError({'email': 'Email must be a valid sfscollege.in address'})
    
    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)
