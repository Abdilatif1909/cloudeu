from rest_framework import serializers

from .models import Glossary


class GlossarySerializer(serializers.ModelSerializer):
    class Meta:
        model = Glossary
        fields = ["id", "term", "definition", "category"]
