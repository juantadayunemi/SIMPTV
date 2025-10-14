"""
Script para resetear análisis a estado PENDING
Útil cuando un análisis queda atascado en PROCESSING
"""

import sys
import os
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.traffic_app.models import TrafficAnalysis

def reset_analysis(analysis_id):
    """Reset análisis a PENDING - más robusto"""
    try:
        analysis = TrafficAnalysis.objects.get(pk=analysis_id)
        
        print("=" * 60)
        print(f"� RESETEANDO ANÁLISIS ID: {analysis_id}")
        print(f"   Estado actual: {analysis.status}")
        print(f"   isPlaying: {analysis.isPlaying}")
        print(f"   isPaused: {analysis.isPaused}")
        print(f"   currentTimestamp: {analysis.currentTimestamp}")
        print("=" * 60)
        
        # Resetear TODOS los campos relevantes
        analysis.status = "PENDING"
        analysis.isPlaying = False
        analysis.isPaused = False
        analysis.currentTimestamp = 0
        
        # Guardar con actualización explícita
        analysis.save(update_fields=[
            "status", 
            "isPlaying", 
            "isPaused", 
            "currentTimestamp"
        ])
        
        # Verificar que se guardó correctamente
        analysis.refresh_from_db()
        print(f"✅ Análisis {analysis_id} reseteado exitosamente")
        print(f"   Nuevo estado: {analysis.status}")
        print(f"   isPlaying: {analysis.isPlaying}")
        print(f"   isPaused: {analysis.isPaused}")
        print("=" * 60)
        
    except TrafficAnalysis.DoesNotExist:
        print(f"❌ Análisis {analysis_id} no existe")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error reseteando: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Uso: python reset_analysis.py <analysis_id>")
        print("Ejemplo: python reset_analysis.py 4")
        sys.exit(1)
    
    analysis_id = int(sys.argv[1])
    reset_analysis(analysis_id)
