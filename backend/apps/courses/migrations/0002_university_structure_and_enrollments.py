from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("courses", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="University",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=32, unique=True)),
                ("address", models.TextField(blank=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["name"], "verbose_name_plural": "universities"},
        ),
        migrations.CreateModel(
            name="AcademicYear",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=32, unique=True)),
                ("starts_on", models.DateField()),
                ("ends_on", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ["-starts_on"]},
        ),
        migrations.CreateModel(
            name="Faculty",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=32)),
                ("is_active", models.BooleanField(default=True)),
                ("university", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="faculties", to="courses.university")),
            ],
            options={"ordering": ["university", "name"], "verbose_name_plural": "faculties"},
        ),
        migrations.CreateModel(
            name="Semester",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=64)),
                ("number", models.PositiveSmallIntegerField()),
                ("starts_on", models.DateField()),
                ("ends_on", models.DateField()),
                ("is_active", models.BooleanField(default=True)),
                ("academic_year", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="semesters", to="courses.academicyear")),
            ],
            options={"ordering": ["academic_year", "number"]},
        ),
        migrations.CreateModel(
            name="Department",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=32)),
                ("is_active", models.BooleanField(default=True)),
                ("faculty", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="departments", to="courses.faculty")),
            ],
            options={"ordering": ["faculty", "name"]},
        ),
        migrations.CreateModel(
            name="EducationDirection",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=255)),
                ("code", models.CharField(max_length=32)),
                ("is_active", models.BooleanField(default=True)),
                ("faculty", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="directions", to="courses.faculty")),
            ],
            options={"ordering": ["faculty", "name"]},
        ),
        migrations.CreateModel(
            name="AcademicGroup",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("name", models.CharField(max_length=64)),
                ("code", models.CharField(max_length=32)),
                ("is_active", models.BooleanField(default=True)),
                ("direction", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="groups", to="courses.educationdirection")),
                ("semester", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="groups", to="courses.semester")),
            ],
            options={"ordering": ["direction", "name"]},
        ),
        migrations.AddField("course", "department", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="courses", to="courses.department")),
        migrations.AddField("course", "academic_semester", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="courses", to="courses.semester")),
        migrations.AddField("course", "teacher", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, related_name="teaching_courses", to=settings.AUTH_USER_MODEL)),
        migrations.AddField("course", "is_archived", models.BooleanField(default=False)),
        migrations.AddField("course", "is_published", models.BooleanField(default=True)),
        migrations.CreateModel(
            name="CourseEnrollment",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                ("status", models.CharField(choices=[("active", "Active"), ("pending", "Pending"), ("completed", "Completed"), ("dropped", "Dropped")], default="active", max_length=16)),
                ("enrolled_at", models.DateTimeField(auto_now_add=True)),
                ("course", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="enrollments", to="courses.course")),
                ("group", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="course_enrollments", to="courses.academicgroup")),
                ("student", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="course_enrollments", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ["course", "student"]},
        ),
        migrations.AddConstraint("faculty", models.UniqueConstraint(fields=("university", "code"), name="unique_faculty_code_per_university")),
        migrations.AddConstraint("semester", models.UniqueConstraint(fields=("academic_year", "number"), name="unique_semester_number_per_year")),
        migrations.AddConstraint("department", models.UniqueConstraint(fields=("faculty", "code"), name="unique_department_code_per_faculty")),
        migrations.AddConstraint("educationdirection", models.UniqueConstraint(fields=("faculty", "code"), name="unique_direction_code_per_faculty")),
        migrations.AddConstraint("academicgroup", models.UniqueConstraint(fields=("direction", "code"), name="unique_group_code_per_direction")),
        migrations.AddConstraint("courseenrollment", models.UniqueConstraint(fields=("student", "course"), name="unique_student_course_enrollment")),
    ]
