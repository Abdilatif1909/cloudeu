from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("progress", "0002_interactive_learning"),
    ]

    operations = [
        migrations.AddIndex("studentprogress", models.Index(fields=["student", "completed"], name="sprogress_student_done_idx")),
        migrations.AddIndex("studentprogress", models.Index(fields=["lesson", "completed"], name="sprogress_lesson_done_idx")),
        migrations.AddIndex("studentprogress", models.Index(fields=["last_activity_at"], name="sprogress_activity_idx")),
        migrations.AddIndex("quizresult", models.Index(fields=["student", "quiz"], name="qresult_student_quiz_idx")),
        migrations.AddIndex("quizresult", models.Index(fields=["quiz", "passed"], name="qresult_quiz_passed_idx")),
        migrations.AddIndex("quizresult", models.Index(fields=["created_at"], name="qresult_created_idx")),
    ]
