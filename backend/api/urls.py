from django.urls import include, path
from rest_framework.routers import DefaultRouter

from apps.accounts.views import ChangePasswordView, LogoutView, ProfileView
from apps.common.views import AuditLogViewSet, GlobalSearchView, StatisticsView
from apps.courses.views import (
    AcademicGroupViewSet,
    AcademicYearViewSet,
    CourseEnrollmentViewSet,
    CourseViewSet,
    DepartmentViewSet,
    EducationDirectionViewSet,
    FacultyViewSet,
    SemesterViewSet,
    UniversityViewSet,
)
from apps.glossary.views import GlossaryViewSet
from apps.lessons.views import LessonViewSet
from apps.materials.views import LectureMaterialViewSet, PracticeMaterialViewSet, ResourceViewSet
from apps.progress.views import (
    BookmarkViewSet,
    CertificateViewSet,
    LearningEventViewSet,
    NotificationViewSet,
    PDFReadingProgressViewSet,
    PersonalNoteViewSet,
    ProgressSummaryView,
    QuizResultViewSet,
    StudentAnalyticsView,
    StudentProgressViewSet,
    TeacherAnalyticsView,
)
from apps.quizzes.views import QuestionViewSet, QuizViewSet
from apps.videos.views import VideoLessonViewSet

router = DefaultRouter()
router.register("universities", UniversityViewSet, basename="university")
router.register("faculties", FacultyViewSet, basename="faculty")
router.register("departments", DepartmentViewSet, basename="department")
router.register("academic-years", AcademicYearViewSet, basename="academic-year")
router.register("semesters", SemesterViewSet, basename="semester")
router.register("education-directions", EducationDirectionViewSet, basename="education-direction")
router.register("academic-groups", AcademicGroupViewSet, basename="academic-group")
router.register("audit-logs", AuditLogViewSet, basename="audit-log")
router.register("courses", CourseViewSet, basename="course")
router.register("course-enrollments", CourseEnrollmentViewSet, basename="course-enrollment")
router.register("lessons", LessonViewSet, basename="lesson")
router.register("lecture-materials", LectureMaterialViewSet, basename="lecture-material")
router.register("practice-materials", PracticeMaterialViewSet, basename="practice-material")
router.register("resources", ResourceViewSet, basename="resource")
router.register("videos", VideoLessonViewSet, basename="video")
router.register("quizzes", QuizViewSet, basename="quiz")
router.register("questions", QuestionViewSet, basename="question")
router.register("progress", StudentProgressViewSet, basename="progress")
router.register("learning-events", LearningEventViewSet, basename="learning-event")
router.register("pdf-progress", PDFReadingProgressViewSet, basename="pdf-progress")
router.register("notes", PersonalNoteViewSet, basename="note")
router.register("bookmarks", BookmarkViewSet, basename="bookmark")
router.register("certificates", CertificateViewSet, basename="certificate")
router.register("notifications", NotificationViewSet, basename="notification")
router.register("quiz-results", QuizResultViewSet, basename="quiz-result")
router.register("glossary", GlossaryViewSet, basename="glossary")

urlpatterns = [
    path("", include(router.urls)),
    path("auth/", include("apps.accounts.urls")),
    path("auth/profile/", ProfileView.as_view(), name="profile"),
    path("auth/change-password/", ChangePasswordView.as_view(), name="change-password"),
    path("auth/logout/", LogoutView.as_view(), name="logout"),
    path("progress-summary/", ProgressSummaryView.as_view(), name="progress-summary"),
    path("analytics/student/", StudentAnalyticsView.as_view(), name="student-analytics"),
    path("analytics/teacher/", TeacherAnalyticsView.as_view(), name="teacher-analytics"),
    path("search/", GlobalSearchView.as_view(), name="global-search"),
    path("statistics/", StatisticsView.as_view(), name="statistics"),
]
