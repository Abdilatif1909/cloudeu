from django.db import models

from apps.common.models import TimeStampedModel
from apps.courses.models import Course


class Lesson(TimeStampedModel):
    course = models.ForeignKey(Course, related_name="lessons", on_delete=models.CASCADE)
    lesson_number = models.PositiveSmallIntegerField()
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    order = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ["course", "order"]
        indexes = [
            models.Index(fields=["course", "order"], name="lesson_course_order_idx"),
            models.Index(fields=["course", "lesson_number"], name="lesson_course_number_idx"),
        ]
        constraints = [
            models.UniqueConstraint(fields=["course", "lesson_number"], name="unique_lesson_number_per_course"),
            models.UniqueConstraint(fields=["course", "order"], name="unique_lesson_order_per_course"),
        ]

    def __str__(self) -> str:
        return f"{self.course.code} / {self.lesson_number}. {self.title}"
