# 🏗️ Arquitectura DLL (Data Layer Library) - TrafiSmart Backend

## 📋 Concepto General

El backend de TrafiSmart utiliza un patrón arquitectónico personalizado llamado **DLL (Data Layer Library)** que permite sincronizar automáticamente los modelos de datos entre TypeScript (frontend/shared) y Python (backend/Django).

## 🔄 Flujo de Trabajo

```
┌─────────────────────────────────────────────────────────────────┐
│                    SHARED LIBRARY (TypeScript)                  │
│                                                                 │
│  shared/src/entities/authEntities.ts                           │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ interface UserEntity {                               │     │
│  │   id: string;                                        │     │
│  │   email: string;                                     │     │
│  │   firstName: string;                                 │     │
│  │   lastName: string;                                  │     │
│  │   phoneNumber?: string;                              │     │
│  │   emailConfirmed: boolean;                           │     │
│  │   isActive: boolean;                                 │     │
│  │   createdAt: Date;                                   │     │
│  │   updatedAt: Date;                                   │     │
│  │ }                                                     │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
                    python manage.py generate_entities
                            ⬇️
┌─────────────────────────────────────────────────────────────────┐
│              ENTITIES APP (Modelos Abstractos DLL)              │
│                                                                 │
│  backend/apps/entities/models/auth.py                          │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ class UserEntity(BaseModel):                         │     │
│  │     """Abstract DLL model from TypeScript"""        │     │
│  │     email = models.EmailField(max_length=255)       │     │
│  │     firstName = models.CharField(max_length=255)    │     │
│  │     lastName = models.CharField(max_length=255)     │     │
│  │     phoneNumber = models.CharField(...)             │     │
│  │     emailConfirmed = models.BooleanField(...)       │     │
│  │                                                      │     │
│  │     class Meta:                                      │     │
│  │         abstract = True  # ← No crea tabla          │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
                         Herencia
                            ⬇️
┌─────────────────────────────────────────────────────────────────┐
│            AUTH_APP (Implementación Concreta)                   │
│                                                                 │
│  backend/apps/auth_app/models.py                               │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ class User(UserEntity):                              │     │
│  │     """Concrete model inheriting from DLL"""        │     │
│  │     # Campos heredados de UserEntity ✅              │     │
│  │                                                      │     │
│  │     # Campos específicos de auth_app                │     │
│  │     last_login = models.DateTimeField(...)          │     │
│  │     failed_login_attempts = models.IntegerField()   │     │
│  │     is_locked_out = models.BooleanField()           │     │
│  │                                                      │     │
│  │     class Meta:                                      │     │
│  │         db_table = "auth_users"  # ← Crea tabla     │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
                            ⬇️
                    python manage.py migrate
                            ⬇️
┌─────────────────────────────────────────────────────────────────┐
│                    BASE DE DATOS                                │
│                                                                 │
│  Tabla: auth_users                                             │
│  ┌──────────────────────────────────────────────────────┐     │
│  │ id (PK)                                              │     │
│  │ email                    ← De UserEntity            │     │
│  │ firstName                ← De UserEntity            │     │
│  │ lastName                 ← De UserEntity            │     │
│  │ phoneNumber              ← De UserEntity            │     │
│  │ emailConfirmed           ← De UserEntity            │     │
│  │ isActive                 ← De BaseModel             │     │
│  │ createdAt                ← De BaseModel             │     │
│  │ updatedAt                ← De BaseModel             │     │
│  │ last_login               ← De User (auth_app)       │     │
│  │ failed_login_attempts    ← De User (auth_app)       │     │
│  │ is_locked_out            ← De User (auth_app)       │     │
│  └──────────────────────────────────────────────────────┘     │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Las 4 Apps del Backend

```
backend/apps/
│
├── 📚 entities/                  # DLL - Modelos Abstractos
│   ├── models/
│   │   ├── base.py              # BaseModel (id, created_at, updated_at, is_active)
│   │   ├── auth.py              # UserEntity, UserRoleEntity, etc.
│   │   ├── traffic.py           # TrafficAnalysisEntity, etc.
│   │   ├── plates.py            # PlateDetectionEntity, etc.
│   │   └── ...
│   ├── constants/
│   │   ├── roles.py             # USER_ROLES_CHOICES
│   │   ├── traffic.py           # DENSITY_LEVELS_CHOICES
│   │   └── ...
│   └── management/commands/
│       └── generate_entities.py # Script generador
│
├── 🔐 auth_app/                  # App 1: Autenticación
│   ├── models.py                # User(UserEntity), UserRole(UserRoleEntity)
│   ├── serializers.py           # Validación y serialización
│   ├── views.py                 # LoginView, RegisterView, etc.
│   ├── urls.py                  # /api/auth/*
│   └── management/commands/
│       └── seed_admin.py        # Crear usuario admin
│
├── 🚗 traffic_app/               # App 2: Análisis de Tráfico
│   ├── models.py                # TrafficAnalysis(TrafficAnalysisEntity)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py                  # /api/traffic/*
│
├── 🔍 plates_app/                # App 3: Detección de Placas
│   ├── models.py                # PlateDetection(PlateDetectionEntity)
│   ├── serializers.py
│   ├── views.py
│   └── urls.py                  # /api/plates/*
│
└── 🌐 external_apis/             # App 4: APIs Externas
    ├── email_service.py         # Gmail SMTP
    ├── sms_service.py           # Twilio (futuro)
    └── ...
