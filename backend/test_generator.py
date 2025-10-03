#!/usr/bin/env python3
"""
Script de prueba para el generador de entidades
Ejecuta el comando de Django para generar entidades desde TypeScript
"""

import os
import sys
import subprocess
from pathlib import Path


def find_virtual_env():
    """Buscar el entorno virtual"""
    backend_path = Path(__file__).parent

    # Buscar en diferentes ubicaciones comunes
    possible_venv_paths = [
        backend_path / "venv",
        backend_path / ".venv",
        backend_path / "env",
        backend_path.parent / "venv",
        backend_path.parent / ".venv",
        backend_path.parent / "env",
    ]

    for venv_path in possible_venv_paths:
        if venv_path.exists():
            # Verificar si tiene la estructura correcta
            if (venv_path / "Scripts" / "python.exe").exists():  # Windows
                return venv_path / "Scripts" / "python.exe"
            elif (venv_path / "bin" / "python").exists():  # Linux/Mac
                return venv_path / "bin" / "python"

    return None


def main():
    # Cambiar al directorio del backend
    backend_path = Path(__file__).parent
    os.chdir(backend_path)

    print("🚀 Ejecutando generador de entidades...")
    print(f"📁 Directorio de trabajo: {backend_path.absolute()}")

    # Buscar entorno virtual
    venv_python = find_virtual_env()

    if venv_python:
        print(f"🐍 Usando entorno virtual: {venv_python}")
        python_executable = str(venv_python)
    else:
        print("⚠️  No se encontró entorno virtual, usando Python del sistema")
        python_executable = sys.executable

    # Construir el comando
    shared_path = "../shared/src"  # Ruta relativa desde backend (un nivel arriba)

    cmd = [
        python_executable,
        "manage.py",
        "generate_entities",
        f"--shared-path={shared_path}",
        "--organized",
        "--dry-run",  # Primero hacer dry-run para ver qué se generaría
    ]

    print(f"📋 Comando: {' '.join(cmd)}")
    print("=" * 60)

    # Ejecutar el comando
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")

        print("STDOUT:")
        print(result.stdout)

        if result.stderr:
            print("\nSTDERR:")
            print(result.stderr)

        print(f"\n🎯 Código de salida: {result.returncode}")

        if result.returncode == 0:
            print("✅ Generación exitosa!")

            # Preguntar si quiere ejecutar sin dry-run
            response = input(
                "\n¿Ejecutar sin --dry-run para generar archivos reales? (y/N): "
            )
            if response.lower() in ["y", "yes", "s", "si"]:
                print("\n🔧 Ejecutando generación real...")
                cmd_real = cmd[:-1]  # Remover --dry-run
                result_real = subprocess.run(
                    cmd_real, capture_output=True, text=True, encoding="utf-8"
                )

                print("STDOUT (Real):")
                print(result_real.stdout)

                if result_real.stderr:
                    print("\nSTDERR (Real):")
                    print(result_real.stderr)

                if result_real.returncode == 0:
                    print("✅ Generación real completada!")
                else:
                    print("❌ Error en la generación real")
        else:
            print("❌ Error en la generación")

    except Exception as e:
        print(f"💥 Error ejecutando comando: {e}")


if __name__ == "__main__":
    main()
