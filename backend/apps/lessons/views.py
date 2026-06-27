import csv

from django.http import HttpResponse
from rest_framework import decorators, response, status, viewsets

from apps.common.models import AuditLog
from apps.common.permissions import IsTeacherOrSuperAdmin, ReadOnlyOrTeacher
from apps.common.services import AuditLogService
from apps.courses.services import CourseCloneService

from .models import Lesson
from .serializers import LessonSerializer


class LessonViewSet(viewsets.ModelViewSet):
    queryset = Lesson.objects.select_related("course").prefetch_related(
        "lecture_materials",
        "practice_materials",
        "videos",
        "resources",
        "quizzes",
    )
    serializer_class = LessonSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["course", "lesson_number"]
    search_fields = ["title", "description", "course__title", "course__code"]
    ordering_fields = ["order", "lesson_number", "created_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(course__teacher=user)
        if not user.is_authenticated or getattr(user, "is_student", False):
            return queryset.filter(course__is_active=True, course__is_published=True, course__is_archived=False)
        return queryset

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def duplicate(self, request, pk=None):
        lesson = self.get_object()
        duplicate = CourseCloneService.duplicate_lesson(lesson)
        return response.Response(LessonSerializer(duplicate, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def reorder(self, request):
        items = request.data.get("items", [])
        if not isinstance(items, list):
            return response.Response({"items": "Expected list of {id, order} objects."}, status=status.HTTP_400_BAD_REQUEST)
        lessons = {lesson.id: lesson for lesson in self.get_queryset().filter(id__in=[item.get("id") for item in items])}
        for item in items:
            lesson = lessons.get(item.get("id"))
            if lesson and "order" in item:
                lesson.order = item["order"]
                lesson.save(update_fields=["order", "updated_at"])
        return response.Response({"updated": len(lessons)})

    @decorators.action(detail=False, methods=["get"], permission_classes=[IsTeacherOrSuperAdmin])
    def export(self, request):
        export_format = request.query_params.get("format", "json")
        queryset = self.get_queryset()
        AuditLogService.record(request, AuditLog.Action.EXPORT, "lessons", metadata={"format": export_format})
        if export_format == "csv":
            http_response = HttpResponse(content_type="text/csv")
            http_response["Content-Disposition"] = 'attachment; filename="lessons.csv"'
            writer = csv.writer(http_response)
            writer.writerow(["course", "lesson_number", "title", "description", "order"])
            for lesson in queryset:
                writer.writerow([lesson.course_id, lesson.lesson_number, lesson.title, lesson.description, lesson.order])
            return http_response
        return response.Response(LessonSerializer(queryset, many=True, context=self.get_serializer_context()).data)
