from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    dependencies = [
        ("courses", "0002_university_structure_and_enrollments"),
        ("accounts", "0001_initial"),
    ]

    operations = [
        migrations.AddField("user", "faculty", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="courses.faculty")),
        migrations.AddField("user", "direction", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="courses.educationdirection")),
        migrations.AddField("user", "academic_group", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="courses.academicgroup")),
        migrations.AddField("user", "current_semester", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="students", to="courses.semester")),
    ]
