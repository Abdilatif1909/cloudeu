from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.courses.models import Course
from apps.lessons.models import Lesson
from apps.materials.models import LectureMaterial
from apps.quizzes.models import Quiz


class StudentProgress(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="lesson_progress", on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name="student_progress", on_delete=models.CASCADE)
    lecture_viewed = models.BooleanField(default=False)
    lecture_completed = models.BooleanField(default=False)
    pdf_downloaded = models.BooleanField(default=False)
    video_started = models.BooleanField(default=False)
    video_completed = models.BooleanField(default=False)
    practice_downloaded = models.BooleanField(default=False)
    practice_completed = models.BooleanField(default=False)
    quiz_attempted = models.BooleanField(default=False)
    quiz_passed = models.BooleanField(default=False)
    study_seconds = models.PositiveIntegerField(default=0)
    last_activity_at = models.DateTimeField(blank=True, null=True)
    completed = models.BooleanField(default=False)
    completion_date = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["student", "lesson__course", "lesson__order"]
        indexes = [
            models.Index(fields=["student", "completed"], name="sprogress_student_done_idx"),
            models.Index(fields=["lesson", "completed"], name="sprogress_lesson_done_idx"),
            models.Index(fields=["last_activity_at"], name="sprogress_activity_idx"),
        ]
        constraints = [models.UniqueConstraint(fields=["student", "lesson"], name="unique_student_lesson_progress")]

    def save(self, *args, **kwargs):
        checks = [
            self.lecture_viewed,
            self.lecture_completed,
            self.pdf_downloaded,
            self.video_started,
            self.video_completed,
            self.practice_downloaded,
            self.practice_completed,
            self.quiz_attempted,
            self.quiz_passed,
        ]
        self.completed = all(checks)
        if self.completed and self.completion_date is None:
            self.completion_date = timezone.now()
        if not self.completed:
            self.completion_date = None
        super().save(*args, **kwargs)

    @property
    def completion_percentage(self) -> float:
        checks = [
            self.lecture_viewed,
            self.lecture_completed,
            self.pdf_downloaded,
            self.video_started,
            self.video_completed,
            self.practice_downloaded,
            self.practice_completed,
            self.quiz_attempted,
            self.quiz_passed,
        ]
        return round((sum(1 for check in checks if check) / len(checks)) * 100, 2)

    def __str__(self) -> str:
        return f"{self.student} - {self.lesson}"


class QuizResult(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="quiz_results", on_delete=models.CASCADE)
    quiz = models.ForeignKey(Quiz, related_name="results", on_delete=models.CASCADE)
    score = models.PositiveSmallIntegerField()
    total = models.PositiveSmallIntegerField()
    duration = models.DurationField()
    passed = models.BooleanField(default=False)
    attempt_number = models.PositiveSmallIntegerField(default=1)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["student", "quiz"], name="qresult_student_quiz_idx"),
            models.Index(fields=["quiz", "passed"], name="qresult_quiz_passed_idx"),
            models.Index(fields=["created_at"], name="qresult_created_idx"),
        ]

    @property
    def percentage(self) -> float:
        if self.total == 0:
            return 0.0
        return round((self.score / self.total) * 100, 2)

    def save(self, *args, **kwargs):
        self.passed = self.percentage >= self.quiz.pass_score
        if not self.attempt_number:
            self.attempt_number = (
                QuizResult.objects.filter(student=self.student, quiz=self.quiz).count() + 1
            )
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.quiz}: {self.score}/{self.total}"


