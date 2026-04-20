from django.db import models
from django.conf import settings
from apps.rooms.models import Room
from apps.faculty.models import Faculty


class ExamType(models.Model):
    name = models.CharField(max_length=100)
    duration_hours = models.PositiveIntegerField(default=0)
    duration_minutes = models.PositiveIntegerField(default=0)
    exam_program_type = models.CharField(max_length=50, blank=True)
    # Default start time for exams of this type (e.g. 09:00 AM)
    default_start_time = models.TimeField(null=True, blank=True)

    def __str__(self):
        return self.name

    class Meta:
        unique_together = [['name', 'exam_program_type', 'duration_hours', 'duration_minutes']]

    @property
    def duration_label(self):
        """Human-readable duration string."""
        parts = []
        if self.duration_hours:
            parts.append(f"{self.duration_hours}h")
        if self.duration_minutes:
            parts.append(f"{self.duration_minutes}m")
        return " ".join(parts) if parts else "—"

    @property
    def default_start_time_display(self):
        """Return formatted start time string, e.g. '09:00 AM'."""
        if self.default_start_time:
            return self.default_start_time.strftime("%I:%M %p")
        return "—"


class DutySession(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('FINALIZED', 'Finalized')
    ]
    title = models.CharField(max_length=200)
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    timetable = models.ForeignKey(
        'timetable.ExamTimetable',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='duty_sessions',
    )
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


class DutyReserve(models.Model):
    """Reserve faculty members for a duty session"""
    session = models.ForeignKey(DutySession, on_delete=models.CASCADE, related_name='reserves')
    faculty = models.ForeignKey(Faculty, on_delete=models.CASCADE)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [['session', 'faculty']]
        ordering = ['added_at']

    def __str__(self):
        return f"{self.faculty.name} - Reserve for {self.session.title}"