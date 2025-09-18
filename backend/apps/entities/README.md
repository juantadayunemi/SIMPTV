# ENTITIES - Shared Models Library (DLL)

Esta app funciona como una librería de modelos compartidos que se generan automáticamente desde archivos TypeScript.

## 📁 Estructura

```
entities/
├── __init__.py              # Configuración como DLL
├── apps.py                  ## 🔧 Configuración

### 📋 Estructura organizada (--organized)
- **Modelos abstractos**: Los modelos generados son `abstract = True`
- **Sin tablas DB**: Los modelos DLL no crean tablas - solo definen estructura
- **Imports organizados**: `from entities.models.auth import UserEntity`
- **Campos base**: Todos heredan `created_at`, `updated_at`, `is_active`
- **Constantes separadas**: `from entities.constants.roles import USER_ROLES_CHOICES`

### 📄 Estructura simple (modo anterior)
- **Modelos concretos**: Genera archivo único `models.py`
- **Tabla prefix**: `entities_` (ej: `entities_userentity`)  
- **Import simple**: `from entities.models import UserEntity`iguración de Django app
├── models/                  # 🆕 Modelos organizados por categoría
│   ├── __init__.py          # Importa todos los modelos
│   ├── base.py              # BaseModel abstracto
│   ├── auth.py              # UserEntity, UserRoleEntity
│   ├── traffic.py           # TrafficAnalysisEntity, VehicleDetectionEntity
│   ├── plates.py            # PlateDetectionEntity, PlateAnalysisEntity
│   ├── predictions.py       # Modelos de ML y predicciones
│   ├── notifications.py     # NotificationEntity, NotificationSettingsEntity
│   └── common.py            # WeatherDataEntity, EventDataEntity
├── constants/               # 🆕 Constantes organizadas por categoría
│   ├── __init__.py          # Importa todas las constantes
│   ├── roles.py             # USER_ROLES, PERMISSIONS + _CHOICES
│   ├── traffic.py           # VEHICLE_TYPES, ANALYSIS_STATUS + _CHOICES
│   ├── notifications.py     # NOTIFICATION_TYPES + _CHOICES
│   └── common.py            # DataTypeKey, API_ENDPOINTS + _CHOICES
├── models.py                # 📄 Archivo único (modo anterior)
├── migrations/              # Migraciones de Django
└── management/
    └── commands/
        └── generate_entities.py  # Comando para generar modelos
```

## 🚀 Uso en otras apps

### 📦 Importación (Estructura Organizada)

```python
# Opción 1: Importar desde categorías específicas
from apps.entities.models.auth import UserEntity, UserRoleEntity
from apps.entities.models.traffic import TrafficAnalysisEntity, VehicleDetectionEntity
from apps.entities.constants.roles import USER_ROLES_CHOICES, PERMISSIONS
from apps.entities.constants.traffic import VEHICLE_TYPES_CHOICES, ANALYSIS_STATUS_CHOICES

# Opción 2: Importar desde __init__.py (más limpio)
from apps.entities.models import UserEntity, TrafficAnalysisEntity, VehicleDetectionEntity
from apps.entities.constants import USER_ROLES_CHOICES, VEHICLE_TYPES_CHOICES
```

### 🏗️ Ejemplo de uso en otras apps

```python
# apps/auth_module/models.py
from apps.entities.models.auth import UserEntity
from apps.entities.constants.roles import USER_ROLES_CHOICES

class User(UserEntity):
    """Concrete user model inheriting from entities DLL"""
    
    # Override role field to use choices
    role = models.CharField(max_length=50, choices=USER_ROLES_CHOICES, default="VIEWER")
    
    # Add app-specific fields
    last_login_ip = models.GenericIPAddressField(null=True)
    
    class Meta:
        db_table = "auth_users"
        verbose_name = "User"

# apps/traffic_module/models.py
from apps.entities.models.traffic import TrafficAnalysisEntity
from apps.entities.constants.traffic import ANALYSIS_STATUS_CHOICES, VEHICLE_TYPES_CHOICES

class TrafficAnalysis(TrafficAnalysisEntity):
    """Concrete traffic analysis model"""
    
    # Override status field to use choices
    status = models.CharField(max_length=20, choices=ANALYSIS_STATUS_CHOICES)
    
    # Add module-specific fields
    camera_id = models.CharField(max_length=50)
    processing_time = models.DurationField()
    
    class Meta:
        db_table = "traffic_analyses"
```