```

## 🔧 Script de Generación

**Archivo:** `backend/apps/entities/management/commands/generate_entities.py`

**Funcionalidad:**
1. Lee archivos TypeScript de `shared/src/entities/`
2. Parsea interfaces TypeScript
3. Convierte tipos TS → tipos Django:
   - `string` → `CharField` o `EmailField`
   - `number` → `IntegerField` o `FloatField`
   - `boolean` → `BooleanField`
   - `Date` → `DateTimeField`
   - `enum` → `CharField` con choices
4. Genera clases Python con modelos abstractos
5. Guarda en `apps/entities/models/*.py`

**Comando:**
```bash
python manage.py generate_entities
```

**Ejemplo de salida:**
```
Generando modelos desde TypeScript...
✅ Generado: apps/entities/models/auth.py (7 modelos)
✅ Generado: apps/entities/models/traffic.py (12 modelos)
✅ Generado: apps/entities/models/plates.py (8 modelos)
✅ Total: 27 modelos generados
```

## ✨ Ventajas del Patrón DLL

### 1. **Single Source of Truth**
```typescript
// shared/src/entities/authEntities.ts
interface UserEntity {
    email: string;
    firstName: string;
    lastName: string;
}
```
↓ Auto-generado ↓
```python
# apps/entities/models/auth.py
class UserEntity(BaseModel):
    email = models.EmailField(max_length=255)
    firstName = models.CharField(max_length=255)
    lastName = models.CharField(max_length=255)
```

### 2. **No Duplicación de Código**
- ❌ **Antes**: Definir modelos en TypeScript Y en Python (manualmente)
- ✅ **Ahora**: Definir solo en TypeScript, Python se genera automáticamente

### 3. **Sincronización Automática**
- Cambios en TypeScript → Ejecutar `generate_entities` → Modelos Python actualizados
- No hay inconsistencias entre frontend y backend

### 4. **Tipo-Seguridad en Ambos Lados**
- TypeScript valida en compilación
- Python/Django valida en runtime con modelos ORM

### 5. **Extensibilidad**
Cada app puede agregar campos específicos:
```python
# auth_app/models.py
class User(UserEntity):
    # Campos heredados de UserEntity ✅
    
    # Campos específicos de auth_app
    last_login = models.DateTimeField(null=True)
    failed_login_attempts = models.IntegerField(default=0)
```

## 📊 Comparación: Tradicional vs DLL

### Enfoque Tradicional
```
Developer escribe interface TypeScript
    ↓
Developer escribe modelo Django (manualmente)
    ↓
Developer sincroniza campos a mano
    ↓
❌ Alto riesgo de inconsistencias
❌ Duplicación de código
❌ Mantenimiento tedioso
```

### Enfoque DLL (TrafiSmart)
```
Developer escribe interface TypeScript
    ↓
Script genera modelo Django (automático)
    ↓
Developer hereda y extiende según necesidad
    ↓
✅ Cero inconsistencias
✅ DRY principle
✅ Mantenimiento simplificado
```

## 🚀 Flujo de Desarrollo

### Agregar Nueva Entidad

1. **Definir en TypeScript**
```typescript
// shared/src/entities/vehicleEntities.ts
export interface VehicleEntity {
    id: string;
    plateNumber: string;
    model: string;
    color: string;
    createdAt: Date;
    updatedAt: Date;
}
```

2. **Generar Modelo Python**
```bash
cd backend
python manage.py generate_entities
```

3. **Verificar Generación**
```python
# apps/entities/models/vehicle.py (auto-generado)
class VehicleEntity(BaseModel):
    plateNumber = models.CharField(max_length=255)
    model = models.CharField(max_length=255)
    color = models.CharField(max_length=255)
    
    class Meta:
        abstract = True
```

4. **Usar en App Concreta**
```python
# apps/plates_app/models.py
from apps.entities.models import VehicleEntity

class Vehicle(VehicleEntity):
    # Heredar todos los campos de VehicleEntity
    
    # Agregar campos específicos
    owner_name = models.CharField(max_length=255)
    is_reported = models.BooleanField(default=False)
    
    class Meta:
        db_table = "plates_vehicles"
```

5. **Crear Migración**
```bash
python manage.py makemigrations plates_app
python manage.py migrate
```

## 🎓 Conceptos Clave

### BaseModel
Modelo abstracto base que todos heredan:
```python
class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    class Meta:
        abstract = True
```

### Modelos Abstractos
- `abstract = True` → No crea tabla en BD
- Solo sirven como "plantilla" para heredar
- Definidos en `apps/entities/models/`

### Modelos Concretos
- `abstract = False` (default) → Crea tabla en BD
- Heredan de modelos abstractos
- Definidos en cada app (`auth_app`, `traffic_app`, etc.)

## 📝 Resumen

**El patrón DLL de TrafiSmart:**
1. ✅ Centraliza definiciones de datos en TypeScript (shared)
2. ✅ Genera automáticamente modelos Django abstractos (entities)
3. ✅ Cada app hereda y extiende según necesidad
4. ✅ Mantiene sincronización automática frontend ↔ backend
5. ✅ Reduce errores y acelera desarrollo

**Arquitectura: API REST pura (sin templates, solo JSON)**
- Django REST Framework para APIs
- No usa sistema de templates de Django
- Solo responde JSON (serializers)
- Frontend consume APIs vía Axios

---

✨ **Este patrón es único de TrafiSmart y optimiza el desarrollo full-stack TypeScript + Python!**
