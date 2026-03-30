# Generated manually for AloCentra academic model restructure.

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


def populate_timetablecell_semester(apps, schema_editor):
    TimetableCell = apps.get_model('timetable', 'TimetableCell')
    Program = apps.get_model('timetable', 'Program')
    for cell in TimetableCell.objects.all():
        try:
            p = Program.objects.get(pk=cell.course_id)
            raw = str(p.semester or '').strip()
            digits = ''.join(c for c in raw if c.isdigit())
            n = int(digits) if digits else 1
            cell.semester = max(1, min(n, 12))
        except Exception:
            cell.semester = 1
        cell.save(update_fields=['semester'])


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RenameModel(old_name='Course', new_name='Program'),
        migrations.AddField(
            model_name='timetablecell',
            name='semester',
            field=models.PositiveSmallIntegerField(default=1),
            preserve_default=False,
        ),
        migrations.RunPython(populate_timetablecell_semester, noop_reverse),
        migrations.RemoveField(model_name='program', name='section'),
        migrations.RemoveField(model_name='program', name='semester'),
        migrations.AddField(
            model_name='program',
            name='total_semesters',
            field=models.PositiveSmallIntegerField(default=6),
        ),
        migrations.AlterField(
            model_name='program',
            name='department',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='programs',
                to='timetable.department',
            ),
        ),
        migrations.CreateModel(
            name='Specialisation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                (
                    'program',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='specialisations',
                        to='timetable.program',
                    ),
                ),
            ],
            options={'unique_together': {('program', 'name')}},
        ),
        migrations.CreateModel(
            name='Section',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('semester', models.PositiveSmallIntegerField()),
                ('name', models.CharField(max_length=20)),
                (
                    'program',
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sections',
                        to='timetable.program',
                    ),
                ),
                (
                    'specialisation',
                    models.ForeignKey(
                        blank=True,
                        null=True,
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name='sections',
                        to='timetable.specialisation',
                    ),
                ),
            ],
            options={'unique_together': {('program', 'specialisation', 'semester', 'name')}},
        ),
        migrations.RenameModel(old_name='Subject', new_name='Course'),
        migrations.RenameField(
            model_name='course',
            old_name='course',
            new_name='program',
        ),
        migrations.AlterField(
            model_name='course',
            name='program',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name='courses',
                to='timetable.program',
            ),
        ),
        migrations.AddField(
            model_name='course',
            name='semester',
            field=models.PositiveSmallIntegerField(default=1),
        ),
        migrations.AddField(
            model_name='course',
            name='specialisation',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name='courses',
                to='timetable.specialisation',
            ),
        ),
        migrations.AlterField(
            model_name='course',
            name='code',
            field=models.CharField(blank=True, max_length=30),
        ),
        migrations.RenameField(
            model_name='timetablecell',
            old_name='course',
            new_name='program',
        ),
        migrations.AlterField(
            model_name='timetablecell',
            name='program',
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                to='timetable.program',
            ),
        ),
        migrations.RenameField(
            model_name='timetablecell',
            old_name='subject',
            new_name='course',
        ),
        migrations.AlterField(
            model_name='timetablecell',
            name='course',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                to='timetable.course',
            ),
        ),
        migrations.AlterUniqueTogether(
            name='timetablecell',
            unique_together={('timetable', 'program', 'semester', 'date')},
        ),
        migrations.RemoveField(model_name='department', name='short_name'),
    ]
