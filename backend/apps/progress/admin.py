from django.contrib import admin

from .models import Bookmark, Certificate, LearningEvent, Notification, PDFReadingProgress, PersonalNote, QuizResult, StudentProgress


@admin.register(StudentProgress)
class StudentProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lesson", "completion_percentage", "completed", "completion_date")
    list_filter = ("completed", "lesson__course")
    search_fields = ("student__username", "student__email", "lesson__title")


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "score", "total", "percentage", "passed", "attempt_number", "duration", "created_at")
    list_filter = ("passed", "quiz__lesson__course", "created_at")
    search_fields = ("student__username", "student__email", "quiz__title")


@admin.register(LearningEvent)
class LearningEventAdmin(admin.ModelAdmin):
    list_display = ("student", "event_type", "course", "lesson", "study_seconds", "created_at")
    list_filter = ("event_type", "course", "created_at")
    search_fields = ("student__username", "student__email", "lesson__title", "course__title")


@admin.register(PDFReadingProgress)
class PDFReadingProgressAdmin(admin.ModelAdmin):
    list_display = ("student", "lecture", "current_page", "total_pages", "reading_percentage", "completed", "updated_at")
    list_filter = ("completed", "lecture__lesson__course")
    search_fields = ("student__username", "student__email", "lecture__title")


@admin.register(PersonalNote)
class PersonalNoteAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "course", "lesson", "lecture", "updated_at")
    list_filter = ("course", "updated_at")
    search_fields = ("title", "content", "student__username", "course__title", "lesson__title", "lecture__title")


@admin.register(Bookmark)
class BookmarkAdmin(admin.ModelAdmin):
    list_display = ("title", "student", "content_type", "object_id", "created_at")
    list_filter = ("content_type", "created_at")
    search_fields = ("title", "student__username", "url")


@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ("certificate_id", "student", "course", "issued_at")
    list_filter = ("course", "issued_at")
    search_fields = ("certificate_id", "verification_code", "student__username", "course__title")


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "notification_type", "recipient", "course", "is_read", "created_at")
    list_filter = ("notification_type", "is_read", "course")
    search_fields = ("title", "message", "recipient__username", "course__title")
