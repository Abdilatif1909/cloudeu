from rest_framework import decorators, exceptions, permissions, response, viewsets

from apps.common.models import AuditLog
from apps.common.permissions import ReadOnlyOrTeacher
from apps.common.services import AuditLogService
from apps.progress.models import LearningEvent
from apps.progress.services import ProgressService

from .models import VideoLesson, VideoWatchProgress
from .serializers import VideoLessonSerializer, VideoWatchProgressSerializer


class VideoLessonViewSet(viewsets.ModelViewSet):
    queryset = VideoLesson.objects.select_related("lesson", "lesson__course")
    serializer_class = VideoLessonSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["lesson", "lesson__course"]
    search_fields = ["title", "description", "speaker", "lesson__title", "lesson__course__title"]
    ordering_fields = ["duration", "created_at", "lesson__order"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(lesson__course__teacher=user)
        return queryset

    def _validate_teacher_lesson(self, lesson):
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin and lesson.course.teacher_id != user.id:
            raise exceptions.PermissionDenied("Teachers can manage only their own course videos.")

    def perform_create(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data["lesson"])
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "video", instance.pk)

    def perform_update(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data.get("lesson", serializer.instance.lesson))
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "video", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "video", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["get"])
    def related(self, request, pk=None):
        video = self.get_object()
        related = self.get_queryset().filter(lesson__course=video.lesson.course).exclude(pk=video.pk)[:6]
        return response.Response(VideoLessonSerializer(related, many=True, context=self.get_serializer_context()).data)

    @decorators.action(detail=True, methods=["get"], url_path="navigation")
    def navigation(self, request, pk=None):
        video = self.get_object()
        siblings = self.get_queryset().filter(lesson__course=video.lesson.course)
        previous_item = siblings.filter(lesson__order__lt=video.lesson.order).order_by("-lesson__order").first()
        next_item = siblings.filter(lesson__order__gt=video.lesson.order).order_by("lesson__order").first()
        return response.Response(
            {
                "previous": VideoLessonSerializer(previous_item, context=self.get_serializer_context()).data if previous_item else None,
                "next": VideoLessonSerializer(next_item, context=self.get_serializer_context()).data if next_item else None,
            }
        )

    @decorators.action(detail=True, methods=["post"], permission_classes=[permissions.IsAuthenticated], url_path="watch-progress")
    def watch_progress(self, request, pk=None):
        video = self.get_object()
        serializer = VideoWatchProgressSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        progress, _ = VideoWatchProgress.objects.update_or_create(
            student=request.user,
            video=video,
            defaults={
                "watched_seconds": serializer.validated_data["watched_seconds"],
                "current_position": serializer.validated_data.get("current_position", serializer.validated_data["watched_seconds"]),
                "completed": serializer.validated_data.get("completed", False),
            },
        )
        ProgressService.record_event(request.user, video.lesson, LearningEvent.EventType.VIDEO_COMPLETED if progress.completed else LearningEvent.EventType.VIDEO_STARTED)
        return response.Response(VideoWatchProgressSerializer(progress).data)

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="watch-progress")
    def get_watch_progress(self, request, pk=None):
        video = self.get_object()
        progress = VideoWatchProgress.objects.filter(student=request.user, video=video).first()
        if progress is None:
            return response.Response({"current_position": 0, "watch_percentage": 0, "completed": False})
        return response.Response(VideoWatchProgressSerializer(progress).data)
