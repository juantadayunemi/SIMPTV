# Config Django

# Import Celery app to ensure it's loaded when Django starts
from .celery import app as celery_app
import firebase_admin
from firebase_admin import credentials
import os

__all__ = ("celery_app",)

# Get the directory where this file is located
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Path to service account key
SERVICE_ACCOUNT_PATH = os.path.join(BASE_DIR, 'config', 'firebase-service-account.json')

# Initialize Firebase Admin SDK
if not firebase_admin._apps:
    cred = credentials.Certificate(SERVICE_ACCOUNT_PATH)
    firebase_admin.initialize_app(cred)
    print("✅ Firebase Admin SDK initialized successfully")