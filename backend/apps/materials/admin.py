from django.contrib import admin

from .models import LectureMaterial, PracticeMaterial, Resource


@admin.register(LectureMaterial)
class LectureMaterialAdmin(admin.ModelAdmin):
    list_display = ("lecture_number", "title", "lesson", "is_published", "view_count", "download_count", "updated_at")
    list_filter = ("is_published", "lesson__course")
    search_fields = ("title", "description", "lesson__title", "lesson__course__title", "lesson__course__code")
    readonly_fields = ("download_count", "view_count", "created_at", "updated_at")


@admin.register(PracticeMaterial)
class PracticeMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "difficulty", "estimated_time", "updated_at")
    list_filter = ("difficulty", "lesson__course")
    search_fields = ("title", "description", "lesson__title", "lesson__course__title", "lesson__course__code")
    readonly_fields = ("created_at", "updated_at")


@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ("title", "category", "course", "lesson", "is_published", "download_count", "updated_at")
    list_filter = ("category", "is_published", "course")
    search_fields = ("title", "description", "course__title", "lesson__title")
    readonly_fields = ("download_count", "created_at", "updated_at")
