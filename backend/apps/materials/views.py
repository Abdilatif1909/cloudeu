from io import BytesIO
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile

from django.db.models import F
from django.http import FileResponse
from rest_framework import decorators, exceptions, response, viewsets

from apps.common.models import AuditLog
from apps.common.permissions import ReadOnlyOrTeacher
from apps.common.services import AuditLogService
from apps.progress.models import LearningEvent
from apps.progress.services import ProgressService

from .models import LectureMaterial, PracticeMaterial, Resource
from .serializers import LectureMaterialSerializer, PracticeMaterialSerializer, ResourceSerializer


class LectureMaterialViewSet(viewsets.ModelViewSet):
    queryset = LectureMaterial.objects.select_related("lesson", "lesson__course")
    serializer_class = LectureMaterialSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["lesson", "lesson__course", "is_published", "lecture_number"]
    search_fields = ["title", "description", "lesson__title", "lesson__course__title", "lesson__course__code"]
    ordering_fields = ["lecture_number", "created_at", "updated_at", "view_count", "download_count"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(lesson__course__teacher=user)
        if not (user.is_authenticated and (getattr(user, "is_teacher", False) or getattr(user, "is_super_admin", False))):
            queryset = queryset.filter(is_published=True)
        return queryset

    def _validate_teacher_lesson(self, lesson):
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin and lesson.course.teacher_id != user.id:
            raise exceptions.PermissionDenied("Teachers can manage only their own course content.")

    def perform_create(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data["lesson"])
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "lecture", instance.pk)

    def perform_update(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data.get("lesson", serializer.instance.lesson))
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "lecture", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "lecture", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["get"])
    def preview(self, request, pk=None):
        lecture = self.get_object()
        LectureMaterial.objects.filter(pk=lecture.pk).update(view_count=F("view_count") + 1)
        ProgressService.record_event(request.user, lecture.lesson, LearningEvent.EventType.LECTURE_VIEWED, metadata={"id": lecture.id, "title": lecture.title})
        return FileResponse(lecture.pdf_file.open("rb"), content_type="application/pdf")

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        lecture = self.get_object()
        LectureMaterial.objects.filter(pk=lecture.pk).update(download_count=F("download_count") + 1)
        ProgressService.record_event(request.user, lecture.lesson, LearningEvent.EventType.PDF_DOWNLOADED, metadata={"id": lecture.id, "title": lecture.title})
        return FileResponse(lecture.pdf_file.open("rb"), as_attachment=True, filename=lecture.pdf_file.name.split("/")[-1])

    @decorators.action(detail=True, methods=["get"], url_path="navigation")
    def navigation(self, request, pk=None):
        lecture = self.get_object()
        siblings = LectureMaterial.objects.filter(lesson__course=lecture.lesson.course, is_published=True)
        previous_item = siblings.filter(lecture_number__lt=lecture.lecture_number).order_by("-lecture_number").first()
        next_item = siblings.filter(lecture_number__gt=lecture.lecture_number).order_by("lecture_number").first()
        return response.Response(
            {
                "previous": LectureMaterialSerializer(previous_item, context=self.get_serializer_context()).data if previous_item else None,
                "next": LectureMaterialSerializer(next_item, context=self.get_serializer_context()).data if next_item else None,
            }
        )


class PracticeMaterialViewSet(viewsets.ModelViewSet):
    queryset = PracticeMaterial.objects.select_related("lesson", "lesson__course")
    serializer_class = PracticeMaterialSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["lesson", "lesson__course", "difficulty"]
    search_fields = ["title", "description", "lesson__title", "lesson__course__title", "lesson__course__code"]
    ordering_fields = ["created_at", "updated_at", "estimated_time", "lesson__order"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(lesson__course__teacher=user)
        return queryset

    def _validate_teacher_lesson(self, lesson):
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin and lesson.course.teacher_id != user.id:
            raise exceptions.PermissionDenied("Teachers can manage only their own course content.")

    def perform_create(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data["lesson"])
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "practice", instance.pk)

    def perform_update(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data.get("lesson", serializer.instance.lesson))
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "practice", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "practice", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["get"])
    def files(self, request, pk=None):
        practice = self.get_object()
        data = {
            "pdf_file": request.build_absolute_uri(practice.pdf_file.url) if practice.pdf_file else None,
            "example_files": request.build_absolute_uri(practice.example_files.url) if practice.example_files else None,
            "source_code_files": request.build_absolute_uri(practice.source_code_files.url) if practice.source_code_files else None,
        }
        return response.Response(data)

    @decorators.action(detail=True, methods=["get"], url_path="download-all")
    def download_all(self, request, pk=None):
        practice = self.get_object()
        ProgressService.record_event(request.user, practice.lesson, LearningEvent.EventType.PRACTICE_DOWNLOADED, metadata={"id": practice.id, "title": practice.title})
        files = [
            ("practice-pdf", practice.pdf_file),
            ("example-files", practice.example_files),
            ("source-code-files", practice.source_code_files),
        ]
        archive = BytesIO()
        with ZipFile(archive, "w", ZIP_DEFLATED) as zip_file:
            for prefix, file_field in files:
                if not file_field:
                    continue
                filename = Path(file_field.name).name
                with file_field.open("rb") as opened_file:
                    zip_file.writestr(f"{prefix}/{filename}", opened_file.read())
        archive.seek(0)
        filename = f"practice-{practice.pk}-files.zip"
        return FileResponse(archive, as_attachment=True, filename=filename, content_type="application/zip")


class ResourceViewSet(viewsets.ModelViewSet):
    queryset = Resource.objects.select_related("course", "lesson")
    serializer_class = ResourceSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["course", "lesson", "category", "is_published"]
    search_fields = ["title", "description", "course__title", "lesson__title"]
    ordering_fields = ["title", "category", "created_at", "download_count"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(course__teacher=user) | queryset.filter(lesson__course__teacher=user)
        if not (user.is_authenticated and (getattr(user, "is_teacher", False) or getattr(user, "is_super_admin", False))):
            queryset = queryset.filter(is_published=True)
        return queryset

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "resource", instance.pk)

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "resource", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "resource", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["get"])
    def download(self, request, pk=None):
        resource = self.get_object()
        Resource.objects.filter(pk=resource.pk).update(download_count=F("download_count") + 1)
        return FileResponse(resource.file.open("rb"), as_attachment=True, filename=resource.file.name.split("/")[-1])
