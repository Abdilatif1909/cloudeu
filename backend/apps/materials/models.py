from django.db import models

from apps.common.models import TimeStampedModel
from apps.lessons.models import Lesson

from .validators import validate_archive_file, validate_pdf_file, validate_resource_file


class LectureMaterial(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, related_name="lecture_materials", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled lecture")
    lecture_number = models.PositiveSmallIntegerField(default=1)
    pdf_file = models.FileField(upload_to="materials/lectures/", validators=[validate_pdf_file])
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="materials/lecture-covers/", blank=True, null=True)
    estimated_reading_time = models.PositiveSmallIntegerField(help_text="Estimated reading time in minutes.", default=0)
    download_count = models.PositiveIntegerField(default=0)
    view_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["lesson__course", "lecture_number"]
        indexes = [
            models.Index(fields=["lesson", "lecture_number", "is_published"], name="lecture_lesson_pub_idx"),
            models.Index(fields=["is_published", "created_at"], name="lecture_pub_created_idx"),
            models.Index(fields=["download_count"], name="lecture_downloads_idx"),
            models.Index(fields=["view_count"], name="lecture_views_idx"),
        ]

    def __str__(self) -> str:
        return f"{self.lecture_number}. {self.title}"


class PracticeMaterial(TimeStampedModel):
    class Difficulty(models.TextChoices):
        EASY = "easy", "Easy"
        MEDIUM = "medium", "Medium"
        HARD = "hard", "Hard"

    lesson = models.ForeignKey(Lesson, related_name="practice_materials", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled practice")
    pdf_file = models.FileField(upload_to="materials/practices/", validators=[validate_pdf_file])
    example_files = models.FileField(upload_to="materials/practice-examples/", validators=[validate_archive_file], blank=True, null=True)
    source_code_files = models.FileField(upload_to="materials/practice-code/", blank=True, null=True)
    description = models.TextField(blank=True)
    difficulty = models.CharField(max_length=16, choices=Difficulty.choices, default=Difficulty.MEDIUM)
    estimated_time = models.PositiveSmallIntegerField(help_text="Estimated completion time in minutes.", default=0)

    class Meta:
        ordering = ["lesson__course", "lesson__order", "id"]
        indexes = [
            models.Index(fields=["lesson", "difficulty"], name="practice_lesson_diff_idx"),
            models.Index(fields=["created_at"], name="practice_created_idx"),
        ]

    def __str__(self) -> str:
        return self.title


class Resource(TimeStampedModel):
    class Category(models.TextChoices):
        BOOKS = "books", "Books"
        ARTICLES = "articles", "Articles"
        DATASETS = "datasets", "Datasets"
        CODE = "code", "Code"
        PRESENTATION = "presentation", "Presentation"
        ASSIGNMENT = "assignment", "Assignment"
        OTHER = "other", "Other"

    course = models.ForeignKey("courses.Course", related_name="resources", on_delete=models.CASCADE, blank=True, null=True)
    lesson = models.ForeignKey(Lesson, related_name="resources", on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=32, choices=Category.choices, default=Category.OTHER)
    file = models.FileField(upload_to="resources/", validators=[validate_resource_file])
    download_count = models.PositiveIntegerField(default=0)
    is_published = models.BooleanField(default=True)

    class Meta:
        ordering = ["category", "title"]
        indexes = [
            models.Index(fields=["course", "category", "is_published"], name="resource_course_cat_idx"),
            models.Index(fields=["lesson", "category", "is_published"], name="resource_lesson_cat_idx"),
            models.Index(fields=["download_count"], name="resource_downloads_idx"),
        ]

    def __str__(self) -> str:
        return self.title
