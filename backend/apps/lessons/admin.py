from django.contrib import admin

from .models import Lesson


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("title", "course", "lesson_number", "order")
    list_filter = ("course",)
    search_fields = ("title", "description", "course__title", "course__code")
