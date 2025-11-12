# Sistema de Confirmación de Email - Mejoras Implementadas

## 📋 Resumen de Cambios

Se implementaron mejoras en el sistema de autenticación para manejar correctamente la confirmación de email y limpieza automática de usuarios no verificados.

---

## 🔐 1. Login con Email No Confirmado

### ✅ Comportamiento Anterior
- El usuario intentaba iniciar sesión
- Si el email no estaba confirmado, mostraba error
- El usuario debía solicitar manualmente un nuevo link

### ✅ Comportamiento Nuevo
- El usuario intenta iniciar sesión
- Si el email no está confirmado, **automáticamente se envía un nuevo link de confirmación**
- El usuario recibe mensaje: "Tu cuenta aún no ha sido activada. Hemos enviado un nuevo enlace de confirmación a tu correo."

**Archivo modificado:** `backend/apps/auth_app/views.py` - `LoginView.post()`

```python
if not user.emailConfirmed:
    # Reenviar email de confirmación automáticamente
    try:
        token = generate_confirmation_token(user)
        email_sent = send_confirmation_email(user, token)
        print(f"ℹ️ Login intento sin confirmar [{user.email}]: Email reenviado={email_sent}")
    except Exception as e:
        print(f"⚠️ Error reenviando email [{user.email}]: {str(e)}")
        email_sent = False
    
    return Response({
        "error": "Tu cuenta aún no ha sido activada. Hemos enviado un nuevo enlace de confirmación a tu correo.",
        "emailConfirmed": False,
        "email": user.email,
        "emailSent": email_sent,
        "code": "EMAIL_NOT_CONFIRMED",
    }, status=status.HTTP_403_FORBIDDEN)
```

---

## ✉️ 2. Confirmación de Email Activa la Cuenta

### ✅ Comportamiento
Cuando el usuario hace clic en el link de confirmación:
1. Se marca `emailConfirmed = True`
2. Se marca `isActive = True`
3. Se marca el token como usado
4. Se envía email de bienvenida

**Archivo modificado:** `backend/apps/auth_app/views.py` - `ConfirmEmailView.post()`

```python
# Get user and activate account
user = token.user
user.emailConfirmed = True
user.isActive = True
user.save(update_fields=['emailConfirmed', 'isActive', 'updatedAt'])

# Mark token as used
token.mark_as_used()

print(f"✅ Email confirmado exitosamente: {user.email}")
```

---

## 🔑 3. Reset Password También Confirma Email

### ✅ Comportamiento
Cuando el usuario usa el link de "Olvidé mi contraseña":
1. Se actualiza la contraseña
2. **Se confirma el email automáticamente** (`emailConfirmed = True`)
3. **Se activa la cuenta** (`isActive = True`)
4. Se marca el token como usado

**Archivo modificado:** `backend/apps/auth_app/views.py` - `ResetPasswordView.post()`

```python
# Update user password and confirm email
user = token.user
user.passwordHash = make_password(new_password)
user.emailConfirmed = True  # Confirmar email al resetear contraseña
user.isActive = True  # Asegurar que la cuenta esté activa
user.save(update_fields=['passwordHash', 'emailConfirmed', 'isActive', 'updatedAt'])

# Mark token as used
token.mark_as_used()

print(f"✅ Contraseña reseteada y email confirmado: {user.email}")
```

---

## 🗑️ 4. Limpieza Automática de Usuarios No Verificados

### ✅ Problema
Los usuarios que se registran pero nunca confirman su email quedan en la base de datos indefinidamente.

### ✅ Solución
Se implementó un sistema de limpieza automática que elimina usuarios no verificados después de **4 minutos**.

### 📁 Archivos Creados

#### A. Comando Django: `cleanup_unverified_users.py`
**Ubicación:** `backend/apps/auth_app/management/commands/cleanup_unverified_users.py`

**Uso manual:**
```bash
# Eliminar usuarios no verificados después de 4 minutos (default)
python manage.py cleanup_unverified_users

# Simular sin eliminar (dry run)
python manage.py cleanup_unverified_users --dry-run

# Cambiar el tiempo de espera (ejemplo: 10 minutos)
python manage.py cleanup_unverified_users --minutes 10
```

**Funcionalidad:**
- Busca usuarios con `emailConfirmed = False`
- Que fueron creados hace más de 4 minutos
- Los elimina de la base de datos
- Muestra log con emails eliminados

#### B. Tarea Celery: `tasks.py`
**Ubicación:** `backend/apps/auth_app/tasks.py`

```python
@shared_task(name='apps.auth_app.tasks.cleanup_unverified_users_task')
def cleanup_unverified_users_task(minutes=4):
    """
    Tarea Celery para eliminar usuarios no verificados después de X minutos
    """
    # Elimina usuarios no verificados automáticamente
    # Retorna: {'success': True, 'deleted_count': 3, 'deleted_emails': [...]}
```

#### C. Configuración Celery Beat: `settings.py`
**Ubicación:** `backend/config/settings.py`

```python
CELERY_BEAT_SCHEDULE = {
    # ... otras tareas ...
    
    # Limpieza de usuarios no verificados (cada 5 minutos)
    "cleanup-unverified-users": {
        "task": "apps.auth_app.tasks.cleanup_unverified_users_task",
        "schedule": crontab(minute="*/5"),  # Cada 5 minutos
    },
}
```

**Ejecución automática:**
- Se ejecuta **cada 5 minutos**
- Elimina usuarios registrados hace más de **4 minutos** sin confirmar email
- Registra logs en consola de Celery