class LearningEvent(TimeStampedModel):
    class EventType(models.TextChoices):
        LECTURE_VIEWED = "lecture_viewed", "Lecture viewed"
        LECTURE_COMPLETED = "lecture_completed", "Lecture completed"
        PDF_DOWNLOADED = "pdf_downloaded", "PDF downloaded"
        VIDEO_STARTED = "video_started", "Video started"
        VIDEO_COMPLETED = "video_completed", "Video completed"
        PRACTICE_DOWNLOADED = "practice_downloaded", "Practice downloaded"
        PRACTICE_COMPLETED = "practice_completed", "Practice completed"
        QUIZ_ATTEMPTED = "quiz_attempted", "Quiz attempted"
        QUIZ_PASSED = "quiz_passed", "Quiz passed"
        NOTE_UPDATED = "note_updated", "Note updated"

    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="learning_events", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="learning_events", on_delete=models.CASCADE, blank=True, null=True)
    lesson = models.ForeignKey(Lesson, related_name="learning_events", on_delete=models.CASCADE, blank=True, null=True)
    event_type = models.CharField(max_length=32, choices=EventType.choices)
    study_seconds = models.PositiveIntegerField(default=0)
    metadata = models.JSONField(default=dict, blank=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["student", "event_type", "created_at"], name="learning_student_event_idx")]

    def __str__(self) -> str:
        return f"{self.student} - {self.event_type}"


class PDFReadingProgress(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="pdf_progress", on_delete=models.CASCADE)
    lecture = models.ForeignKey(LectureMaterial, related_name="reading_progress", on_delete=models.CASCADE)
    current_page = models.PositiveIntegerField(default=1)
    total_pages = models.PositiveIntegerField(default=0)
    zoom = models.FloatField(default=1.0)
    reading_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)

    class Meta:
        ordering = ["student", "lecture"]
        constraints = [models.UniqueConstraint(fields=["student", "lecture"], name="unique_student_pdf_progress")]

    def save(self, *args, **kwargs):
        if self.total_pages:
            self.reading_percentage = round(min(self.current_page / self.total_pages, 1) * 100, 2)
            self.completed = self.reading_percentage >= 90
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.lecture}"


class PersonalNote(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notes", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="notes", on_delete=models.CASCADE)
    lesson = models.ForeignKey(Lesson, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
    lecture = models.ForeignKey(LectureMaterial, related_name="notes", on_delete=models.CASCADE, blank=True, null=True)
    title = models.CharField(max_length=255, blank=True)
    content = models.TextField(blank=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self) -> str:
        return self.title or f"Note #{self.pk}"


class Bookmark(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="bookmarks", on_delete=models.CASCADE)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey("content_type", "object_id")
    title = models.CharField(max_length=255)
    url = models.CharField(max_length=255, blank=True)

    class Meta:
        ordering = ["-created_at"]
        constraints = [models.UniqueConstraint(fields=["student", "content_type", "object_id"], name="unique_student_bookmark")]

    def __str__(self) -> str:
        return self.title


class Certificate(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="certificates", on_delete=models.CASCADE)
    course = models.ForeignKey(Course, related_name="certificates", on_delete=models.CASCADE)
    certificate_id = models.CharField(max_length=64, unique=True)
    verification_code = models.CharField(max_length=128, unique=True)
    issued_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-issued_at"]
        constraints = [models.UniqueConstraint(fields=["student", "course"], name="unique_student_course_certificate")]

    def __str__(self) -> str:
        return self.certificate_id


class Notification(TimeStampedModel):
    class NotificationType(models.TextChoices):
        LECTURE = "lecture", "New lecture published"
        VIDEO = "video", "New video added"
        QUIZ = "quiz", "Quiz available"
        ASSIGNMENT = "assignment", "Assignment updated"

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="notifications", on_delete=models.CASCADE, blank=True, null=True)
    course = models.ForeignKey(Course, related_name="notifications", on_delete=models.CASCADE, blank=True, null=True)
    lesson = models.ForeignKey(Lesson, related_name="notifications", on_delete=models.CASCADE, blank=True, null=True)
    notification_type = models.CharField(max_length=32, choices=NotificationType.choices)
    title = models.CharField(max_length=255)
    message = models.TextField(blank=True)
    url = models.CharField(max_length=255, blank=True)
    is_read = models.BooleanField(default=False)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self) -> str:
        return self.title
