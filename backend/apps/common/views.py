from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.db import connections
from django.db.utils import OperationalError
from drf_spectacular.utils import extend_schema, inline_serializer
from rest_framework import permissions, serializers, status, viewsets
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import AuditLog
from .serializers import AuditLogSerializer
from .services import GlobalSearchService, StatisticsService


class GlobalSearchView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(
        responses=inline_serializer(
            "GlobalSearchResponse",
            {"query": serializers.CharField(), "results": serializers.ListField(child=serializers.DictField())},
        )
    )
    @method_decorator(cache_page(60))
    def get(self, request):
        query = request.query_params.get("q", "").strip()
        return Response({"query": query, "results": GlobalSearchService.build_results(query)})


class StatisticsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    @extend_schema(responses=inline_serializer("StatisticsResponse", {"data": serializers.JSONField()}))
    def get(self, request):
        return Response(StatisticsService.dashboard())


class AuditLogViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AuditLog.objects.select_related("actor")
    serializer_class = AuditLogSerializer
    permission_classes = [permissions.IsAdminUser]
    filterset_fields = ["actor", "action", "target"]
    search_fields = ["actor__username", "actor__email", "target", "target_id"]
    ordering_fields = ["created_at", "action", "target"]


class HealthView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=inline_serializer("HealthResponse", {"status": serializers.CharField()}))
    def get(self, request):
        return Response({"status": "ok"})


class LiveView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=inline_serializer("LiveResponse", {"status": serializers.CharField()}))
    def get(self, request):
        return Response({"status": "live"})


class ReadyView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=inline_serializer("ReadyResponse", {"status": serializers.CharField(), "database": serializers.CharField(required=False)}))
    def get(self, request):
        try:
            connections["default"].cursor()
        except OperationalError as exc:
            return Response({"status": "not_ready", "database": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)
        return Response({"status": "ready", "database": "ok"})


class VersionView(APIView):
    permission_classes = [permissions.AllowAny]

    @extend_schema(responses=inline_serializer("VersionResponse", {"name": serializers.CharField(), "version": serializers.CharField()}))
    @method_decorator(cache_page(300))
    def get(self, request):
        return Response({"name": "university-lms", "version": settings.SPECTACULAR_SETTINGS.get("VERSION", "1.0.0")})
