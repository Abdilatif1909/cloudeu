from django.http import HttpResponse
from drf_spectacular.utils import extend_schema
from rest_framework import decorators, permissions, response, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.common.permissions import IsOwnerTeacherOrSuperAdmin, IsTeacherOrSuperAdmin
from apps.courses.models import Course

from .models import Bookmark, Certificate, LearningEvent, Notification, PDFReadingProgress, PersonalNote, QuizResult, StudentProgress
from .serializers import (
    BookmarkSerializer,
    CertificateSerializer,
    LearningEventSerializer,
    NotificationSerializer,
    PDFReadingProgressSerializer,
    PersonalNoteSerializer,
    ProgressSummarySerializer,
    QuizResultSerializer,
    StudentProgressSerializer,
)
from .services import CertificateService, ProgressService


class StudentProgressViewSet(viewsets.ModelViewSet):
    serializer_class = StudentProgressSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerTeacherOrSuperAdmin]
    filterset_fields = ["student", "lesson", "lesson__course", "completed"]
    search_fields = ["lesson__title", "lesson__course__title", "student__username", "student__email"]
    ordering_fields = ["completion_date", "created_at", "lesson__order"]

    def get_queryset(self):
        queryset = StudentProgress.objects.select_related("student", "lesson", "lesson__course")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset


class QuizResultViewSet(viewsets.ModelViewSet):
    serializer_class = QuizResultSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerTeacherOrSuperAdmin]
    filterset_fields = ["student", "quiz", "quiz__lesson", "quiz__lesson__course"]
    search_fields = ["quiz__title", "student__username", "student__email"]
    ordering_fields = ["created_at", "score", "total", "duration"]

    def get_queryset(self):
        queryset = QuizResult.objects.select_related("student", "quiz", "quiz__lesson", "quiz__lesson__course")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    def perform_create(self, serializer):
        result = serializer.save()
        ProgressService.record_event(result.student, result.quiz.lesson, LearningEvent.EventType.QUIZ_ATTEMPTED)
        if result.passed:
            ProgressService.record_event(result.student, result.quiz.lesson, LearningEvent.EventType.QUIZ_PASSED)


class ProgressSummaryView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=ProgressSummarySerializer)
    def get(self, request):
        course_id = request.query_params.get("course")
        summary = ProgressService.build_summary(request.user, int(course_id) if course_id else None)
        serializer = ProgressSummarySerializer(summary)
        return Response(serializer.data)


class LearningEventViewSet(viewsets.ModelViewSet):
    serializer_class = LearningEventSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "lesson", "event_type"]
    ordering_fields = ["created_at", "study_seconds"]

    def get_queryset(self):
        queryset = LearningEvent.objects.select_related("student", "course", "lesson")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        event = ProgressService.record_event(
            request.user,
            serializer.validated_data.get("lesson"),
            serializer.validated_data["event_type"],
            serializer.validated_data.get("study_seconds", 0),
            serializer.validated_data.get("metadata", {}),
        )
        return response.Response(self.get_serializer(event).data, status=status.HTTP_201_CREATED)


class PDFReadingProgressViewSet(viewsets.ModelViewSet):
    serializer_class = PDFReadingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["lecture", "lecture__lesson", "lecture__lesson__course", "completed"]

    def get_queryset(self):
        queryset = PDFReadingProgress.objects.select_related("student", "lecture", "lecture__lesson")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    def perform_create(self, serializer):
        progress = serializer.save(student=self.request.user)
        event = LearningEvent.EventType.LECTURE_COMPLETED if progress.completed else LearningEvent.EventType.LECTURE_VIEWED
        ProgressService.record_event(self.request.user, progress.lecture.lesson, event)

    def perform_update(self, serializer):
        progress = serializer.save()
        event = LearningEvent.EventType.LECTURE_COMPLETED if progress.completed else LearningEvent.EventType.LECTURE_VIEWED
        ProgressService.record_event(self.request.user, progress.lecture.lesson, event)


