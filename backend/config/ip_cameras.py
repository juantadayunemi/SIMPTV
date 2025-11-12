"""
IP Camera Configuration
Central configuration for IP cameras in the system

DroidCam USB:
- Se conecta como dispositivo USB virtual
- No requiere configuración de IP
- Aparece como "DroidCam Video" en la lista de cámaras
"""

# DroidCam (USB Connection) - Recomendada
IP_CAMERAS = [
    {
        "id": "droidcam-usb",
        "name": "📱 DroidCam - USB",
        "url": "N/A",  # USB device, no URL needed
        "type": "droidcam",
        "enabled": True,
        "notes": "App DroidCam conectada via USB - No requiere WiFi"
    },
    # Add more IP cameras here
    # {
    #     "id": "ip-camera-2",
    #     "name": "📱 Cámara IP - Tablet",
    #     "url": "http://192.168.1.10:8080/video",
    #     "type": "ip_webcam",
    #     "enabled": True
    # }
]

# RTSP Cameras (for future support)
RTSP_CAMERAS = [
    # {
    #     "id": "rtsp-cam-1",
    #     "name": "🎥 Cámara RTSP - Entrada",
    #     "url": "rtsp://admin:password@192.168.1.20:554/stream1",
    #     "type": "rtsp",
    #     "enabled": False
    # }
]

def get_enabled_ip_cameras():
    """Get list of enabled IP cameras"""
    return [cam for cam in IP_CAMERAS if cam.get("enabled", False)]

def get_camera_by_id(camera_id: str):
    """Get camera configuration by ID"""
    for cam in IP_CAMERAS:
        if cam["id"] == camera_id:
            return cam
    return None
