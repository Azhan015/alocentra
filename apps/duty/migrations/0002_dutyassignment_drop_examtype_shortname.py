# Rename AssignmentResult -> DutyAssignment; drop ExamType.short_name

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('duty', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='examtype',
            name='short_name',
        ),
        migrations.RenameModel(old_name='AssignmentResult', new_name='DutyAssignment'),
    ]
