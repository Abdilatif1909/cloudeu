import json
from dataclasses import dataclass

from django.db import transaction
from rest_framework import serializers

from apps.lessons.models import Lesson

from .models import Question, Quiz


@dataclass
class QuizImportResult:
    quiz: Quiz
    created_questions: int
    updated_questions: int
    skipped_duplicates: int


class QuizImportService:
    @staticmethod
    def parse_uploaded_file(uploaded_file) -> dict:
        try:
            return json.loads(uploaded_file.read().decode("utf-8"))
        except UnicodeDecodeError as exc:
            raise serializers.ValidationError({"file": "JSON file must be UTF-8 encoded."}) from exc
        except json.JSONDecodeError as exc:
            raise serializers.ValidationError({"file": f"Invalid JSON: {exc.msg}"}) from exc

    @classmethod
    @transaction.atomic
    def import_payload(cls, payload: dict, actor=None) -> QuizImportResult:
        lesson_id = payload.get("lesson")
        title = payload.get("title")
        questions = payload.get("questions")

        if not lesson_id or not title or not isinstance(questions, list):
            raise serializers.ValidationError("Payload must include lesson, title, and questions list.")

        lesson = Lesson.objects.filter(pk=lesson_id).first()
        if lesson is None:
            raise serializers.ValidationError({"lesson": "Lesson does not exist."})
        if actor and actor.is_authenticated and actor.is_teacher and not actor.is_super_admin and lesson.course.teacher_id != actor.id:
            raise serializers.ValidationError({"lesson": "Teachers can import quizzes only for their own courses."})

        quiz, _ = Quiz.objects.update_or_create(
            lesson=lesson,
            title=title,
            defaults={"description": payload.get("description", ""), "is_active": payload.get("is_active", True)},
        )

        created_questions = 0
        updated_questions = 0
        skipped_duplicates = 0
        seen_questions: set[str] = set()

        for index, item in enumerate(questions, start=1):
            question_text = str(item.get("question", "")).strip()
            options = item.get("options")
            correct_index = item.get("correct")
            explanation = item.get("explanation", "")

            if not question_text or not isinstance(options, list) or len(options) < 2:
                raise serializers.ValidationError({f"questions[{index}]": "Question text and at least two options are required."})
            if not isinstance(correct_index, int) or correct_index < 0 or correct_index >= len(options):
                raise serializers.ValidationError({f"questions[{index}].correct": "Correct must be a valid option index."})

            normalized = question_text.lower()
            if normalized in seen_questions:
                skipped_duplicates += 1
                continue
            seen_questions.add(normalized)

            defaults = {
                "options": options,
                "correct_answer": options[correct_index],
                "explanation": explanation,
            }
            question, created = Question.objects.update_or_create(quiz=quiz, question=question_text, defaults=defaults)
            if created:
                created_questions += 1
            else:
                updated_questions += 1

        return QuizImportResult(
            quiz=quiz,
            created_questions=created_questions,
            updated_questions=updated_questions,
            skipped_duplicates=skipped_duplicates,
        )
