from django.db import models
from django.conf import settings
from apps.duty.models import ExamType


class Department(models.Model):
    name = models.CharField(max_length=150)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Program(models.Model):
    PROGRAM_TYPE_CHOICES = [
        ('UG', 'UG'),
        ('PG', 'PG'),
        ('PHD', 'PHD'),
    ]
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='programs')
    name = models.CharField(max_length=150)
    program_type = models.CharField(max_length=50, choices=PROGRAM_TYPE_CHOICES, default='UG')
    total_semesters = models.PositiveSmallIntegerField(default=6)

    def __str__(self):
        return self.name


class Specialisation(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='specialisations')
    name = models.CharField(max_length=100)

    class Meta:
        unique_together = [['program', 'name']]

    def __str__(self):
        return f'{self.program.name} - {self.name}'


class Section(models.Model):
    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='sections')
    specialisation = models.ForeignKey(
        Specialisation, on_delete=models.CASCADE, null=True, blank=True, related_name='sections'
    )
    semester = models.PositiveSmallIntegerField()
    name = models.CharField(max_length=20)

    class Meta:
        unique_together = [['program', 'specialisation', 'semester', 'name']]

    def __str__(self):
        spec = f' {self.specialisation.name}' if self.specialisation else ''
        return f'{self.program.name}{spec} Sem{self.semester} Sec {self.name}'


class Course(models.Model):
    """Academic course unit (subject) mapped to a program/semester, optionally scoped to a specialisation."""

    COURSE_TYPE_CHOICES = [
        ('core', 'Core'),
        ('lab', 'Lab'),
        ('sec', 'SEC'),
        ('oe', 'OE'),
        ('aecc', 'AECC'),
    ]

    program = models.ForeignKey(Program, on_delete=models.CASCADE, related_name='courses')
    semester = models.PositiveSmallIntegerField()
    course_type = models.CharField(max_length=10, choices=COURSE_TYPE_CHOICES, default='core')
    code = models.CharField(max_length=30, blank=True)
    name = models.CharField(max_length=150)
    specialisation = models.ForeignKey(
        Specialisation, on_delete=models.CASCADE, null=True, blank=True, related_name='courses'
    )

    class Meta:
        ordering = ['program_id', 'semester', 'code']

    def __str__(self):
        return f'{self.code} — {self.name}'


class ExamTimetable(models.Model):
    exam_type = models.ForeignKey(ExamType, on_delete=models.PROTECT)
    date_from = models.DateField()
    date_to = models.DateField()
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.exam_type.name} ({self.date_from} to {self.date_to})'


class TimetableCell(models.Model):
    timetable = models.ForeignKey(ExamTimetable, on_delete=models.CASCADE, related_name='cells')
    program = models.ForeignKey(Program, on_delete=models.CASCADE)
    semester = models.PositiveSmallIntegerField()
    date = models.DateField()
    course = models.ForeignKey(Course, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        unique_together = [['timetable', 'program', 'semester', 'date']]
