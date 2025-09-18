"""
Development settings for Urbia Traffic Analysis project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True

ALLOWED_HOSTS = ["*"]

# Development apps
INSTALLED_APPS += [
    "django_extensions",
]

# Database configuration inherited from base.py
# Using SQL Server for development as specified in .env

# CORS settings for development
CORS_ALLOW_ALL_ORIGINS = True

# Email backend for development (console)
EMAIL_BACKEND = "django.core.mail.backends.console.EmailBackend"

# Disable caching in development
CACHES = {
    "default": {
        "BACKEND": "django.core.cache.backends.dummy.DummyCache",
    }
}

# Logging for development
LOGGING["root"]["level"] = "DEBUG"
LOGGING["loggers"]["django"]["level"] = "DEBUG"