from django.contrib import admin, messages
from django.shortcuts import redirect
from django.template.response import TemplateResponse
from django.urls import path
from rest_framework import serializers

from .models import Question, Quiz
from .services import QuizImportService


class QuestionInline(admin.TabularInline):
    model = Question
    extra = 1


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "lesson", "is_active", "pass_score", "randomize_questions", "shuffle_answers", "created_at")
    list_filter = ("is_active", "lesson__course")
    search_fields = ("title", "description", "lesson__title")
    inlines = [QuestionInline]
    change_list_template = "admin/quizzes/quiz/change_list.html"

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path("import-json/", self.admin_site.admin_view(self.import_json_view), name="quizzes_quiz_import_json"),
        ]
        return custom_urls + urls

    def import_json_view(self, request):
        if request.method == "POST":
            uploaded_file = request.FILES.get("file")
            if not uploaded_file:
                messages.error(request, "Please choose a quiz.json file.")
                return redirect("admin:quizzes_quiz_import_json")
            try:
                payload = QuizImportService.parse_uploaded_file(uploaded_file)
                result = QuizImportService.import_payload(payload, actor=request.user)
            except serializers.ValidationError as exc:
                messages.error(request, exc.detail if hasattr(exc, "detail") else str(exc))
                return redirect("admin:quizzes_quiz_import_json")

            messages.success(
                request,
                (
                    f"Imported '{result.quiz.title}': {result.created_questions} created, "
                    f"{result.updated_questions} updated, {result.skipped_duplicates} duplicates skipped."
                ),
            )
            return redirect("admin:quizzes_quiz_changelist")

        context = {
            **self.admin_site.each_context(request),
            "title": "Import quiz JSON",
            "opts": self.model._meta,
        }
        return TemplateResponse(request, "admin/quizzes/quiz/import_json.html", context)


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("question", "quiz", "correct_answer")
    list_filter = ("quiz", "quiz__lesson__course")
    search_fields = ("question", "explanation")
