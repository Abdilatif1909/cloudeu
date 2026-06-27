from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("videos", "0002_videolesson_speaker_videolesson_thumbnail_and_more"),
    ]

    operations = [
        migrations.AddField(
            model_name="videowatchprogress",
            name="completed_at",
            field=models.DateTimeField(blank=True, null=True),
        ),
        migrations.AddField(
            model_name="videowatchprogress",
            name="current_position",
            field=models.PositiveIntegerField(default=0),
        ),
        migrations.AddField(
            model_name="videowatchprogress",
            name="watch_percentage",
            field=models.FloatField(default=0.0),
        ),
    ]
