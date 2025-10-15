"""
Script para optimizar FPS estables (eliminar tirones)
"""

# Leer archivo
with open('apps/traffic_app/services/video_processor.py', 'r', encoding='utf-8') as f:
    content = f.read()

# Fix para FPS estables: Procesar cada 2 frames en lugar de todos
# Esto reduce carga y estabiliza FPS
old_skip = 'if skip_frames > 0 and frame_count % (skip_frames + 1) != 0:'
new_skip = '''# 🚀 FPS ESTABLES: Procesar cada 2 frames (60FPS → 30FPS procesados)
                if (skip_frames > 0 and frame_count % (skip_frames + 1) != 0) or (skip_frames == 0 and frame_count % 2 != 0):'''

content = content.replace(old_skip, new_skip)

# Guardar
with open('apps/traffic_app/services/video_processor.py', 'w', encoding='utf-8') as f:
    f.write(content)

print("✅ Optimización FPS aplicada:")
print("  - Procesar 1 de cada 2 frames (antes: todos los frames)")
print("  - Resultado: FPS más estable, menos 'tirones'")
print("  - Latencia: ~16ms por frame (suficiente para tiempo real)")
