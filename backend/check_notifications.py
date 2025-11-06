#!/usr/bin/env python
"""
Script para verificar notificaciones en la base de datos
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from apps.notifications_app.models import NotificationLog
from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("🔍 VERIFICANDO NOTIFICACIONES EN BASE DE DATOS")
print("=" * 60)

# Total de notificaciones
total_notifications = NotificationLog.objects.count()
print(f"\n📊 Total de notificaciones: {total_notifications}")

# Por usuario
users = User.objects.all()
print(f"\n👥 Usuarios en el sistema: {users.count()}")

for user in users:
    user_notifications = NotificationLog.objects.filter(user=user).count()
    print(f"   - {user.email}: {user_notifications} notificaciones")

    if user_notifications > 0:
        # Mostrar las últimas 3
        recent = NotificationLog.objects.filter(user=user).order_by("-sent_at")[:3]
        print(f"\n   📌 Últimas 3 notificaciones de {user.email}:")
        for notif in recent:
            print(f"      • [{notif.sent_at}] {notif.title}")
            print(f"        Tipo: {notif.notification_type}")
            print(f"        Success: {notif.success}")
            print(f"        Data: {notif.data}")

# Listar todas las notificaciones si hay pocas
if total_notifications > 0 and total_notifications <= 10:
    print(f"\n📋 TODAS LAS NOTIFICACIONES:")
    print("-" * 60)
    for notif in NotificationLog.objects.all().order_by("-sent_at"):
        print(f"ID: {notif.id}")
        print(f"Usuario: {notif.user.email}")
        print(f"Tipo: {notif.notification_type}")
        print(f"Título: {notif.title}")
        print(f"Enviado: {notif.sent_at}")
        print(f"Success: {notif.success}")
        print(f"Data: {notif.data}")
        print("-" * 60)

print("\n✅ Verificación completada")
