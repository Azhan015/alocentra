from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('timetable', '0005_program_type_phd_datafix'),
        ('duty', '0004_alter_dutyassignment_session'),
    ]

    operations = [
        migrations.AddField(
            model_name='dutysession',
            name='timetable',
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name='duty_sessions',
                to='timetable.examtimetable',
            ),
        ),
    ]

