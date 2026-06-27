from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("materials", "0002_resource_alter_lecturematerial_options_and_more"),
    ]

    operations = [
        migrations.AddIndex("lecturematerial", models.Index(fields=["lesson", "lecture_number", "is_published"], name="lecture_lesson_pub_idx")),
        migrations.AddIndex("lecturematerial", models.Index(fields=["is_published", "created_at"], name="lecture_pub_created_idx")),
        migrations.AddIndex("lecturematerial", models.Index(fields=["download_count"], name="lecture_downloads_idx")),
        migrations.AddIndex("lecturematerial", models.Index(fields=["view_count"], name="lecture_views_idx")),
        migrations.AddIndex("practicematerial", models.Index(fields=["lesson", "difficulty"], name="practice_lesson_diff_idx")),
        migrations.AddIndex("practicematerial", models.Index(fields=["created_at"], name="practice_created_idx")),
        migrations.AddIndex("resource", models.Index(fields=["course", "category", "is_published"], name="resource_course_cat_idx")),
        migrations.AddIndex("resource", models.Index(fields=["lesson", "category", "is_published"], name="resource_lesson_cat_idx")),
        migrations.AddIndex("resource", models.Index(fields=["download_count"], name="resource_downloads_idx")),
    ]
