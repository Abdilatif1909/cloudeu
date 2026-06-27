from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType

from apps.glossary.models import Glossary
from apps.materials.models import LectureMaterial, PracticeMaterial, Resource
from apps.videos.models import VideoLesson

from .models import Bookmark, Certificate, LearningEvent, Notification, PDFReadingProgress, PersonalNote, QuizResult, StudentProgress


BOOKMARK_TARGETS = {
    "lecture": LectureMaterial,
    "video": VideoLesson,
    "practice": PracticeMaterial,
    "resource": Resource,
    "glossary": Glossary,
}


class StudentProgressSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    completion_percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = StudentProgress
        fields = [
            "id",
            "student",
            "student_name",
            "lesson",
            "lesson_title",
            "lecture_viewed",
            "lecture_completed",
            "pdf_downloaded",
            "video_started",
            "video_completed",
            "practice_downloaded",
            "practice_completed",
            "quiz_attempted",
            "quiz_passed",
            "study_seconds",
            "last_activity_at",
            "completed",
            "completion_date",
            "completion_percentage",
        ]
        read_only_fields = ["completion_date"]

    def validate_student(self, value):
        request = self.context["request"]
        if request.user.is_student and value != request.user:
            raise serializers.ValidationError("Students can update only their own progress.")
        return value


class QuizResultSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    quiz_title = serializers.CharField(source="quiz.title", read_only=True)
    percentage = serializers.FloatField(read_only=True)

    class Meta:
        model = QuizResult
        fields = ["id", "student", "student_name", "quiz", "quiz_title", "score", "total", "duration", "percentage", "passed", "attempt_number", "created_at"]
        read_only_fields = ["created_at", "percentage", "passed", "attempt_number"]

    def validate(self, attrs):
        score = attrs.get("score", getattr(self.instance, "score", 0))
        total = attrs.get("total", getattr(self.instance, "total", 0))
        if total <= 0:
            raise serializers.ValidationError({"total": "Total must be greater than zero."})
        if score > total:
            raise serializers.ValidationError({"score": "Score cannot be greater than total."})
        return attrs

    def validate_student(self, value):
        request = self.context["request"]
        if request.user.is_student and value != request.user:
            raise serializers.ValidationError("Students can submit only their own results.")
        return value


class ProgressSummarySerializer(serializers.Serializer):
    total_lessons = serializers.IntegerField()
    completed_lessons = serializers.IntegerField()
    remaining_lessons = serializers.IntegerField()
    completion_percentage = serializers.FloatField()
    quiz_attempts = serializers.IntegerField()
    average_score = serializers.FloatField()
    total_study_seconds = serializers.IntegerField()
    last_visited_lesson = serializers.DictField(allow_null=True)
    current_streak = serializers.IntegerField()
    recently_watched_videos = serializers.ListField()
    recently_downloaded_pdfs = serializers.ListField()
    weekly_activity = serializers.ListField()


class LearningEventSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = LearningEvent
        fields = ["id", "student", "course", "course_title", "lesson", "lesson_title", "event_type", "study_seconds", "metadata", "created_at"]
        read_only_fields = ["student", "created_at"]


class PDFReadingProgressSerializer(serializers.ModelSerializer):
    lecture_title = serializers.CharField(source="lecture.title", read_only=True)

    class Meta:
        model = PDFReadingProgress
        fields = ["id", "student", "lecture", "lecture_title", "current_page", "total_pages", "zoom", "reading_percentage", "completed", "updated_at"]
        read_only_fields = ["student", "reading_percentage", "completed", "updated_at"]


class PersonalNoteSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    lecture_title = serializers.CharField(source="lecture.title", read_only=True)

    class Meta:
        model = PersonalNote
        fields = ["id", "student", "course", "course_title", "lesson", "lesson_title", "lecture", "lecture_title", "title", "content", "created_at", "updated_at"]
        read_only_fields = ["student", "created_at", "updated_at"]


class BookmarkSerializer(serializers.ModelSerializer):
    content_type_label = serializers.CharField(source="content_type.model", read_only=True)
    target_type = serializers.ChoiceField(choices=list(BOOKMARK_TARGETS.keys()), write_only=True, required=False)

    class Meta:
        model = Bookmark
        fields = ["id", "student", "content_type", "content_type_label", "target_type", "object_id", "title", "url", "created_at"]
        read_only_fields = ["student", "created_at"]
        extra_kwargs = {"content_type": {"required": False}}

    def validate(self, attrs):
        target_type = attrs.pop("target_type", None)
        if target_type:
            attrs["content_type"] = ContentType.objects.get_for_model(BOOKMARK_TARGETS[target_type])
        if "content_type" not in attrs and self.instance is None:
            raise serializers.ValidationError({"target_type": "Bookmark target type is required."})
        return attrs


class CertificateSerializer(serializers.ModelSerializer):
    student_name = serializers.CharField(source="student.get_full_name", read_only=True)
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Certificate
        fields = ["id", "student", "student_name", "course", "course_title", "certificate_id", "verification_code", "issued_at"]
        read_only_fields = ["student", "certificate_id", "verification_code", "issued_at"]


class NotificationSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Notification
        fields = ["id", "recipient", "course", "course_title", "lesson", "lesson_title", "notification_type", "title", "message", "url", "is_read", "created_at"]
        read_only_fields = ["created_at"]
