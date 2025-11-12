"""
REST API URL routing for streaming app
"""
from django.urls import path
from . import views

app_name = 'streaming'

urlpatterns = [
    # Camera management
    path('cameras/', views.list_cameras, name='list_cameras'),
    path('cameras/create/', views.create_camera, name='create_camera'),
    path('cameras/<str:camera_id>/', views.get_camera, name='get_camera'),
    
    # Stream control
    path('stream/start/', views.start_stream, name='start_stream'),
    path('stream/stop/', views.stop_stream, name='stop_stream'),
    path('stream/status/<str:camera_id>/', views.stream_status, name='stream_status'),
    
    # Recordings - ORDEN IMPORTANTE: rutas específicas primero
    path('recordings/start/', views.start_recording, name='start_recording'),
    path('recordings/<str:recording_id>/upload/', views.upload_recording, name='upload_recording'),
    path('recordings/<str:recording_id>/finalize/', views.finalize_recording, name='finalize_recording'),
    path('recordings/<str:recording_id>/delete/', views.delete_recording, name='delete_recording'),
    path('recordings/<str:recording_id>/', views.get_recording, name='get_recording'),
    path('recordings/', views.list_recordings, name='list_recordings'),
    
    # System
    path('system/active-streams/', views.active_streams, name='active_streams'),
    
    # Frame processing (for webcam)
    path('process-frame/', views.process_frame, name='process_frame'),
    
    # Detection sessions
    path('detection-sessions/start/', views.start_detection_session, name='start_detection_session'),
    path('detection-sessions/save-detection/', views.save_detection, name='save_detection'),
    path('detection-sessions/finalize/', views.finalize_detection_session, name='finalize_detection_session'),
    
    # IP Camera configuration
    path('update-ip-camera/', views.update_ip_camera_config, name='update_ip_camera'),
    
    # YOLO Processor session management (for JSON export)
    path('processor-session/start/', views.start_processor_session, name='start_processor_session'),
    path('processor-session/end/', views.end_processor_session, name='end_processor_session'),
]
