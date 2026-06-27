from rest_framework import serializers

from .models import LectureMaterial, PracticeMaterial, Resource


class LectureMaterialSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="lesson.course_id", read_only=True)

    class Meta:
        model = LectureMaterial
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "course_id",
            "title",
            "lecture_number",
            "pdf_file",
            "description",
            "cover_image",
            "estimated_reading_time",
            "download_count",
            "view_count",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["download_count", "view_count", "created_at", "updated_at"]


class PracticeMaterialSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    course_id = serializers.IntegerField(source="lesson.course_id", read_only=True)

    class Meta:
        model = PracticeMaterial
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "course_id",
            "title",
            "pdf_file",
            "example_files",
            "source_code_files",
            "description",
            "difficulty",
            "estimated_time",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class ResourceSerializer(serializers.ModelSerializer):
    course_title = serializers.CharField(source="course.title", read_only=True)
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)

    class Meta:
        model = Resource
        fields = [
            "id",
            "course",
            "course_title",
            "lesson",
            "lesson_title",
            "title",
            "description",
            "category",
            "file",
            "download_count",
            "is_published",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["download_count", "created_at", "updated_at"]
