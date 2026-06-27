from django.contrib import admin

from .models import VideoLesson, VideoWatchProgress


@admin.register(VideoLesson)
class VideoLessonAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "speaker", "video_id", "duration")
    list_filter = ("lesson__course",)
    search_fields = ("title", "lesson__title", "speaker", "description", "youtube_url", "video_id")
    readonly_fields = ("video_id", "thumbnail", "created_at", "updated_at")


@admin.register(VideoWatchProgress)
class VideoWatchProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "video", "watched_seconds", "completed", "updated_at")
    list_filter = ("completed", "video__lesson__course")
    search_fields = ("student__username", "student__email", "video__title")
