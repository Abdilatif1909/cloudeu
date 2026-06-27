from rest_framework import serializers

from apps.materials.serializers import LectureMaterialSerializer, PracticeMaterialSerializer, ResourceSerializer
from apps.videos.serializers import VideoLessonSerializer

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    lecture_materials = LectureMaterialSerializer(many=True, read_only=True)
    practice_materials = PracticeMaterialSerializer(many=True, read_only=True)
    videos = VideoLessonSerializer(many=True, read_only=True)
    resources = ResourceSerializer(many=True, read_only=True)
    quizzes = serializers.SerializerMethodField()

    def get_quizzes(self, obj):
        return [
            {
                "id": quiz.id,
                "lesson": quiz.lesson_id,
                "lesson_title": obj.title,
                "title": quiz.title,
                "description": quiz.description,
                "is_active": quiz.is_active,
                "question_timer_seconds": quiz.question_timer_seconds,
                "pass_score": quiz.pass_score,
            }
            for quiz in obj.quizzes.filter(is_active=True)
        ]

    class Meta:
        model = Lesson
        fields = [
            "id",
            "course",
            "course_title",
            "lesson_number",
            "title",
            "description",
            "order",
            "lecture_materials",
            "practice_materials",
            "videos",
            "resources",
            "quizzes",
        ]
