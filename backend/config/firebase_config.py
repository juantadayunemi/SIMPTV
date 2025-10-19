import os
import json
from dotenv import load_dotenv
import firebase_admin
from firebase_admin import credentials, db

# Cargar variables del archivo .env
load_dotenv()


def get_firebase_credentials():
    """Lee las credenciales de Firebase desde variables de entorno"""
    cred_dict = {
        "type": os.getenv("FIREBASE_TYPE"),
        "project_id": os.getenv("FIREBASE_PROJECT_ID"),
        "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
        "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
        "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
        "client_id": os.getenv("FIREBASE_CLIENT_ID"),
        "auth_uri": os.getenv("FIREBASE_AUTH_URI"),
        "token_uri": os.getenv("FIREBASE_TOKEN_URI"),
        "auth_provider_x509_cert_url": os.getenv(
            "FIREBASE_AUTH_PROVIDER_X509_CERT_URL"
        ),
        "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_X509_CERT_URL"),
    }
    return cred_dict


def initialize_firebase():
    """Inicializa Firebase con las credenciales del .env"""
    try:
        # Obtener credenciales
        cred_dict = get_firebase_credentials()

        # Validar que todas las variables existan
        if not all(cred_dict.values()):
            raise ValueError("Faltan variables de entorno de Firebase")

        # Crear credencial
        cred = credentials.Certificate(cred_dict)

        # Inicializar Firebase (si no está ya inicializado)
        if not firebase_admin._apps:
            firebase_admin.initialize_app(
                cred,
                {"databaseURL": f'https://{cred_dict["project_id"]}.firebaseio.com'},
            )

        return firebase_admin.get_app()

    except Exception as e:
        print(f"Error al inicializar Firebase: {e}")
        raise


def get_firebase_app():
    """Retorna la app de Firebase inicializada"""
    try:
        return firebase_admin.get_app()
    except ValueError:
        return initialize_firebase()


def get_firebase_db():
    """Retorna la referencia a la base de datos de Firebase"""
    app = get_firebase_app()
    return db.reference("/", app)


# Inicializar Firebase automáticamente al importar este módulo (solo si no está inicializado)
try:
    get_firebase_app()
    print("✓ Firebase inicializado correctamente (auto)")
except Exception as e:
    print(f"Error al inicializar Firebase automáticamente: {e}")
