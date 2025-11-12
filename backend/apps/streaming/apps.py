"""
Streaming app configuration
"""
from django.apps import AppConfig
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class StreamingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.streaming'
    verbose_name = 'Live Monitoring & Streaming'
    
    def ready(self):
        """
        Auto-create streaming data directories on Django startup
        Separate from video analysis directories to avoid conflicts
        """
        from django.conf import settings
        
        # Create streaming directories (SEPARATE from analysis)
        streaming_dirs = [
            settings.STREAMING_DATA_DIR,      # JSON files
            settings.STREAMING_PLACAS_DIR,    # Vehicle images WITH plates
            settings.STREAMING_ROI_DIR,       # Vehicle images WITHOUT plates
        ]
        
        for directory in streaming_dirs:
            try:
                Path(directory).mkdir(parents=True, exist_ok=True)
                logger.info(f"✅ Streaming directory ready: {directory}")
            except Exception as e:
                logger.error(f"❌ Failed to create streaming directory {directory}: {e}")
