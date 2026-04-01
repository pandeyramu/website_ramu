from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("CEE_Quiz", "0004_chapter_has_subchapters_subchapter_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="question",
            name="solution",
            field=models.TextField(blank=True, default=""),
        ),
    ]
