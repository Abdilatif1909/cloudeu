from django.db import models

from apps.common.models import TimeStampedModel
from apps.lessons.models import Lesson


class Quiz(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, related_name="quizzes", on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True)
    randomize_questions = models.BooleanField(default=False)
    shuffle_answers = models.BooleanField(default=True)
    question_timer_seconds = models.PositiveSmallIntegerField(default=0)
    pass_score = models.PositiveSmallIntegerField(default=70)

    class Meta:
        ordering = ["lesson__course", "lesson__order", "id"]
        verbose_name_plural = "quizzes"

    def __str__(self) -> str:
        return self.title


class Question(TimeStampedModel):
    quiz = models.ForeignKey(Quiz, related_name="questions", on_delete=models.CASCADE)
    question = models.TextField()
    options = models.JSONField()
    correct_answer = models.CharField(max_length=255)
    explanation = models.TextField(blank=True)

    class Meta:
        ordering = ["quiz", "id"]

    def __str__(self) -> str:
        return self.question[:80]
