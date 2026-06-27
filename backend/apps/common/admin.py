from django.contrib import admin

from .models import AuditLog
from .services import StatisticsService


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ("action", "actor", "target", "target_id", "ip_address", "created_at")
    list_filter = ("action", "created_at")
    search_fields = ("actor__username", "target", "target_id")
    readonly_fields = ("actor", "action", "target", "target_id", "metadata", "ip_address", "created_at", "updated_at")

admin.site.site_header = "Cloud Education Platform Administration"
admin.site.site_title = "cloude.uz Admin"
admin.site.index_title = "Sun'iy intellekt asoslari"
admin.site.index_template = "admin/index.html"

_original_each_context = admin.site.each_context


def each_context_with_lms_dashboard(request):
    context = _original_each_context(request)
    context["lms_dashboard"] = StatisticsService.dashboard()
    return context


admin.site.each_context = each_context_with_lms_dashboard
