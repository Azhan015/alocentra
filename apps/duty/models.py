from django.db import models
from django.conf import settings
from apps.rooms.models import Room
from apps.faculty.models import Faculty

class ExamType(models.Model):
    name = models.CharField(max_length=100)
    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    exam_program_type = models.CharField(max_length=50, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [['name', 'exam_program_type', 'duration_hours', 'duration_minutes']]

class DutySession(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('FINALIZED', 'Finalized')
    ]
    title = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    timetable = models.ForeignKey('timetable.ExamTimetable', on_delete=models.SET_NULL, null=True, blank=True, related_name='duty_sessions')
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='DRAFT')
    date_from = models.DateField(null=True, blank=True)
    date_to = models.DateField(null=True, blank=True)

    def __str__(self):
        return self.title

class DutySessionRoom(models.Model):
    session = models.ForeignKey(DutySession, on_delete=models.CASCADE, related_name='session_rooms')
    room = models.ForeignKey(Room, on_delete=models.CASCADE)

class FacultyDutyAssignment(models.Model):
    session = models.ForeignKey(DutySession, on_delete=models.CASCADE, related_name='faculty_assignments')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    no_of_duties = models.PositiveIntegerField(default=1)
    is_reliever = models.BooleanField(default=False)
    reliever_room_count = models.PositiveIntegerField(default=5)

class DutyAssignment(models.Model):
    session = models.ForeignKey(DutySession, on_delete=models.CASCADE, related_name='assignments')
    date = models.DateField()
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    is_reliever = models.BooleanField(default=False)
    assigned_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date', 'room']
