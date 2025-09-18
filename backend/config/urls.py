"""
URL configuration for Urbia Traffic Analysis project.
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse


def api_root(request):
    """API root endpoint"""
    return JsonResponse(
        {
            "message": "Urbia Traffic Analysis API v1.0",
            "endpoints": {
                "admin": "/admin/",
                "api": {
                    "auth": "/api/v1/auth/",
                    "traffic": "/api/v1/traffic/",
                    "plates": "/api/v1/plates/",
                    "predictions": "/api/v1/predictions/",
                    "external": "/api/v1/external/",
                    "notifications": "/api/v1/notifications/",
                },
            },
        }
    )


urlpatterns = [
    path("admin/", admin.site.urls),
    path("", api_root, name="api-root"),
    # API REST Endpoints v1
    path("api/auth/", include("apps.auth_app.urls")),  # /api/auth/login/
    # path('api/v1/traffic/', include('traffic_analysis.urls')),
    # path('api/v1/plates/', include('plate_detection.urls')),
    # path('api/v1/predictions/', include('traffic_prediction.urls')),
    # path('api/v1/external/', include('external_apis.urls')),
    # path('api/v1/notifications/', include('notifications.urls')),
]

# Serve media files in development
if settings.DEBUG:
    # Debug toolbar
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    # Static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
