from rest_framework import serializers
from random import shuffle

from .models import Question, Quiz


class QuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "quiz", "question", "options", "correct_answer", "explanation"]

    def validate_options(self, value):
        if not isinstance(value, list) or len(value) < 2:
            raise serializers.ValidationError("Options must be a list with at least two values.")
        if any(not str(option).strip() for option in value):
            raise serializers.ValidationError("Options cannot contain empty values.")
        return value

    def validate(self, attrs):
        options = attrs.get("options", getattr(self.instance, "options", []))
        answer = attrs.get("correct_answer", getattr(self.instance, "correct_answer", ""))
        if answer not in options:
            raise serializers.ValidationError({"correct_answer": "Correct answer must exist in options."})
        return attrs


class PublicQuestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Question
        fields = ["id", "quiz", "question", "options"]


class QuizSerializer(serializers.ModelSerializer):
    lesson_title = serializers.CharField(source="lesson.title", read_only=True)
    questions = PublicQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "lesson",
            "lesson_title",
            "title",
            "description",
            "is_active",
            "randomize_questions",
            "shuffle_answers",
            "question_timer_seconds",
            "pass_score",
            "questions",
        ]


class QuizStartQuestionSerializer(serializers.ModelSerializer):
    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ["id", "question", "options"]

    def get_options(self, obj):
        options = list(obj.options)
        if self.context.get("shuffle_answers"):
            shuffle(options)
        return options


class QuizImportSerializer(serializers.Serializer):
    file = serializers.FileField()

    def validate_file(self, value):
        if not value.name.lower().endswith(".json"):
            raise serializers.ValidationError("Only quiz.json files are accepted.")
        return value
