"""
Production settings for Urbia Traffic Analysis project.
"""

from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

ALLOWED_HOSTS = config(
    "ALLOWED_HOSTS",
    default="yourdomain.com",
    cast=lambda v: [s.strip() for s in v.split(",")],
)

# Database - SQL Server for production
DATABASES = {
    "default": {
        "ENGINE": "mssql",
        "NAME": config("DB_NAME"),
        "USER": config("DB_USER"),
        "PASSWORD": config("DB_PASSWORD"),
        "HOST": config("DB_HOST"),
        "PORT": config("DB_PORT", default="1433"),
        "OPTIONS": {
            "driver": "ODBC Driver 17 for SQL Server",
            "extra_params": "TrustServerCertificate=yes;",
        },
    }
}

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = "DENY"

# Email settings
EMAIL_BACKEND = "django.core.mail.backends.smtp.EmailBackend"
EMAIL_HOST = config("EMAIL_HOST", default="smtp.gmail.com")
EMAIL_PORT = config("EMAIL_PORT", default=587, cast=int)
EMAIL_USE_TLS = config("EMAIL_USE_TLS", default=True, cast=bool)
EMAIL_HOST_USER = config("EMAIL_HOST_USER", default="")
EMAIL_HOST_PASSWORD = config("EMAIL_HOST_PASSWORD", default="")

# Static files (CSS, JavaScript, Images)
STATIC_ROOT = os.path.join(BASE_DIR, "staticfiles")

# Logging for production
LOGGING["handlers"]["file"]["level"] = "ERROR"
LOGGING["root"]["level"] = "WARNING"