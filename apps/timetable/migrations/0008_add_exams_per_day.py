# Generated migration for exams_per_day field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0007_add_duration_fields'),
    ]

    operations = [
        migrations.AddField(
            model_name='examtimetable',
            name='exams_per_day',
            field=models.IntegerField(
                choices=[(1, '1 exam per day'), (2, '2 exams per day')], 
                default=1
            ),
        ),
    ]
