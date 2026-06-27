import csv

from django.http import HttpResponse
from rest_framework import decorators, permissions, response, status, viewsets

from apps.common.models import AuditLog
from apps.common.permissions import IsTeacherOrSuperAdmin, ReadOnlyOrTeacher
from apps.common.services import AuditLogService

from .models import AcademicGroup, AcademicYear, Course, CourseEnrollment, Department, EducationDirection, Faculty, Semester, University
from .serializers import (
    AcademicGroupSerializer,
    AcademicYearSerializer,
    BulkEnrollmentSerializer,
    CSVEnrollmentImportSerializer,
    CourseEnrollmentSerializer,
    CourseSerializer,
    DepartmentSerializer,
    EducationDirectionSerializer,
    FacultySerializer,
    SemesterSerializer,
    UniversitySerializer,
)
from .services import CourseCloneService, EnrollmentService


class UniversityViewSet(viewsets.ModelViewSet):
    queryset = University.objects.all()
    serializer_class = UniversitySerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["is_active"]
    search_fields = ["name", "code", "address"]
    ordering_fields = ["name", "code", "created_at"]


class FacultyViewSet(viewsets.ModelViewSet):
    queryset = Faculty.objects.select_related("university")
    serializer_class = FacultySerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["university", "is_active"]
    search_fields = ["name", "code", "university__name"]
    ordering_fields = ["name", "code", "created_at"]


class DepartmentViewSet(viewsets.ModelViewSet):
    queryset = Department.objects.select_related("faculty", "faculty__university")
    serializer_class = DepartmentSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["faculty", "faculty__university", "is_active"]
    search_fields = ["name", "code", "faculty__name", "faculty__university__name"]
    ordering_fields = ["name", "code", "created_at"]


class AcademicYearViewSet(viewsets.ModelViewSet):
    queryset = AcademicYear.objects.all()
    serializer_class = AcademicYearSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["is_active"]
    search_fields = ["name"]
    ordering_fields = ["starts_on", "ends_on", "name"]


class SemesterViewSet(viewsets.ModelViewSet):
    queryset = Semester.objects.select_related("academic_year")
    serializer_class = SemesterSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["academic_year", "number", "is_active"]
    search_fields = ["name", "academic_year__name"]
    ordering_fields = ["academic_year__starts_on", "number", "starts_on"]


class EducationDirectionViewSet(viewsets.ModelViewSet):
    queryset = EducationDirection.objects.select_related("faculty", "faculty__university")
    serializer_class = EducationDirectionSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["faculty", "faculty__university", "is_active"]
    search_fields = ["name", "code", "faculty__name"]
    ordering_fields = ["name", "code", "created_at"]


class AcademicGroupViewSet(viewsets.ModelViewSet):
    queryset = AcademicGroup.objects.select_related("direction", "direction__faculty", "semester")
    serializer_class = AcademicGroupSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["direction", "direction__faculty", "semester", "is_active"]
    search_fields = ["name", "code", "direction__name"]
    ordering_fields = ["name", "code", "created_at"]


