import uuid
from datetime import timedelta
from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

class CustomUserManager(BaseUserManager):
    def create_user(self, email, name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, name=name, **extra_fields)
        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, email, name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'COE')
        extra_fields.setdefault('is_coe', True)
        return self.create_user(email, name, password, **extra_fields)

class CustomUser(AbstractBaseUser, PermissionsMixin):
    ROLE_CHOICES = [
        ('COE', 'COE'),
        ('STAFF', 'STAFF')
    ]
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    email = models.EmailField(unique=True)
    designation = models.CharField(max_length=200, default='Controller of Examination')
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='STAFF')
    is_coe = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    password_set = models.BooleanField(default=False)
    invited_by = models.ForeignKey('self', null=True, blank=True, on_delete=models.SET_NULL, related_name='invited_users')
    created_at = models.DateTimeField(auto_now_add=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    def __str__(self):
        return self.name

class UserPermission(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='permissions')
    can_view_rooms = models.BooleanField(default=True)
    can_add_rooms = models.BooleanField(default=True)
    can_delete_rooms = models.BooleanField(default=True)
    can_view_faculty = models.BooleanField(default=True)
    can_add_faculty = models.BooleanField(default=True)
    can_delete_faculty = models.BooleanField(default=True)
    can_view_duty = models.BooleanField(default=True)
    can_assign_duty = models.BooleanField(default=True)
    can_export_duty = models.BooleanField(default=True)
    can_view_timetable = models.BooleanField(default=True)
    can_edit_timetable = models.BooleanField(default=True)
    can_manage_users = models.BooleanField(default=False)
    can_view_dashboard = models.BooleanField(default=True)

    def __str__(self):
        return f"Permissions for {self.user.name}"

class InvitationToken(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    token = models.CharField(max_length=64, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=48)
        super().save(*args, **kwargs)
