from rest_framework import serializers

from .models import VideoLesson, VideoWatchProgress
from .services import YouTubeService


class VideoLessonSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="lesson.course_id", read_only=True)

    class Meta:
        model = VideoLesson
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "course_id",
            "title",
            "youtube_url",
            "video_id",
            "duration",
            "thumbnail",
            "speaker",
            "description",
        ]
        read_only_fields = ["video_id", "thumbnail"]

    def validate_youtube_url(self, value: str) -> str:
        if not YouTubeService.extract_video_id(value):
            raise serializers.ValidationError("A valid YouTube URL is required.")
        return value


class VideoWatchProgressSerializer(serializers.ModelSerializer):
    class Meta:
        model = VideoWatchProgress
        fields = ["id", "student", "video", "watched_seconds", "current_position", "watch_percentage", "completed", "completed_at", "updated_at"]
        read_only_fields = ["student", "watch_percentage", "completed_at", "updated_at"]
