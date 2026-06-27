from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.http import Http404
from django.views.generic import TemplateView
from django.views.static import serve as static_serve
from django.urls import include, path, re_path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from apps.common.views import HealthView, LiveView, ReadyView, VersionView


def serve_static_file(request, path):
    for document_root in (settings.STATIC_ROOT, *settings.STATICFILES_DIRS):
        try:
            return static_serve(request, path, document_root=document_root)
        except Http404:
            continue
    raise Http404(path)

urlpatterns = [
    path("health/", HealthView.as_view(), name="health"),
    path("ready/", ReadyView.as_view(), name="ready"),
    path("live/", LiveView.as_view(), name="live"),
    path("version/", VersionView.as_view(), name="version"),
    path("admin/", admin.site.urls),
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
    path("api/v1/", include("api.urls")),
    re_path(r"^static/(?P<path>.*)$", serve_static_file, name="static-files"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

urlpatterns += [
    path("", TemplateView.as_view(template_name="frontend/index.html"), name="frontend"),
    re_path(r"^(?!static/|media/|api/|admin/|health/|ready/|live/|version/).*$", TemplateView.as_view(template_name="frontend/index.html"), name="frontend-spa"),
]
