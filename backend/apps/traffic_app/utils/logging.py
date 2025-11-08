import logging
import os
from django.conf import settings
from logging.handlers import RotatingFileHandler

def setup_logger(name, log_file=None, level=logging.INFO):
    """
    Configura un logger centralizado para toda la aplicación
    
    Args:
        name: Nombre del logger (ej: 'traffic_analyzer')
        log_file: Nombre del archivo de log (si es None, usa carpeta por defecto)
        level: Nivel de logging (INFO, DEBUG, WARNING, ERROR)
    
    Returns:
        logging.Logger: Instancia configurada del logger
    """
    # Crear directorio de logs si no existe
    log_dir = os.path.join(settings.BASE_DIR, 'logs')
    os.makedirs(log_dir, exist_ok=True)
    
    # Determinar nombre del archivo si no se proporcionó
    if log_file is None:
        log_file = f"{name.replace('.', '_')}.log"
    
    # Ruta completa del archivo de log
    log_path = os.path.join(log_dir, log_file)
    
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # Evitar duplicar handlers si el logger ya está configurado
    if logger.hasHandlers():
        return logger
    
    # Formato de logs
    formatter = logging.Formatter(
        '%(asctime)s | %(threadName)-12s | %(levelname)-8s | %(name)-15s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler para archivo (con rotación)
    file_handler = RotatingFileHandler(
        log_path,
        maxBytes=10 * 1024 * 1024,  # 10 MB
        backupCount=5,
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    # Logger de inicialización
    logger.info(f"✅ Logger '{name}' inicializado correctamente")
    logger.info(f"📁 Archivo de logs: {log_path}")
    
    return logger