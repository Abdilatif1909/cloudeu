from rest_framework import decorators, exceptions, parsers, permissions, response, status, viewsets
from random import shuffle

from apps.common.models import AuditLog
from apps.common.permissions import IsTeacherOrSuperAdmin, ReadOnlyOrTeacher
from apps.common.services import AuditLogService

from .models import Question, Quiz
from .serializers import PublicQuestionSerializer, QuestionSerializer, QuizImportSerializer, QuizSerializer, QuizStartQuestionSerializer
from .services import QuizImportService


class QuizViewSet(viewsets.ModelViewSet):
    queryset = Quiz.objects.select_related("lesson", "lesson__course").prefetch_related("questions")
    serializer_class = QuizSerializer
    permission_classes = [ReadOnlyOrTeacher]
    parser_classes = [parsers.JSONParser, parsers.MultiPartParser, parsers.FormParser]
    filterset_fields = ["lesson", "lesson__course", "is_active"]
    search_fields = ["title", "description", "lesson__title", "lesson__course__title"]
    ordering_fields = ["created_at", "title", "lesson__order"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(lesson__course__teacher=user)
        return queryset

    def _validate_teacher_lesson(self, lesson):
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin and lesson.course.teacher_id != user.id:
            raise exceptions.PermissionDenied("Teachers can manage only their own course quizzes.")

    def perform_create(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data["lesson"])
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "quiz", instance.pk)

    def perform_update(self, serializer):
        self._validate_teacher_lesson(serializer.validated_data.get("lesson", serializer.instance.lesson))
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "quiz", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "quiz", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["get"], permission_classes=[permissions.IsAuthenticated])
    def start(self, request, pk=None):
        quiz = self.get_object()
        questions = list(quiz.questions.all())
        if quiz.randomize_questions:
            shuffle(questions)
        return response.Response(
            {
                "id": quiz.id,
                "title": quiz.title,
                "question_timer_seconds": quiz.question_timer_seconds,
                "pass_score": quiz.pass_score,
                "questions": QuizStartQuestionSerializer(questions, many=True, context={"shuffle_answers": quiz.shuffle_answers}).data,
            }
        )

    @decorators.action(detail=False, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin], url_path="import-json")
    def import_json(self, request):
        serializer = QuizImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = QuizImportService.parse_uploaded_file(serializer.validated_data["file"])
        result = QuizImportService.import_payload(payload, actor=request.user)
        AuditLogService.record(request, AuditLog.Action.IMPORT, "quiz.json", result.quiz.pk)
        return response.Response(
            {
                "quiz": QuizSerializer(result.quiz, context=self.get_serializer_context()).data,
                "created_questions": result.created_questions,
                "updated_questions": result.updated_questions,
                "skipped_duplicates": result.skipped_duplicates,
            },
            status=status.HTTP_201_CREATED,
        )


class QuestionViewSet(viewsets.ModelViewSet):
    queryset = Question.objects.select_related("quiz", "quiz__lesson")
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["quiz", "quiz__lesson", "quiz__lesson__course"]
    search_fields = ["question", "explanation"]
    ordering_fields = ["created_at", "id"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_authenticated and user.is_teacher and not user.is_super_admin:
            return queryset.filter(quiz__lesson__course__teacher=user)
        return queryset

    def get_serializer_class(self):
        user = self.request.user
        if self.action in {"list", "retrieve"} and not (user.is_authenticated and (user.is_teacher or user.is_super_admin)):
            return PublicQuestionSerializer
        return QuestionSerializer
