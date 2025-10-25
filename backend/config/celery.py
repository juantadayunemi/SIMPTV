# config/celery.py
import os
from celery import Celery

# Establece el módulo de configuración de Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

app = Celery('config')

# Lee la configuración desde settings.py con el prefijo CELERY_
app.config_from_object('django.conf:settings', namespace='CELERY')

# Autodescubre tareas en todas las apps instaladas
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f'Request: {self.request!r}')