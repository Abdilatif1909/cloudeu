from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("lessons", "0001_initial"),
    ]

    operations = [
        migrations.AddIndex("lesson", models.Index(fields=["course", "order"], name="lesson_course_order_idx")),
        migrations.AddIndex("lesson", models.Index(fields=["course", "lesson_number"], name="lesson_course_number_idx")),
    ]