class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.select_related("department", "department__faculty", "academic_semester", "teacher").prefetch_related("lessons", "enrollments")
    serializer_class = CourseSerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["department", "department__faculty", "academic_semester", "teacher", "semester", "credits", "is_active", "is_published", "is_archived"]
    search_fields = ["title", "code", "description", "department__name", "teacher__username", "teacher__first_name", "teacher__last_name"]
    ordering_fields = ["title", "code", "semester", "credits", "created_at", "updated_at"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if not user.is_authenticated:
            return queryset.filter(is_active=True, is_published=True, is_archived=False)
        if user.is_student:
            return queryset.filter(enrollments__student=user, enrollments__status=CourseEnrollment.Status.ACTIVE)
        if user.is_teacher and not user.is_super_admin:
            return queryset.filter(teacher=user)
        return queryset

    def perform_create(self, serializer):
        teacher = self.request.user if self.request.user.is_teacher and not self.request.user.is_super_admin else serializer.validated_data.get("teacher")
        instance = serializer.save(teacher=teacher)
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "course", instance.pk)

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "course", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "course", instance.pk)
        instance.delete()

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def archive(self, request, pk=None):
        course = self.get_object()
        course.is_archived = True
        course.is_active = False
        course.save(update_fields=["is_archived", "is_active", "updated_at"])
        AuditLogService.record(request, AuditLog.Action.EDIT, "course.archive", course.pk)
        return response.Response(CourseSerializer(course, context=self.get_serializer_context()).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def publish(self, request, pk=None):
        course = self.get_object()
        course.is_published = True
        course.is_active = True
        course.save(update_fields=["is_published", "is_active", "updated_at"])
        AuditLogService.record(request, AuditLog.Action.EDIT, "course.publish", course.pk)
        return response.Response(CourseSerializer(course, context=self.get_serializer_context()).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def unpublish(self, request, pk=None):
        course = self.get_object()
        course.is_published = False
        course.save(update_fields=["is_published", "updated_at"])
        AuditLogService.record(request, AuditLog.Action.EDIT, "course.unpublish", course.pk)
        return response.Response(CourseSerializer(course, context=self.get_serializer_context()).data)

    @decorators.action(detail=True, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def clone(self, request, pk=None):
        course = self.get_object()
        clone = CourseCloneService.clone_course(course, title=request.data.get("title"), code=request.data.get("code"), teacher=request.user)
        AuditLogService.record(request, AuditLog.Action.IMPORT, "course.clone", clone.pk, {"source_course": course.pk})
        return response.Response(CourseSerializer(clone, context=self.get_serializer_context()).data, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=["get"], permission_classes=[permissions.IsAuthenticated], url_path="my")
    def my_courses(self, request):
        serializer = self.get_serializer(self.get_queryset(), many=True)
        return response.Response(serializer.data)

    @decorators.action(detail=False, methods=["get"], permission_classes=[IsTeacherOrSuperAdmin])
    def export(self, request):
        export_format = request.query_params.get("format", "json")
        queryset = self.get_queryset()
        AuditLogService.record(request, AuditLog.Action.EXPORT, "courses", metadata={"format": export_format})
        if export_format == "csv":
            http_response = HttpResponse(content_type="text/csv")
            http_response["Content-Disposition"] = 'attachment; filename="courses.csv"'
            writer = csv.writer(http_response)
            writer.writerow(["code", "title", "semester", "credits", "department", "teacher", "is_published", "is_archived"])
            for course in queryset:
                writer.writerow([course.code, course.title, course.semester, course.credits, course.department_id or "", course.teacher_id or "", course.is_published, course.is_archived])
            return http_response
        return response.Response(CourseSerializer(queryset, many=True, context=self.get_serializer_context()).data)


class CourseEnrollmentViewSet(viewsets.ModelViewSet):
    queryset = CourseEnrollment.objects.select_related("student", "course", "group")
    serializer_class = CourseEnrollmentSerializer
    permission_classes = [permissions.IsAuthenticated]
    filterset_fields = ["student", "course", "group", "status"]
    search_fields = ["student__username", "student__email", "course__title", "course__code", "group__name"]
    ordering_fields = ["enrolled_at", "created_at", "status"]

    def get_queryset(self):
        queryset = super().get_queryset()
        user = self.request.user
        if user.is_student:
            return queryset.filter(student=user)
        if user.is_teacher and not user.is_super_admin:
            return queryset.filter(course__teacher=user)
        return queryset

    def get_permissions(self):
        if self.action in {"create", "update", "partial_update", "destroy", "bulk", "import_csv"}:
            return [IsTeacherOrSuperAdmin()]
        return super().get_permissions()

    def perform_create(self, serializer):
        course = serializer.validated_data["course"]
        user = self.request.user
        if user.is_teacher and not user.is_super_admin and course.teacher_id != user.id:
            from rest_framework.exceptions import PermissionDenied

            raise PermissionDenied("Teachers can enroll students only into their own courses.")
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.IMPORT, "course_enrollment", instance.pk)

    @decorators.action(detail=False, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin])
    def bulk(self, request):
        serializer = BulkEnrollmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = EnrollmentService.bulk_enroll(
            serializer.validated_data["course"],
            serializer.validated_data["students"],
            serializer.validated_data.get("group"),
            serializer.validated_data["status"],
        )
        AuditLogService.record(request, AuditLog.Action.IMPORT, "course_enrollment.bulk", serializer.validated_data["course"].pk, result)
        return response.Response(result, status=status.HTTP_201_CREATED)

    @decorators.action(detail=False, methods=["post"], permission_classes=[IsTeacherOrSuperAdmin], url_path="import-csv")
    def import_csv(self, request):
        serializer = CSVEnrollmentImportSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        result = EnrollmentService.import_csv(serializer.validated_data["course"], serializer.validated_data["file"])
        AuditLogService.record(request, AuditLog.Action.IMPORT, "course_enrollment.csv", serializer.validated_data["course"].pk, result)
        return response.Response(result, status=status.HTTP_201_CREATED)
