# Config Django

# Import Celery app to ensure it's loaded when Django starts
from .celery import app as celery_app
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db, messaging

import os

__all__ = ("celery_app",)

# Cargar variables de entorno
load_dotenv()

def initialize_firebase():
    """
    Inicializa Firebase usando credenciales del .env
    (Sin necesidad de archivo JSON)
    """
    try:
        # Verificar si ya está inicializado
        if firebase_admin._apps:
            return firebase_admin.get_app()
        
        # Crear credencial desde variables de entorno
        firebase_config = {
            "type": os.getenv("FIREBASE_TYPE", "service_account"),
            "project_id": os.getenv("FIREBASE_PROJECT_ID"),
            "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
            "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
            "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
            "client_id": os.getenv("FIREBASE_CLIENT_ID"),
            "auth_uri": os.getenv("FIREBASE_AUTH_URI", "https://accounts.google.com/o/oauth2/auth"),
            "token_uri": os.getenv("FIREBASE_TOKEN_URI", "https://oauth2.googleapis.com/token"),
            "auth_provider_x509_cert_url": os.getenv("FIREBASE_AUTH_PROVIDER_X509_CERT_URL",
                                                      "https://www.googleapis.com/oauth2/v1/certs"),
            "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
        }
        
        # Validar que existan credenciales
        if not firebase_config.get("project_id") or not firebase_config.get("private_key"):
            raise ValueError(
                "Firebase credentials not configured. "
                "Please add FIREBASE_* variables to your .env file"
            )
        
        # Inicializar Firebase Admin SDK
        cred = credentials.Certificate(firebase_config)
        app = firebase_admin.initialize_app(cred, {
            'databaseURL': f'https://{firebase_config["project_id"]}.firebaseio.com'
        })
        
        return app
    
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        raise
    except Exception as e:
        print(f"❌ Firebase initialization error: {e}")
        raise


def get_firebase_app():
    """Retorna la app de Firebase inicializada"""
    try:
        return firebase_admin.get_app()
    except ValueError:
        return initialize_firebase()


def get_firebase_db():
    """Retorna la referencia a la base de datos Realtime de Firebase"""
    app = get_firebase_app()
    return db.reference('/', app)


def send_notification(title, body, token):
    """
    Envía una notificación FCM a un dispositivo
    
    Args:
        title: Título de la notificación
        body: Cuerpo del mensaje
        token: Token del dispositivo
    """
    try:
        message = messaging.Message(
            notification=messaging.Notification(
                title=title,
                body=body
            ),
            token=token
        )
        response = messaging.send(message)
        print(f"✓ Notificación enviada: {response}")
        return response
    except Exception as e:
        print(f"❌ Error al enviar notificación: {e}")
        raise