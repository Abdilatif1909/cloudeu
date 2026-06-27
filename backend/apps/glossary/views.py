import csv

from django.http import HttpResponse
from rest_framework import decorators, response, viewsets

from apps.common.models import AuditLog
from apps.common.permissions import ReadOnlyOrTeacher
from apps.common.services import AuditLogService

from .models import Glossary
from .serializers import GlossarySerializer


class GlossaryViewSet(viewsets.ModelViewSet):
    queryset = Glossary.objects.all()
    serializer_class = GlossarySerializer
    permission_classes = [ReadOnlyOrTeacher]
    filterset_fields = ["category"]
    search_fields = ["term", "definition", "category"]
    ordering_fields = ["term", "category", "created_at"]

    def perform_create(self, serializer):
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.UPLOAD, "glossary", instance.pk)

    def perform_update(self, serializer):
        instance = serializer.save()
        AuditLogService.record(self.request, AuditLog.Action.EDIT, "glossary", instance.pk)

    def perform_destroy(self, instance):
        AuditLogService.record(self.request, AuditLog.Action.DELETE, "glossary", instance.pk)
        instance.delete()

    @decorators.action(detail=False, methods=["get"])
    def export(self, request):
        export_format = request.query_params.get("format", "json")
        queryset = self.get_queryset()
        AuditLogService.record(request, AuditLog.Action.EXPORT, "glossary", metadata={"format": export_format})
        if export_format == "csv":
            http_response = HttpResponse(content_type="text/csv")
            http_response["Content-Disposition"] = 'attachment; filename="glossary.csv"'
            writer = csv.writer(http_response)
            writer.writerow(["term", "definition", "category"])
            for item in queryset:
                writer.writerow([item.term, item.definition, item.category])
            return http_response
        return response.Response(GlossarySerializer(queryset, many=True, context=self.get_serializer_context()).data)