---

## 🚀 Cómo Usar

### 1. Reiniciar Celery Beat
Para que la tarea de limpieza automática funcione:

```bash
cd backend

# Terminal 1: Celery Worker
celery -A config worker -l info --pool=solo

# Terminal 2: Celery Beat (scheduler)
celery -A config beat -l info
```

### 2. Verificar Logs
Los logs mostrarán la limpieza automática:

```
[INFO] ✓ Cleanup: No hay usuarios no verificados para eliminar.
[INFO] 🗑️ Eliminando 2 usuarios no verificados: test1@example.com, test2@example.com
[INFO] ✅ Eliminados 2 usuarios no verificados.
```

### 3. Ejecutar Manualmente (Testing)
```bash
# Desde backend/ con venv activado
python manage.py cleanup_unverified_users --dry-run

# Output:
# 📋 Usuarios no verificados encontrados: 2
#   - test@example.com (Registrado hace 5 minutos)
#   - user@example.com (Registrado hace 6 minutos)
# ⚠️  DRY RUN: No se eliminaron usuarios
```

---

## 📊 Flujo Completo

### Escenario 1: Usuario se registra y NO confirma email
```
1. Usuario se registra → email_confirmed = False
2. Recibe email con link de confirmación (expira en 3 minutos)
3. ⏰ Después de 4 minutos → Celery elimina el usuario automáticamente
4. Usuario intenta usar el link → Error: "Usuario no encontrado"
```

### Escenario 2: Usuario se registra e intenta login sin confirmar
```
1. Usuario se registra → email_confirmed = False
2. Intenta hacer login
3. ✅ Sistema detecta email no confirmado
4. ✅ Reenvía automáticamente nuevo link de confirmación
5. Usuario recibe: "Hemos enviado un nuevo enlace..."
6. Usuario confirma email → cuenta activada
```

### Escenario 3: Usuario usa "Olvidé mi contraseña"
```
1. Usuario registrado pero email_confirmed = False
2. Usa "Olvidé mi contraseña"
3. Recibe email con link de reset
4. ✅ Al resetear contraseña → email_confirmed = True
5. ✅ Cuenta activada automáticamente
6. Usuario puede iniciar sesión
```

---

## ⚙️ Configuración

### Cambiar Tiempo de Expiración de Tokens

**Email Confirmation Token:**
```python
# backend/apps/auth_app/email_utils.py - generate_confirmation_token()
expiresAt = timezone.now() + timedelta(minutes=3)  # Cambiar aquí
```

**Password Reset Token:**
```python
# backend/apps/auth_app/email_utils.py - generate_password_reset_token()
expiresAt = timezone.now() + timedelta(minutes=2)  # Cambiar aquí
```

### Cambiar Tiempo de Limpieza de Usuarios

**Opción 1: En settings.py (Celery Beat)**
```python
"cleanup-unverified-users": {
    "task": "apps.auth_app.tasks.cleanup_unverified_users_task",
    "schedule": crontab(minute="*/5"),  # Frecuencia de ejecución
    "kwargs": {"minutes": 4},  # Tiempo antes de eliminar
},
```

**Opción 2: En tasks.py (default)**
```python
@shared_task(name='apps.auth_app.tasks.cleanup_unverified_users_task')
def cleanup_unverified_users_task(minutes=4):  # Cambiar default aquí
```

---

## 🧪 Testing

### Probar Limpieza Manual
```bash
# 1. Crear usuario de prueba (sin confirmar email)
python manage.py shell
>>> from apps.auth_app.models import User
>>> User.objects.create_user(email='test@example.com', password='test123', firstName='Test', lastName='User')

# 2. Esperar 4 minutos (o modificar createdAt manualmente)
>>> user = User.objects.get(email='test@example.com')
>>> from django.utils import timezone
>>> from datetime import timedelta
>>> user.createdAt = timezone.now() - timedelta(minutes=5)
>>> user.save()

# 3. Ejecutar limpieza
python manage.py cleanup_unverified_users

# Output: ✅ Eliminados 1 usuarios no verificados.
```

---

## 📝 Notas Importantes

1. **Los tokens de confirmación expiran en 3 minutos** pero el usuario se elimina después de 4 minutos del registro
2. **Celery Beat debe estar corriendo** para que la limpieza automática funcione
3. **Los logs se muestran en la consola de Celery Worker**
4. **El sistema es compatible con el modelo UserEntity existente**
5. **No afecta a usuarios ya verificados**

---

## 🔍 Verificación

### Verificar que Celery Beat está configurado:
```bash
celery -A config inspect scheduled
```

### Verificar última ejecución de la tarea:
```bash
# En Django shell
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> task = PeriodicTask.objects.get(name='cleanup-unverified-users')
>>> print(f"Última ejecución: {task.last_run_at}")
```

---

## ✅ Checklist de Implementación

- [x] LoginView reenvía email automáticamente si no está confirmado
- [x] ConfirmEmailView activa cuenta (`emailConfirmed=True`, `isActive=True`)
- [x] ResetPasswordView confirma email al resetear contraseña
- [x] Comando Django `cleanup_unverified_users` creado
- [x] Tarea Celery `cleanup_unverified_users_task` creada
- [x] Configuración Celery Beat añadida a `settings.py`
- [x] Logs informativos en todas las operaciones

---

**Fecha de implementación:** 12 de noviembre, 2025
**Desarrollador:** GitHub Copilot
**Versión:** 1.0
