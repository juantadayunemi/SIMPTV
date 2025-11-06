"""
Script para reparar fcm_service.py eliminando el método corrupto y agregando uno limpio
"""

# Leer archivo hasta línea 245 (antes del método corrupto)
with open("fcm_service.py", "r", encoding="utf-8", errors="ignore") as f:
    lines = f.readlines()

# Tomar solo las primeras 245 líneas (todo antes del método corrupto)
clean_lines = lines[:245]

# Agregar el método correcto con emojis usando códigos Unicode
method_code = '''
    @staticmethod
    def send_vehicle_complaint_alert(
        admin_tokens: List[str],
        plate_number: str,
        owner_name: str,
        complaints_count: int,
        severity: str,
        camera_location: str,
        detection_time: str,
        case_number: str = "N/A",
    ) -> Dict[str, int]:
        """
        Send vehicle complaint/denuncia alert to admins.
        
        Args:
            admin_tokens: List of admin device tokens
            plate_number: License plate number
            owner_name: Vehicle owner name
            complaints_count: Number of complaints
            severity: Severity level (LOW, MEDIUM, HIGH, CRITICAL)
            camera_location: Camera location where detected
            detection_time: Time of detection
            case_number: Case/expediente number
            
        Returns:
            Dictionary with success/failure counts
        """
        # Emoji segun severidad (sin tildes para evitar problemas)
        severity_emoji = {
            'NONE': '✅',
            'LOW': '⚠️',
            'MEDIUM': '🚨',
            'HIGH': '🔴',
            'CRITICAL': '🆘'
        }
        emoji = severity_emoji.get(severity, '🚨')
        
        title = f"{emoji} Vehiculo con Denuncias Detectado"
        body = f"Placa {plate_number} tiene {complaints_count} denuncia(s). Propietario: {owner_name}"

        data = {
            "type": "vehicle_complaint",
            "plate_number": str(plate_number),
            "owner_name": str(owner_name),
            "complaints_count": str(complaints_count),
            "severity": str(severity),
            "case_number": str(case_number),
            "location": str(camera_location),
            "time": str(detection_time),
        }

        return FCMService.send_notification(
            tokens=admin_tokens,
            title=title,
            body=body,
            data=data,
        )
'''

# Escribir el archivo limpio
with open("fcm_service.py", "w", encoding="utf-8") as f:
    f.writelines(clean_lines)
    f.write(method_code)

print("✅ Archivo fcm_service.py reparado exitosamente")
print(f"📝 Total de líneas: {len(clean_lines) + len(method_code.splitlines())}")
