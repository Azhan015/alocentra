from django.db import migrations, models


def migrate_ph_to_phd(apps, schema_editor):
    Program = apps.get_model('timetable', 'Program')
    Program.objects.filter(program_type='PH').update(program_type='PHD')


def reverse_phd_to_ph(apps, schema_editor):
    Program = apps.get_model('timetable', 'Program')
    Program.objects.filter(program_type='PHD').update(program_type='PH')


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0004_alter_course_options_alter_course_semester'),
    ]

    operations = [
        migrations.RunPython(migrate_ph_to_phd, reverse_phd_to_ph),
        migrations.AlterField(
            model_name='program',
            name='program_type',
            field=models.CharField(
                choices=[('UG', 'UG'), ('PG', 'PG'), ('PHD', 'PHD')],
                default='UG',
                max_length=50,
            ),
        ),
    ]

