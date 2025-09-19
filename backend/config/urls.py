"""
URL configuration for SIMPTV Traffic Analysis project.
Auto-discovers and includes URL patterns from all installed apps.
"""

import importlib
from django.contrib import admin
from django.urls import path, include, reverse
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from django.apps import apps
from django.urls import get_resolver
from rest_framework import permissions
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularRedocView,
    SpectacularSwaggerView,
)


def get_available_endpoints():
    """Dynamically discover all available API endpoints"""
    endpoints = {
        "admin": "/admin/",
        "api_docs": {
            "schema": "/api/schema/",
            "swagger": "/api/schema/swagger-ui/",
            "redoc": "/api/schema/redoc/",
        },
        "api": {},
    }

    # Get all installed local apps
    local_apps = [app for app in settings.INSTALLED_APPS if app.startswith("apps.")]

    for app_config in local_apps:
        try:
            app_name = app_config.split(".")[-1]  # Get app name from 'apps.auth_app'

            # Try to import the urls module
            urls_module = importlib.import_module(f"{app_config}.urls")

            # Map app names to API paths
            api_path_mapping = {
                "auth_app": "auth",
                "traffic_app": "traffic",
                "plates_app": "plates",
                "external_apis": "external",
                "notifications": "notifications",
                "predictions_app": "predictions",
                "users_app": "users",
            }

            api_key = api_path_mapping.get(app_name, app_name.replace("_app", ""))
            endpoints["api"][api_key] = f"/api/{api_key}/"

        except ImportError:
            # App doesn't have urls.py, skip it
            continue

    return endpoints


def api_root(request):
    """
    API Root Endpoint
    Returns information about the SIMPTV API and available endpoints
    """
    endpoints = get_available_endpoints()

    return JsonResponse(
        {
            "message": "SIMPTV - Sistema Inteligente de Monitoreo y Predicción de Tráfico Vehicular",
            "version": "1.0.0",
            "description": "API REST para análisis de tráfico, detección de placas y predicciones ML",
            "university": "Universidad de Milagro - Ingeniería en Software",
            "framework": "Django REST Framework",
            "endpoints": endpoints,
            "status": "active",
            "docs": {
                "swagger": f"{request.build_absolute_uri('/api/schema/swagger-ui/')}",
                "redoc": f"{request.build_absolute_uri('/api/schema/redoc/')}",
                "openapi_schema": f"{request.build_absolute_uri('/api/schema/')}",
            },
        }
    )


# Base URL patterns
urlpatterns = [
    # Admin interface
    path("admin/", admin.site.urls),
    # API Root
    path("", api_root, name="api-root"),
    # API Documentation
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "api/schema/swagger-ui/",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    path(
        "api/schema/redoc/",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
]


# Dynamically include URL patterns from installed apps
def include_app_urls():
    """Dynamically include URLs from all installed local apps"""
    app_urls = []
    local_apps = [app for app in settings.INSTALLED_APPS if app.startswith("apps.")]

    # API path mapping for cleaner URLs
    api_path_mapping = {
        "auth_app": "auth",
        "traffic_app": "traffic",
        "plates_app": "plates",
        "external_apis": "external",
        "notifications": "notifications",
        "predictions_app": "predictions",
        "users_app": "users",
    }

    for app_config in local_apps:
        try:
            app_name = app_config.split(".")[-1]

            # Try to import urls module to check if it exists
            importlib.import_module(f"{app_config}.urls")

            # Get clean API path
            api_path = api_path_mapping.get(app_name, app_name.replace("_app", ""))

            # Add to URL patterns
            app_urls.append(path(f"api/{api_path}/", include(f"{app_config}.urls")))

        except ImportError:
            # App doesn't have urls.py, skip silently
            continue

    return app_urls


# Add dynamically discovered app URLs
urlpatterns.extend(include_app_urls())

# Serve media files in development
if settings.DEBUG:
    # Debug toolbar
    urlpatterns += [path("__debug__/", include("debug_toolbar.urls"))]
    # Static files
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