## 🔄 Regenerar modelos

Cuando se actualicen los archivos TypeScript en `../shared/src/`:

```bash
# 1. Generar estructura organizada desde TypeScript
python manage.py generate_entities --organized

# 2. ⚠️ IMPORTANTE: Las entities son abstractas - NO crear migraciones
# Las migraciones las crean las apps que heredan los modelos

# 3. Ejemplo: Si auth_module hereda UserEntity
python manage.py makemigrations auth_module
python manage.py migrate
```

### 🔧 Flujo de trabajo recomendado

```bash
# Desarrollador actualiza ../shared/src/entities/authEntities.ts
# ↓
# 1. Regenerar DLL
python manage.py generate_entities --organized

# 2. Cada módulo actualiza sus modelos concretos
# apps/auth_module/models.py hereda UserEntity

# 3. Cada desarrollador crea sus migraciones
python manage.py makemigrations auth_module
python manage.py makemigrations traffic_module
python manage.py makemigrations plates_module

# 4. Aplicar migraciones
python manage.py migrate
```

## 📋 Comandos disponibles

```bash
# Generar estructura organizada (RECOMENDADO)
python manage.py generate_entities --organized

# Generar archivo único (modo anterior)
python manage.py generate_entities

# Ver qué se generaría sin escribir archivos
python manage.py generate_entities --organized --dry-run

# Solo entidades (sin tipos/constantes)
python manage.py generate_entities --entities-only

# Especificar ruta personalizada de shared
python manage.py generate_entities --shared-path="../shared/src"
```

## 🏗️ Estructura de archivos TypeScript esperada

El generador lee desde `../shared/src/` con esta estructura:

```
shared/src/
├── entities/                # 📄 Interfaces de entidades
│   ├── authEntities.ts     # UserEntity, UserRoleEntity
│   ├── trafficEntities.ts  # TrafficAnalysisEntity, VehicleDetectionEntity
│   ├── plateEntities.ts    # PlateDetectionEntity, PlateAnalysisEntity
│   └── ...
├── types/                   # 📄 Constantes y enums
│   ├── roleTypes.ts        # USER_ROLES, PERMISSIONS
│   ├── trafficTypes.ts     # VEHICLE_TYPES, ANALYSIS_STATUS
│   └── ...
└── ...
```

### 📝 Ejemplos de archivos TypeScript

```typescript
// entities/authEntities.ts
export interface UserEntity {
    id: string;
    email: string;
    passwordHash: string;
    fullName: string;
    phoneNumber?: string;
    isActive: boolean;
    emailConfirmed: boolean;
    createdAt: Date;
    updatedAt: Date;
}

export interface UserRoleEntity {
    id: string;
    userId: string;
    role: UserRoleType;  // ← Referencia a types
    assignedBy?: string;
    assignedAt: Date;
    isActive: boolean;
}
```

```typescript
// types/roleTypes.ts
export const USER_ROLES = {
  ADMIN: 'ADMIN' as const,
  OPERATOR: 'OPERATOR' as const,
  VIEWER: 'VIEWER' as const
} as const;

export const PERMISSIONS = {
  TRAFFIC_CREATE: 'traffic:create',
  TRAFFIC_READ: 'traffic:read',
  // ...
} as const;

export type UserRoleType = typeof USER_ROLES[keyof typeof USER_ROLES];
```

## � Flujo de desarrollo para múltiples desarrolladores

