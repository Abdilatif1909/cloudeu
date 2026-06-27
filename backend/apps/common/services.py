from django.contrib.auth import get_user_model
from django.db.models import Q, QuerySet

from apps.courses.models import AcademicGroup, Course, CourseEnrollment, Department, EducationDirection, Faculty, University
from apps.glossary.models import Glossary
from apps.lessons.models import Lesson
from apps.materials.models import LectureMaterial, PracticeMaterial, Resource
from apps.quizzes.models import Quiz
from apps.videos.models import VideoLesson
from .models import AuditLog


class AuditLogService:
    @staticmethod
    def record(request, action: str, target: str = "", target_id: str = "", metadata: dict | None = None) -> AuditLog:
        actor = getattr(request, "user", None)
        if not actor or not actor.is_authenticated:
            actor = None
        forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR", "")
        ip_address = forwarded_for.split(",")[0].strip() if forwarded_for else request.META.get("REMOTE_ADDR")
        return AuditLog.objects.create(
            actor=actor,
            action=action,
            target=target,
            target_id=str(target_id or ""),
            metadata=metadata or {},
            ip_address=ip_address or None,
        )


class StatisticsService:
    @staticmethod
    def dashboard() -> dict:
        User = get_user_model()
        return {
            "courses": Course.objects.count(),
            "universities": University.objects.count(),
            "faculties": Faculty.objects.count(),
            "departments": Department.objects.count(),
            "groups": AcademicGroup.objects.count(),
            "enrollments": CourseEnrollment.objects.count(),
            "audit_logs": AuditLog.objects.count(),
            "lessons": Lesson.objects.count(),
            "lectures": LectureMaterial.objects.count(),
            "videos": VideoLesson.objects.count(),
            "practice_files": PracticeMaterial.objects.count(),
            "resources": Resource.objects.count(),
            "quizzes": Quiz.objects.count(),
            "students": User.objects.filter(role="student").count(),
            "latest_uploads": list(Resource.objects.order_by("-created_at").values("id", "title", "category", "created_at")[:5]),
            "recent_activity": list(
                LectureMaterial.objects.order_by("-updated_at").values("id", "title", "updated_at", "lesson__course__title")[:5]
            ),
        }


class GlobalSearchService:
    @staticmethod
    def build_results(query: str) -> list[dict]:
        if not query:
            return []
        return [
            *GlobalSearchService._serialize(Course.objects.filter(Q(title__icontains=query) | Q(code__icontains=query) | Q(description__icontains=query)), "course", "title", "description"),
            *GlobalSearchService._serialize(University.objects.filter(Q(name__icontains=query) | Q(code__icontains=query)), "university", "name", "code"),
            *GlobalSearchService._serialize(Faculty.objects.filter(Q(name__icontains=query) | Q(code__icontains=query)), "faculty", "name", "code"),
            *GlobalSearchService._serialize(Department.objects.filter(Q(name__icontains=query) | Q(code__icontains=query)), "department", "name", "code"),
            *GlobalSearchService._serialize(EducationDirection.objects.filter(Q(name__icontains=query) | Q(code__icontains=query)), "direction", "name", "code"),
            *GlobalSearchService._serialize(AcademicGroup.objects.filter(Q(name__icontains=query) | Q(code__icontains=query)), "group", "name", "code"),
            *GlobalSearchService._serialize(Lesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)), "lesson", "title", "description"),
            *GlobalSearchService._serialize(LectureMaterial.objects.filter(Q(title__icontains=query) | Q(description__icontains=query)), "lecture", "title", "description"),
            *GlobalSearchService._serialize(VideoLesson.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(speaker__icontains=query)), "video", "title", "description"),
            *GlobalSearchService._serialize(Glossary.objects.filter(Q(term__icontains=query) | Q(definition__icontains=query) | Q(category__icontains=query)), "glossary", "term", "definition"),
            *GlobalSearchService._serialize(Resource.objects.filter(Q(title__icontains=query) | Q(description__icontains=query) | Q(category__icontains=query)), "resource", "title", "description"),
        ]

    @staticmethod
    def _serialize(queryset: QuerySet, result_type: str, title_field: str, description_field: str) -> list[dict]:
        return [
            {
                "type": result_type,
                "id": item.pk,
                "title": getattr(item, title_field),
                "description": getattr(item, description_field, ""),
            }
            for item in queryset[:10]
        ]
