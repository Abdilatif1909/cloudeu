from django.db import models

from apps.common.models import TimeStampedModel


class University(TimeStampedModel):
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32, unique=True)
    address = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "universities"

    def __str__(self) -> str:
        return self.name


class Faculty(TimeStampedModel):
    university = models.ForeignKey(University, related_name="faculties", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["university", "name"]
        constraints = [models.UniqueConstraint(fields=["university", "code"], name="unique_faculty_code_per_university")]
        verbose_name_plural = "faculties"

    def __str__(self) -> str:
        return f"{self.university.code} / {self.name}"


class Department(TimeStampedModel):
    faculty = models.ForeignKey(Faculty, related_name="departments", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["faculty", "name"]
        constraints = [models.UniqueConstraint(fields=["faculty", "code"], name="unique_department_code_per_faculty")]

    def __str__(self) -> str:
        return f"{self.faculty.code} / {self.name}"


class AcademicYear(TimeStampedModel):
    name = models.CharField(max_length=32, unique=True)
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["-starts_on"]

    def __str__(self) -> str:
        return self.name


class Semester(TimeStampedModel):
    academic_year = models.ForeignKey(AcademicYear, related_name="semesters", on_delete=models.CASCADE)
    name = models.CharField(max_length=64)
    number = models.PositiveSmallIntegerField()
    starts_on = models.DateField()
    ends_on = models.DateField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["academic_year", "number"]
        constraints = [models.UniqueConstraint(fields=["academic_year", "number"], name="unique_semester_number_per_year")]

    def __str__(self) -> str:
        return f"{self.academic_year.name} / {self.name}"


class EducationDirection(TimeStampedModel):
    faculty = models.ForeignKey(Faculty, related_name="directions", on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    code = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["faculty", "name"]
        constraints = [models.UniqueConstraint(fields=["faculty", "code"], name="unique_direction_code_per_faculty")]

    def __str__(self) -> str:
        return f"{self.code} - {self.name}"


class AcademicGroup(TimeStampedModel):
    direction = models.ForeignKey(EducationDirection, related_name="groups", on_delete=models.CASCADE)
    semester = models.ForeignKey(Semester, related_name="groups", on_delete=models.PROTECT, blank=True, null=True)
    name = models.CharField(max_length=64)
    code = models.CharField(max_length=32)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["direction", "name"]
        constraints = [models.UniqueConstraint(fields=["direction", "code"], name="unique_group_code_per_direction")]

    def __str__(self) -> str:
        return self.name


class Course(TimeStampedModel):
    title = models.CharField(max_length=255)
    code = models.CharField(max_length=32, unique=True)
    description = models.TextField()
    department = models.ForeignKey(Department, related_name="courses", on_delete=models.PROTECT, blank=True, null=True)
    academic_semester = models.ForeignKey(Semester, related_name="courses", on_delete=models.PROTECT, blank=True, null=True)
    teacher = models.ForeignKey("accounts.User", related_name="teaching_courses", on_delete=models.PROTECT, blank=True, null=True)
    semester = models.PositiveSmallIntegerField()
    credits = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to="courses/", blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_published = models.BooleanField(default=True)
    is_archived = models.BooleanField(default=False)

    class Meta:
        ordering = ["code"]
        indexes = [
            models.Index(fields=["teacher", "is_active", "is_published", "is_archived"], name="course_teacher_state_idx"),
            models.Index(fields=["department", "academic_semester"], name="course_dept_sem_idx"),
            models.Index(fields=["code"], name="course_code_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.code} - {self.title}"


class CourseEnrollment(TimeStampedModel):
    class Status(models.TextChoices):
        ACTIVE = "active", "Active"
        PENDING = "pending", "Pending"
        COMPLETED = "completed", "Completed"
        DROPPED = "dropped", "Dropped"

    student = models.ForeignKey("accounts.User", related_name="course_enrollments", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="enrollments", on_delete=models.CASCADE)
    group = models.ForeignKey(AcademicGroup, related_name="course_enrollments", on_delete=models.SET_NULL, blank=True, null=True)
    status = models.CharField(max_length=16, choices=Status.choices, default=Status.ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["course", "student"]
        indexes = [
            models.Index(fields=["student", "status"], name="enroll_student_status_idx"),
            models.Index(fields=["course", "status"], name="enroll_course_status_idx"),
            models.Index(fields=["group", "status"], name="enroll_group_status_idx"),
        ]
        constraints = [models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_enrollment")]

    def __str__(self) -> str:
        return f"{self.student} -> {self.course}"