### 🎯 Filosofía del DLL
La app `entities` funciona como una **librería de enlaces dinámicos (DLL)**:
- ✅ Proporciona modelos abstractos organizados por categorías  
- ✅ Se genera automáticamente desde TypeScript compartido
- ✅ Cada desarrollador hereda los modelos en su propio módulo
- ✅ Sin migraciones en entities - solo abstracciones

### 👨‍💻 Cada desarrollador crea su propio módulo:

```bash
# Desarrollador A - Módulo de autenticación
python manage.py startapp auth_module

# Desarrollador B - Módulo de tráfico  
python manage.py startapp traffic_module

# Desarrollador C - Módulo de placas
python manage.py startapp plates_module
```

### 📁 Estructura de módulos individuales:

```python
# apps/auth_module/models.py
from entities.models.auth import UserEntity as BaseUserEntity
from entities.models.auth import UserRoleEntity as BaseUserRoleEntity

class UserEntity(BaseUserEntity):
    """Modelo concreto heredado del DLL"""
    class Meta:
        db_table = 'auth_users'
        
class UserRoleEntity(BaseUserRoleEntity):
    class Meta:
        db_table = 'auth_user_roles'

# apps/traffic_module/models.py  
from entities.models.traffic import TrafficAnalysisEntity as BaseTrafficEntity

class TrafficAnalysis(BaseTrafficEntity):
    class Meta:
        db_table = 'traffic_analysis'
        
# apps/plates_module/models.py
from entities.models.plates import PlateDetectionEntity as BasePlateEntity

class PlateDetection(BasePlateEntity):
    class Meta:
        db_table = 'plates_detections'
```

### 🔄 Flujo de actualización colaborativo:

```bash
# 1. Developer actualiza shared TypeScript
git pull origin main  # Obtiene cambios en ../shared/src/

# 2. Regenerar DLL entities (automático)
python manage.py generate_entities --organized

# 3. Cada desarrollador actualiza su módulo si necesario
# (Solo si hay cambios que afecten sus modelos concretos)

# 4. Crear migraciones individuales
python manage.py makemigrations auth_module
python manage.py makemigrations traffic_module  
python manage.py makemigrations plates_module

# 5. Aplicar migraciones
python manage.py migrate
```

### 🚀 Ventajas de este enfoque:

- **🔄 Sincronización automática**: Cambios en TypeScript se propagan automáticamente
- **🏗️ Separación de responsabilidades**: Cada dev maneja su dominio
- **🧪 Testing independiente**: Cada módulo puede testearse por separado
- **📦 Deploy modular**: Módulos pueden desplegarse independientemente
- **🔒 Abstracción limpia**: DLL mantiene consistencia entre módulos

## �🔧 Configuración

- **Modelos concretos**: Los modelos generados son concretos, no abstractos
- **Tabla prefix**: `entities_` (ej: `entities_userentity`)
- **Campos base**: Todos heredan `created_at`, `updated_at`, `is_active`
- **Auto-import**: Disponible desde `entities.models`

## ⚠️ Notas importantes

### 🚨 Para estructura organizada (--organized):
1. **NO editar manualmente** archivos en `models/` y `constants/` - se regeneran automáticamente
2. **Modelos abstractos**: Los modelos DLL no crean tablas - heredar en módulos concretos  
3. **Sin migraciones**: Esta app DLL no tiene migraciones - los módulos concretos sí
4. **Imports específicos**: Usar imports categorizados (ej: `entities.models.auth`)

### 📄 Para estructura simple (modo anterior):
1. **NO editar manualmente** el archivo `models.py` después del marcador de comentario
2. Los modelos se regeneran completamente en cada ejecución  
3. Las migraciones se deben crear después de regenerar
4. **Modelos concretos**: Crean tablas directamente con prefijo `entities_`

### 🔧 General:
- **TypeScript como fuente**: Los archivos en `../shared/src/` son la fuente de verdad
- **Regeneración segura**: Se puede ejecutar múltiples veces sin problemas
- **Backup automático**: El comando crea respaldos antes de sobrescribir