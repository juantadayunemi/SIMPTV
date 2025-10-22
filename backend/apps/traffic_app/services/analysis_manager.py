"""
Analysis Manager - Control de análisis concurrentes
Gestiona múltiples procesos de análisis de video para evitar interferencias

PROBLEMA RESUELTO:
- Cuando se cargan videos en múltiples cámaras, todos los hilos se ejecutan simultáneamente
- Esto causa saturación de CPU/GPU y frames salteados
- Al cambiar de cámara, el análisis anterior sigue corriendo en background

SOLUCIÓN:
- Solo UN análisis activo a la vez
- Al iniciar nuevo análisis, pausar/detener los anteriores automáticamente
- Sistema de stop_flag para detener hilos limpiamente
"""

import threading
from typing import Dict, Optional
from datetime import datetime


class AnalysisControl:
    """Control de un análisis individual"""
    
    def __init__(self, analysis_id: int):
        self.analysis_id = analysis_id
        self.thread: Optional[threading.Thread] = None
        self.stop_flag = threading.Event()  # Flag para detener el hilo
        self.started_at = datetime.now()
        self.is_active = True
        
    def request_stop(self):
        """Solicita detener el procesamiento"""
        print(f"🛑 Solicitando detener análisis {self.analysis_id}")
        self.stop_flag.set()
        self.is_active = False
        
    def should_stop(self) -> bool:
        """Verifica si se debe detener el procesamiento"""
        return self.stop_flag.is_set()


class AnalysisManager:
    """
    Manager global de análisis en ejecución
    Singleton para coordinar todos los análisis
    """
    
    _instance: Optional['AnalysisManager'] = None
    _lock = threading.Lock()
    
    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        if self._initialized:
            return
            
        self.active_analyses: Dict[int, AnalysisControl] = {}
        self.analyses_lock = threading.Lock()
        self._initialized = True
        print("🎬 AnalysisManager inicializado")
    
    def start_analysis(self, analysis_id: int, thread: threading.Thread) -> AnalysisControl:
        """
        Registra un nuevo análisis y DETIENE todos los demás
        
        Args:
            analysis_id: ID del análisis a iniciar
            thread: Thread del procesamiento
            
        Returns:
            AnalysisControl para este análisis
        """
        with self.analyses_lock:
            # 🛑 DETENER TODOS LOS ANÁLISIS ANTERIORES (solo uno activo a la vez)
            if self.active_analyses:
                print(f"\n🛑 Deteniendo {len(self.active_analyses)} análisis anteriores:")
                for old_id, control in list(self.active_analyses.items()):
                    print(f"   ⏹️  Análisis {old_id} → stop_flag.set()")
                    control.request_stop()
                    
                # Limpiar análisis detenidos
                self.active_analyses.clear()
            
            # Registrar nuevo análisis
            control = AnalysisControl(analysis_id)
            control.thread = thread
            self.active_analyses[analysis_id] = control
            
            print(f"✅ Análisis {analysis_id} registrado como ÚNICO activo")
            return control
    
    def get_analysis(self, analysis_id: int) -> Optional[AnalysisControl]:
        """Obtiene el control de un análisis"""
        with self.analyses_lock:
            return self.active_analyses.get(analysis_id)
    
    def stop_analysis(self, analysis_id: int):
        """Detiene un análisis específico"""
        with self.analyses_lock:
            control = self.active_analyses.get(analysis_id)
            if control:
                print(f"🛑 Deteniendo análisis {analysis_id}")
                control.request_stop()
                del self.active_analyses[analysis_id]
    
    def complete_analysis(self, analysis_id: int):
        """Marca un análisis como completado y lo elimina del registro"""
        with self.analyses_lock:
            if analysis_id in self.active_analyses:
                print(f"✅ Análisis {analysis_id} completado, removido del registro")
                del self.active_analyses[analysis_id]
    
    def get_active_count(self) -> int:
        """Retorna el número de análisis activos"""
        with self.analyses_lock:
            return len(self.active_analyses)
    
    def get_active_ids(self) -> list[int]:
        """Retorna IDs de análisis activos"""
        with self.analyses_lock:
            return list(self.active_analyses.keys())


# Singleton global
_manager_instance = None

def get_analysis_manager() -> AnalysisManager:
    """Obtiene la instancia global del AnalysisManager"""
    global _manager_instance
    if _manager_instance is None:
        _manager_instance = AnalysisManager()
    return _manager_instance
