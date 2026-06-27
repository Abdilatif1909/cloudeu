from rest_framework import serializers

from .models import Lesson


class LessonSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)

    class Meta:
        model = Lesson
        fields = ["id", "course", "course_title", "lesson_number", "title", "description", "order"]
