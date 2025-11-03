"""
Script para verificar la configuración de Firebase en backend
"""

import os
from dotenv import load_dotenv

load_dotenv()

print("\n🔍 Verificando configuración de Firebase\n")
print("=" * 60)

# Backend config
backend_project = os.getenv("FIREBASE_PROJECT_ID")
backend_email = os.getenv("FIREBASE_CLIENT_EMAIL")

print(f"\n📦 BACKEND:")
print(f"   Project ID: {backend_project}")
print(f"   Client Email: {backend_email}")

print(f"\n📱 FRONTEND (según .env):")
print(f"   Messaging Sender ID: 134462786929")
print(f"   App ID: 1:134462786929:web:17c2c53227d113c0a53ad0")

print("\n" + "=" * 60)

if backend_project:
    print(f"\n⚠️  PROBLEMA DETECTADO:")
    print(f"   Backend usa proyecto: '{backend_project}'")
    print(f"   Frontend usa proyecto diferente (sender ID: 134462786929)")
    print(f"\n💡 SOLUCIÓN:")
    print(f"   Ambos deben usar el MISMO proyecto de Firebase")
    print(f"\n   Opción A: Actualizar backend para usar proyecto del frontend")
    print(f"   Opción B: Actualizar frontend para usar proyecto '{backend_project}'")
else:
    print("❌ No se encontró FIREBASE_PROJECT_ID en .env del backend")

print("\n")
