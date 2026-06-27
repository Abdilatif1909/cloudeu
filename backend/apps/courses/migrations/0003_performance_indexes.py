from django.db import migrations, models


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0002_university_structure_and_enrollments"),
    ]

    operations = [
        migrations.AddIndex("course", models.Index(fields=["teacher", "is_active", "is_published", "is_archived"], name="course_teacher_state_idx")),
        migrations.AddIndex("course", models.Index(fields=["department", "academic_semester"], name="course_dept_sem_idx")),
        migrations.AddIndex("course", models.Index(fields=["code"], name="course_code_idx")),
        migrations.AddIndex("courseenrollment", models.Index(fields=["student", "status"], name="enroll_student_status_idx")),
        migrations.AddIndex("courseenrollment", models.Index(fields=["course", "status"], name="enroll_course_status_idx")),
        migrations.AddIndex("courseenrollment", models.Index(fields=["group", "status"], name="enroll_group_status_idx")),
    ]
