# 🚀 Comandos Rápidos - TrafiSmart

## 📋 Setup Inicial

```bash
# 1. Clonar repositorio
git clone https://github.com/juantadayunemi/SIMPTV.git
cd SIMPTV

# 2. Instalar dependencias
npm run install:all

# 3. Build shared library
npm run build:shared

# 4. Generar modelos Django desde TypeScript
cd backend
python manage.py generate_entities

# 5. Configurar base de datos
python manage.py makemigrations
python manage.py migrate

# 6. Crear usuario administrador
python manage.py seed_admin
# Email: admin@gmail.com
# Password: admin123

# 7. Configurar Gmail (para emails de confirmación)
# Editar backend/.env con tu Gmail App Password
```

## 🛠️ Desarrollo Diario

### Iniciar Servidores
```bash
# Terminal 1: Backend (puerto 8000)
cd backend
python manage.py runserver

# Terminal 2: Frontend (puerto 5173)
cd frontend
npm run dev

# O desde raíz con npm scripts
npm run dev:backend
npm run dev:frontend
```

### Actualizar Modelos
```bash
# 1. Editar interfaces en shared/src/entities/
# 2. Regenerar modelos Django
cd backend
python manage.py generate_entities

# 3. Crear y aplicar migraciones
python manage.py makemigrations
python manage.py migrate
```

## 🔧 Base de Datos

### Migraciones
```bash
cd backend

# Crear migraciones
python manage.py makemigrations

# Ver SQL de migraciones
python manage.py sqlmigrate auth_app 0001

# Aplicar migraciones
python manage.py migrate

# Revertir migración
python manage.py migrate auth_app 0001

# Ver estado de migraciones
python manage.py showmigrations
```

### Reset Completo
```bash
cd backend

# Borrar base de datos SQLite (desarrollo)
del db.sqlite3

# Borrar todas las migraciones (excepto __init__.py)
# Hacerlo manualmente o con script

# Regenerar todo
python manage.py generate_entities
python manage.py makemigrations
python manage.py migrate
python manage.py seed_admin
```

### Datos de Prueba
```bash
# Crear usuario admin
python manage.py seed_admin

# Shell interactivo de Django
python manage.py shell

# Ejecutar script Python
python manage.py shell < scripts/load_data.py
```

## 📦 Build y Producción

```bash
# Build shared library
cd shared
npm run build

# Build frontend
cd frontend
npm run build
# Output: dist/

# Desde raíz
npm run build:all
```

## 🧪 Testing

```bash
# Backend tests (pytest)
cd backend
pytest

# Frontend tests (vitest - futuro)
cd frontend
npm test
```

## 🔍 Debugging

### Django Shell
```bash
cd backend
python manage.py shell

>>> from apps.auth_app.models import User
>>> User.objects.all()
>>> user = User.objects.get(email='admin@gmail.com')
>>> user.emailConfirmed
```

### Ver Queries SQL
```python
# En views.py temporalmente
from django.db import connection
print(connection.queries)
```

### Debug Mode
```bash
# backend/.env
DEBUG=True
```

## 📝 Linting y Formateo

```bash
# Python (black, flake8)
cd backend
black .
flake8 .

# TypeScript/React (ESLint)
cd frontend
npm run lint
```

## 🌐 URLs Importantes

```
Frontend Dev:    http://localhost:5173
Backend API:     http://localhost:8000/api
Django Admin:    http://localhost:8000/admin
API Docs:        http://localhost:8000/api/schema/swagger-ui/
API Schema:      http://localhost:8000/api/schema/
```

## 📧 Configurar Gmail SMTP

1. **Activar verificación en 2 pasos**
   - https://myaccount.google.com/security

2. **Generar App Password**
   - https://myaccount.google.com/apppasswords
   - Seleccionar "Mail" > "Otro" > "TrafiSmart"
   - Copiar contraseña de 16 caracteres

3. **Editar backend/.env**
```env
EMAIL_HOST_USER=tu-correo@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
```

## 🐛 Solución de Problemas

### Error: "Token expired"
```bash
# Usuario no puede hacer login
# Solución: Confirmar email primero
# Reenviar email de confirmación desde API
POST /api/auth/resend-confirmation/
{
  "email": "user@example.com"
}
```

### Error: "Module not found: @traffic-analysis/shared"
```bash
# Shared no compilado
cd shared
npm run build

# Reinstalar en frontend
cd ../frontend
npm install
```

### Error: Migration conflicts
```bash
cd backend

# Ver estado
python manage.py showmigrations

# Hacer fake migration
python manage.py migrate --fake auth_app 0001

# O borrar todo y empezar de nuevo (solo desarrollo)
del db.sqlite3
# Borrar carpetas migrations (excepto __init__.py)
python manage.py makemigrations
python manage.py migrate
```

### Error: Port already in use
```bash
# Backend (8000)
# Windows
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:8000 | xargs kill -9

# Frontend (5173)
# Windows
netstat -ano | findstr :5173
taskkill /PID <PID> /F

# Linux/Mac
lsof -ti:5173 | xargs kill -9
```

## 📊 Comandos SQL Útiles

### SQLite (Desarrollo)
```bash
# Abrir BD
sqlite3 backend/db.sqlite3

# Ver tablas
.tables

# Ver estructura
.schema auth_users

# Query
SELECT * FROM auth_users;

# Salir
.exit
```

### SQL Server (Producción)
```sql
-- Ver tablas
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES;

-- Ver usuarios
SELECT * FROM auth_users;

-- Contar registros
SELECT COUNT(*) FROM auth_users;
```

## 🔐 Gestión de Usuarios

```bash
cd backend
python manage.py shell

>>> from apps.auth_app.models import User

# Crear usuario
>>> user = User.objects.create(
...     email='nuevo@example.com',
...     firstName='Nuevo',
...     lastName='Usuario',
...     emailConfirmed=True,
...     is_active=True
... )
>>> user.set_password('password123')
>>> user.save()

# Cambiar contraseña
>>> user = User.objects.get(email='admin@gmail.com')
>>> user.set_password('nueva_password')
>>> user.save()

# Activar cuenta
>>> user = User.objects.get(email='user@example.com')
>>> user.emailConfirmed = True
>>> user.is_active = True
>>> user.save()
```

## 📈 Monitoreo

### Logs
```bash
# Ver logs en tiempo real
cd backend
tail -f logs/django.log

# En Windows
powershell Get-Content logs/django.log -Wait -Tail 50
```

### Performance
```python
# En settings.py (desarrollo)
DEBUG_TOOLBAR_CONFIG = {
    'SHOW_TOOLBAR_CALLBACK': lambda request: True,
}
```

## 🚀 Deploy (Futuro)

```bash
# Collectstatic
python manage.py collectstatic

# Gunicorn
gunicorn config.wsgi:application --bind 0.0.0.0:8000

# Con Docker
docker-compose up -d
```

---

💡 **Tip**: Guarda este archivo en favoritos para acceso rápido!
