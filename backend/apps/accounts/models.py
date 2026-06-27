from __future__ import annotations

from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPER_ADMIN = "super_admin", "Super Admin"
        TEACHER = "teacher", "Teacher"
        STUDENT = "student", "Student"

    email = models.EmailField(unique=True)
    role = models.CharField(max_length=32, choices=Role.choices, default=Role.STUDENT)
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    phone = models.CharField(max_length=32, blank=True)
    faculty = models.ForeignKey("courses.Faculty", related_name="students", on_delete=models.SET_NULL, blank=True, null=True)
    direction = models.ForeignKey("courses.EducationDirection", related_name="students", on_delete=models.SET_NULL, blank=True, null=True)
    academic_group = models.ForeignKey("courses.AcademicGroup", related_name="students", on_delete=models.SET_NULL, blank=True, null=True)
    current_semester = models.ForeignKey("courses.Semester", related_name="students", on_delete=models.SET_NULL, blank=True, null=True)

    REQUIRED_FIELDS = ["email", "first_name", "last_name"]

    class Meta:
        ordering = ["id"]

    @property
    def is_super_admin(self) -> bool:
        return self.role == self.Role.SUPER_ADMIN or self.is_superuser

    @property
    def is_teacher(self) -> bool:
        return self.role == self.Role.TEACHER

    @property
    def is_student(self) -> bool:
        return self.role == self.Role.STUDENT
