from django.contrib import admin
from django.http import JsonResponse
from django.urls import include, path
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
)


def health(request):
    return JsonResponse({"status": "ok"})


urlpatterns = [
    # Django Admin
    path("admin/", admin.site.urls),
    # Health Check
    path("health/", health, name="health"),
    # OpenAPI Schema
    path(
        "api/schema/",
        SpectacularAPIView.as_view(),
        name="schema",
    ),
    # Swagger UI
    path(
        "api/docs/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    # API v1
    path(
        "api/v1/auth/",
        include("authentication.urls"),
    ),
    path(
        "api/v1/customers/",
        include("customers.urls"),
    ),
    path(
        "api/v1/transactions/",
        include("transactions.urls"),
    ),
    path(
        "api/v1/alerts/",
        include("alerts.urls"),
    ),
    path(
        "api/v1/audit/",
        include("audit.urls"),
    ),
    path("api/v1/dashboard/", include("dashboard.urls")),
]
