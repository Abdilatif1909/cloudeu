from django.conf import settings
from django.core.validators import URLValidator
from django.db import models
from django.utils import timezone

from apps.common.models import TimeStampedModel
from apps.lessons.models import Lesson

from .services import YouTubeService


class VideoLesson(TimeStampedModel):
    lesson = models.ForeignKey(Lesson, related_name="videos", on_delete=models.CASCADE)
    title = models.CharField(max_length=255, default="Untitled video")
    youtube_url = models.URLField(validators=[URLValidator(schemes=["http", "https"])])
    video_id = models.CharField(max_length=32, default="", editable=False)
    duration = models.DurationField(help_text="Video duration in HH:MM:SS format.")
    thumbnail = models.URLField(blank=True, default="")
    speaker = models.CharField(max_length=255, blank=True, default="")
    description = models.TextField(blank=True)

    class Meta:
        ordering = ["lesson__course", "lesson__order", "id"]
        indexes = [
            models.Index(fields=["lesson", "created_at"], name="video_lesson_created_idx"),
            models.Index(fields=["speaker"], name="video_speaker_idx"),
        ]

    def save(self, *args, **kwargs):
        self.video_id = YouTubeService.extract_video_id(self.youtube_url)
        if self.video_id and not self.thumbnail:
            self.thumbnail = YouTubeService.thumbnail_url(self.video_id)
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return self.title


class VideoWatchProgress(TimeStampedModel):
    student = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="video_progress", on_delete=models.CASCADE)
    video = models.ForeignKey(VideoLesson, related_name="watch_progress", on_delete=models.CASCADE)
    watched_seconds = models.PositiveIntegerField(default=0)
    current_position = models.PositiveIntegerField(default=0)
    watch_percentage = models.FloatField(default=0.0)
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ["student", "video"]
        indexes = [
            models.Index(fields=["student", "completed"], name="vprogress_student_done_idx"),
            models.Index(fields=["video", "completed"], name="vprogress_video_done_idx"),
            models.Index(fields=["updated_at"], name="vprogress_updated_idx"),
        ]
        constraints = [models.UniqueConstraint(fields=["student", "video"], name="unique_student_video_progress")]

    def save(self, *args, **kwargs):
        total_seconds = int(self.video.duration.total_seconds()) if self.video.duration else 0
        position = max(self.current_position, self.watched_seconds)
        if total_seconds:
            self.watch_percentage = round(min(position / total_seconds, 1) * 100, 2)
        if self.watch_percentage >= 90:
            self.completed = True
        if self.completed and self.completed_at is None:
            self.completed_at = timezone.now()
        if not self.completed:
            self.completed_at = None
        super().save(*args, **kwargs)

    def __str__(self) -> str:
        return f"{self.student} - {self.video}"
