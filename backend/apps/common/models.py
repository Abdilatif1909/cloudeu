from django.db import models
from django.conf import settings


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class AuditLog(TimeStampedModel):
    class Action(models.TextChoices):
        LOGIN = "login", "Login"
        UPLOAD = "upload", "Upload"
        DELETE = "delete", "Delete"
        EDIT = "edit", "Edit"
        IMPORT = "import", "Import"
        EXPORT = "export", "Export"
        ADMIN = "admin", "Admin action"

    actor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name="audit_logs", on_delete=models.SET_NULL, blank=True, null=True)
    action = models.CharField(max_length=32, choices=Action.choices)
    target = models.CharField(max_length=255, blank=True)
    target_id = models.CharField(max_length=64, blank=True)
    metadata = models.JSONField(default=dict, blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["actor", "action", "created_at"], name="common_audi_actor__e6c790_idx")]

    def __str__(self) -> str:
        return f"{self.action}: {self.target}"
