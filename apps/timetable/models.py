from django.db import models
from django.conf import settings
from apps.duty.models import ExamType

class Department(models.Model):
    name = models.CharField(max_length=150)
    short_name = models.CharField(max_length=20)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name

class Course(models.Model):
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    name = models.CharField(max_length=150)
    section = models.CharField(max_length=20, blank=True)
    semester = models.CharField(max_length=20, blank=True)

    def __str__(self):
        return f"{self.name} - {self.section}" if self.section else self.name

class Subject(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='subjects')
    name = models.CharField(max_length=150)
    code = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.code} - {self.name}" if self.code else self.name

class ExamTimetable(models.Model):
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.exam_type.name} ({self.date_from} to {self.date_to})"

class TimetableCell(models.Model):
    timetable = models.ForeignKey(ExamTimetable, on_delete=models.CASCADE, related_name='cells')
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    date = models.DateField()
    subject = models.ForeignKey(Subject, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [['timetable', 'course', 'date']]