class PersonalNoteViewSet(viewsets.ModelViewSet):
    serializer_class = PersonalNoteSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "lesson", "lecture"]
    search_fields = ["title", "content", "course__title", "lesson__title", "lecture__title"]
    ordering_fields = ["created_at", "updated_at", "title"]

    def get_queryset(self):
        queryset = PersonalNote.objects.select_related("student", "course", "lesson", "lecture")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    def perform_create(self, serializer):
        note = serializer.save(student=self.request.user)
        ProgressService.record_event(self.request.user, note.lesson, LearningEvent.EventType.NOTE_UPDATED)

    def perform_update(self, serializer):
        note = serializer.save()
        ProgressService.record_event(self.request.user, note.lesson, LearningEvent.EventType.NOTE_UPDATED)

    @decorators.action(detail=True, methods=["get"], url_path="export-pdf")
    def export_pdf(self, request, pk=None):
        note = self.get_object()
        text = f"{note.title or 'Personal note'}\n\n{note.content}"
        pdf = CertificateService.render_pdf_text("Personal Note", text)
        response_obj = HttpResponse(pdf, content_type="application/pdf")
        response_obj["Content-Disposition"] = f'attachment; filename="note-{note.pk}.pdf"'
        return response_obj


class BookmarkViewSet(viewsets.ModelViewSet):
    serializer_class = BookmarkSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["content_type", "object_id"]
    search_fields = ["title", "url"]
    ordering_fields = ["created_at", "title"]

    def get_queryset(self):
        queryset = Bookmark.objects.select_related("student", "content_type")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    def perform_create(self, serializer):
        serializer.save(student=self.request.user)


class CertificateViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CertificateSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "student", "certificate_id"]

    def get_queryset(self):
        queryset = Certificate.objects.select_related("student", "course")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(student=self.request.user)
        return queryset

    @decorators.action(detail=False, methods=["post"], url_path="issue")
    def issue(self, request):
        course_id = request.data.get("course")
        course = Course.objects.filter(pk=course_id).first()
        if course is None:
            return response.Response({"course": "Course does not exist."}, status=status.HTTP_400_BAD_REQUEST)
        try:
            certificate = CertificateService.issue(request.user, course)
        except ValueError as exc:
            return response.Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return response.Response(CertificateSerializer(certificate, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=True, methods=["get"], url_path="download")
    def download(self, request, pk=None):
        certificate = self.get_object()
        pdf = CertificateService.render_pdf(certificate)
        response_obj = HttpResponse(pdf, content_type="application/pdf")
        response_obj["Content-Disposition"] = f'attachment; filename="{certificate.certificate_id}.pdf"'
        return response_obj


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["course", "lesson", "notification_type", "is_read"]
    search_fields = ["title", "message"]
    ordering_fields = ["created_at", "is_read"]

    def get_queryset(self):
        queryset = Notification.objects.select_related("recipient", "course", "lesson")
        if getattr(self, "swagger_fake_view", False):
            return queryset.none()
        if getattr(self.request.user, "is_student", False):
            return queryset.filter(recipient__isnull=True) | queryset.filter(recipient=self.request.user)
        return queryset

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy"}:
            return [IsTeacherOrSuperAdmin()]
        return super().get_permissions()

    @decorators.action(detail=True, methods=["post"], url_path="mark-read")
    def mark_read(self, request, pk=None):
        notification = self.get_object()
        notification.is_read = True
        notification.save(update_fields=["is_read", "updated_at"])
        return response.Response(NotificationSerializer(notification, context=self.get_serializer_context()).data)


class StudentAnalyticsView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(ProgressService.student_analytics(request.user))


class TeacherAnalyticsView(APIView):
    permission_classes = [IsTeacherOrSuperAdmin]

    @extend_schema(responses=dict)
    def get(self, request):
        return Response(ProgressService.teacher_analytics())
