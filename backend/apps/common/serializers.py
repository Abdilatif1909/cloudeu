from rest_framework import serializers

from .models import AuditLog


class AuditLogSerializer(serializers.ModelSerializer):
    actor_name = serializers.CharField(source="actor.get_full_name", read_only=True)

    class Meta:
        model = AuditLog
        fields = ["id", "actor", "actor_name", "action", "target", "target_id", "metadata", "ip_address", "created_at"]
        read_only_fields = fields


class MessageSerializer(serializers.Serializer):
    detail = serializers.CharField()
