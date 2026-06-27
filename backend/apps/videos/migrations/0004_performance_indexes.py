from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("videos", "0003_videowatchprogress_resume_fields"),
    ]

    operations = [
        migrations.AddIndex("videolesson", models.Index(fields=["lesson", "created_at"], name="video_lesson_created_idx")),
        migrations.AddIndex("videolesson", models.Index(fields=["speaker"], name="video_speaker_idx")),
        migrations.AddIndex("videowatchprogress", models.Index(fields=["student", "completed"], name="vprogress_student_done_idx")),
        migrations.AddIndex("videowatchprogress", models.Index(fields=["video", "completed"], name="vprogress_video_done_idx")),
        migrations.AddIndex("videowatchprogress", models.Index(fields=["updated_at"], name="vprogress_updated_idx")),
    ]
