from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('CEE_Quiz', '0005_question_solution'),
    ]

    operations = [
        migrations.AddField(
            model_name='testresult',
            name='total_correct',
            field=models.IntegerField(default=0),
        ),
        migrations.AddField(
            model_name='testresult',
            name='time_taken_seconds',
            field=models.IntegerField(default=0),
        ),
    ]
