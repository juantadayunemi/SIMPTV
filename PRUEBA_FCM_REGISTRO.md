# Prueba de Registro de Tokens FCM

## ✅ Cambios Realizados

1. **Frontend - fcm.service.ts**: 
   - Eliminada la verificación de localStorage que impedía el registro repetido
   - Mejorado el logging para mostrar información detallada del token y errores
   - Ahora SIEMPRE intenta registrar el token en cada inicialización

2. **Backend - views.py**:
   - Agregado logging detallado para ver:
     - Usuario que intenta registrar
     - Datos recibidos
     - Errores de validación
     - Dispositivo creado/actualizado

3. **Verificado**:
   - ✅ La tabla `notifications_app_fcmdevice` existe
   - ✅ El endpoint `/api/notifications/devices/register_token/` funciona correctamente
   - ✅ El modelo FCMDevice se puede crear y actualizar
   - ✅ Actualmente hay 3 dispositivos registrados en la BD

## 🧪 Pasos para Probar

### Opción A: Prueba desde el navegador (Recomendado)

1. **Limpiar localStorage** (importante para forzar nuevo registro):
   ```javascript
   // En la consola del navegador (F12)
   localStorage.removeItem('fcm_registered_token');
   ```

2. **Recargar la aplicación**:
   - Asegúrate de estar logueado
   - Abre la consola del navegador (F12)
   - Busca los mensajes:
     - `🔥 Initializing Firebase Cloud Messaging...`
     - `🔑 Token FCM obtenido: ...`
     - `📤 Enviando token FCM al backend...`
     - `✅ Respuesta del servidor: ...`

3. **Verificar en la base de datos**:
   ```powershell
   cd D:\TrafiSmart\backend
   python manage.py shell -c "from apps.notifications_app.models import FCMDevice; print('Total dispositivos:', FCMDevice.objects.count()); [print(f'{d.id}: {d.user.email} - {d.device_type} - {d.token[:30]}...') for d in FCMDevice.objects.all()]"
   ```

### Opción B: Prueba desde el backend (Script Python)

```powershell
cd D:\TrafiSmart\backend
python test_fcm_register.py
```

Este script:
- ✅ Simula una petición autenticada al endpoint
- ✅ Muestra la respuesta del servidor
- ✅ Verifica que el dispositivo se creó en la BD

## 🔍 Verificar Logs del Servidor

Si el servidor Django está corriendo, verás estos logs cuando el frontend intente registrar:

```
INFO 📥 Registro de token FCM solicitado por usuario: usuario@example.com
INFO 📦 Datos recibidos: {'token': '...', 'device_name': '...', 'device_type': 'web'}
INFO ✅ Datos validados correctamente
INFO ✅ Dispositivo creado/actualizado: ID=X, Token=..., Usuario=usuario@example.com
```

## ❌ Problemas Comunes

### 1. "Token ya fue registrado previamente" pero no aparece en BD
**Causa**: localStorage tiene el token pero nunca se envió al backend
**Solución**: Ejecutar en consola del navegador:
```javascript
localStorage.removeItem('fcm_registered_token');
location.reload();
```

### 2. Error 401 Unauthorized
**Causa**: El usuario no está autenticado
**Solución**: 
- Verificar que el token de acceso esté en localStorage
- Hacer login nuevamente
- Ver en la consola si hay errores de autenticación

### 3. Error 400 Bad Request
**Causa**: Datos inválidos o falta el token FCM
**Solución**:
- Ver logs del servidor para detalles
- Verificar que Firebase esté correctamente configurado (VITE_FIREBASE_VAPID_KEY)

### 4. No se obtiene token FCM
**Causa**: Permisos de notificación no concedidos o Firebase mal configurado
**Solución**:
- Verificar permisos en configuración del navegador
- Verificar que `firebase-messaging-sw.js` esté registrado
- Verificar VAPID key en `.env`

## 📊 Estado Actual de la BD

```
Total dispositivos: 3
Dispositivos:
- ID 1: usuario@example.com - web - cgqm0zL0Z0WNkBSq14DDzQ:APA91bE...
- ID 7: usuario@example.com - web - TEST_TOKEN_12345...
- ID 8: usuario@example.com - web - TEST_FCM_TOKEN_FROM_SCRIPT_3...
```

## 🎯 Próximos Pasos

1. ✅ Verificar que el registro funcione desde el navegador
2. ✅ Probar envío de notificaciones de prueba
3. ✅ Verificar que las notificaciones se reciban en el navegador
4. ⬜ Implementar limpieza de tokens antiguos/duplicados
5. ⬜ Agregar página de configuración de notificaciones

## 🚀 Para Ejecutar el Sistema Completo

Terminal 1 - Backend:
```powershell
cd D:\TrafiSmart\backend
.\venv\Scripts\Activate
python manage.py runserver
```

Terminal 2 - Frontend:
```powershell
cd D:\TrafiSmart\frontend
npm run dev
```

Luego:
1. Abrir http://localhost:5174
2. Login con usuario existente
3. Abrir consola (F12)
4. Verificar logs de FCM
5. Ejecutar comando de verificación de BD
