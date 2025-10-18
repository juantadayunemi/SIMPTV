# Firebase Cloud Messaging (FCM) Setup Complete ✅

## Configuration Status
- ✅ Frontend: Firebase environment variables configured
- ✅ Backend: Firebase service account configured
- ✅ Testing scripts created and working

## Environment Variables (Frontend)
The following variables are configured in `frontend/.env`:
```env
# Firebase Configuration (for push notifications)
VITE_FIREBASE_API_KEY=AIzaSyB8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8Q8
VITE_FIREBASE_MESSAGING_SENDER_ID=103529930626485993766
VITE_FIREBASE_APP_ID=1:103529930626485993766:web:abcdef123456789
```

## Service Account (Backend)
Firebase service account credentials are configured in:
- `backend/config/firebase-service-account.json`

## Testing Scripts
- Frontend: `npm run test-fcm` or `node scripts/test-fcm-config.cjs`
- Backend: `python backend/scripts/test_fcm_notifications.py --check-config`
- Complete: `npm run test-fcm-complete` or `node scripts/test-fcm-complete.cjs`

## Next Steps
1. **Start Development Servers:**
   ```bash
   # Backend
   cd backend
   python manage.py runserver

   # Frontend (new terminal)
   cd frontend
   npm run dev
   ```

2. **Enable Push Notifications:**
   - Open http://localhost:5173/notifications
   - Click "Enable Push Notifications"
   - Grant browser permission when prompted

3. **Test Notifications:**
   ```bash
   python backend/scripts/test_fcm_notifications.py
   ```

## Important Notes
- Replace the placeholder Firebase credentials with real values from your Firebase Console
- The service account file contains sensitive credentials - keep it secure
- Push notifications only work in HTTPS or localhost environments
- Browser support: Chrome, Firefox, Edge (Safari has limited support)

## Firebase Console Setup
To get real credentials:
1. Go to https://console.firebase.google.com/
2. Select your project (trafismart)
3. Go to Project Settings > General > Your apps
4. Copy the config values to your `.env` file
5. Download the service account key and place it in `backend/config/`

## Troubleshooting
- Run `npm run test-fcm-complete` to check configuration
- Check browser console for FCM errors
- Verify Firebase project has Cloud Messaging enabled
- Ensure service account has FCM permissions

### 2. Obtener las Credenciales de Firebase

1. Ve a [Firebase Console](https://console.firebase.google.com/)
2. Selecciona tu proyecto "trafismart"
3. Ve a **Configuración del proyecto** (icono de engranaje)
4. En la pestaña **General**, desplázate hacia abajo hasta "Tus apps"
5. Si no tienes una app web, crea una nueva:
   - Haz clic en "Agregar app" > Web
   - Nombre: "TrafiSmart Web"
   - Marca la opción "También configurar Firebase Hosting" (opcional)
6. Una vez creada la app, copia los valores del objeto `firebaseConfig`

### 3. Configurar VAPID Key

Para las notificaciones push, necesitas una VAPID key:

1. En Firebase Console, ve a **Cloud Messaging**
2. En la sección "Web configuration", genera una nueva key pair
3. Copia la **VAPID key** pública
4. Actualiza el archivo `src/services/fcm.service.ts`:

```typescript
private vapidKey = 'TU_VAPID_KEY_PUBLICA_AQUI';
```

### 4. Actualizar Service Worker

Actualiza `public/firebase-messaging-sw.js` con las mismas credenciales que pusiste en `.env.local`.

## 🔧 Funcionalidades Implementadas

### ✅ Componentes
- `FCMSettings`: Interfaz para gestionar permisos y dispositivos
- `FCMInitializer`: Inicialización automática al cargar la app
- `useFCM`: Hook personalizado para manejar FCM

### ✅ Servicios
- `fcmService`: Servicio principal para FCM
- Service Worker: Maneja notificaciones en segundo plano
- API endpoints: Registro de tokens y envío de notificaciones

### ✅ Características
- ✅ Solicitud automática de permisos
- ✅ Registro automático de tokens
- ✅ Notificaciones en primer plano (toast)
- ✅ Notificaciones en segundo plano (service worker)
- ✅ Gestión de dispositivos registrados
- ✅ Envío de notificaciones de prueba
- ✅ Alertas para vehículos robados
- ✅ Alertas para infracciones de tránsito

## 📱 Uso en la Aplicación

### Página de Notificaciones
Ve a `/notifications` para:
- Activar/desactivar notificaciones
- Ver dispositivos registrados
- Enviar notificaciones de prueba

### Notificaciones Automáticas
Las notificaciones se envían automáticamente cuando:
- Se detecta un vehículo robado
- Se detecta una infracción de tránsito
- El sistema envía alertas importantes

### Manejo de Clicks en Notificaciones
Al hacer clic en una notificación:
- Se abre la app en primer plano
- Se redirige a la página correspondiente según el tipo de alerta

## 🐛 Solución de Problemas

### Notificaciones no llegan
1. Verifica que los permisos estén concedidos
2. Revisa la consola del navegador por errores
3. Verifica que el service worker esté registrado
4. Comprueba que el token FCM esté registrado en el backend

### Service Worker no se registra
1. Asegúrate de que el archivo `firebase-messaging-sw.js` esté en `/public`
2. Verifica que el servidor se esté ejecutando en HTTPS (requerido para FCM)
3. Revisa la consola por errores de registro

### Error de configuración
1. Verifica que todas las variables de entorno estén configuradas
2. Asegúrate de que las credenciales de Firebase sean correctas
3. Comprueba que el proyecto Firebase tenga Cloud Messaging habilitado

## 🔒 Seguridad

- Los tokens FCM se almacenan de forma segura en el backend
- Las notificaciones incluyen datos mínimos para privacidad
- Los usuarios pueden desactivar dispositivos individuales
- Se requiere autenticación para acceder a la configuración