"""
Root URL configuration for construction_platform.

All API routes are versioned under /api/v1/.
"""

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

urlpatterns = [
    # Admin
    path("admin/", admin.site.urls),

    # API v1
    path("api/v1/auth/", include("apps.users.urls")),
    path("api/v1/contractors/", include("apps.marketplace.urls")),
    path("api/v1/projects/", include("apps.projects.urls")),
    path("api/v1/bookings/", include("apps.bookings.urls")),
    path("api/v1/reviews/", include("apps.reviews.urls")),
    path("api/v1/designs/", include("apps.designs.urls")),
    path("api/v1/notifications/", include("apps.notifications.urls")),

    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
