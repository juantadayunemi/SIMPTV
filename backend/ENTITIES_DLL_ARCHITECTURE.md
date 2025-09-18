# ENTITIES DLL - ARQUITECTURA DE MODELOS COMPARTIDOS

## ¿Qué es la DLL de Entidades?

La app `entities` funciona como una **biblioteca de modelos compartidos (DLL)** que proporciona modelos abstractos generados automáticamente desde interfaces TypeScript ubicadas en `../shared/src/entities`.

## Arquitectura del Proyecto

```
backend/
├── apps/
│   ├── entities/           # 📚 DLL - Modelos abstractos compartidos
│   ├── auth_app/          # 🔐 App de autenticación  
│   ├── plates_app/        # 🚗 App de detección de placas
│   └── traffic_app/       # 🚦 App de análisis de tráfico
├── shared/                # (Fuera del backend)
│   └── src/entities/      # 📄 Interfaces TypeScript fuente
└── config/                # ⚙️ Configuración Django
```

## Flujo de Trabajo

### 1. Definir Entidades TypeScript
```typescript
// ../shared/src/entities/sharedEntities.ts
export interface UserEntity {
    id: number;
    email: string;
    passwordHash: string;
    fullName: string;
    phoneNumber?: string;
    isActive: boolean;
}
```

### 2. Generar Modelos DLL
```bash
cd backend
python manage.py generate_entities
```

Esto genera modelos **abstractos** en `apps/entities/models.py`:

```python
class UserEntity(BaseModel):
    """Abstract DLL model from TypeScript interface UserEntity"""
    """USAGE: Inherit in other apps - class User(UserEntity): pass"""
    
    email = models.EmailField(max_length=255)
    passwordHash = models.CharField(max_length=255)
    fullName = models.CharField(max_length=255)
    # ... más campos
    
    class Meta:
        abstract = True  # ✅ No crea tabla - solo herencia
```

### 3. Usar DLL en Apps Específicas

#### Ejemplo: Authentication App
```python
# apps/auth_app/models.py
from apps.entities.models import UserEntity, UserRoleEntity

class User(UserEntity):
    """Modelo concreto heredando de entities DLL"""
    
    # Campos adicionales específicos de autenticación
    last_login = models.DateTimeField(null=True, blank=True)
    failed_login_attempts = models.IntegerField(default=0)
    
    class Meta:
        db_table = "auth_users"  # ✅ Crea tabla concreta
        verbose_name = "User"
```

#### Ejemplo: Plates App  
```python
# apps/plates_app/models.py
from apps.entities.models import PlateDetectionEntity
from apps.auth_app.models import User  # ✅ Relación entre apps

class PlateDetection(PlateDetectionEntity):
    """Modelo concreto heredando de entities DLL"""
    
    # Campos adicionales específicos de placas
    processed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    
    class Meta:
        db_table = "plates_detections"  # ✅ Crea tabla concreta
```

### 4. Crear Migraciones por App
```bash
# Cada app crea sus propias migraciones
python manage.py makemigrations auth_app
python manage.py makemigrations plates_app

# Y las aplica
python manage.py migrate
```

## Ventajas de esta Arquitectura

### ✅ Desarrollo Independiente
- Cada desarrollador puede trabajar en su app sin afectar otras
- Las entidades están centralizadas pero cada app es autónoma

### ✅ Consistencia de Datos
- Todas las apps usan las mismas definiciones de entidades
- Los cambios en TypeScript se propagan automáticamente

### ✅ Relaciones Entre Apps
```python
# Las apps pueden relacionarse entre sí
class PlateDetection(PlateDetectionEntity):
    processed_by = models.ForeignKey(
        'auth_app.User',  # ✅ Relación a otra app
        on_delete=models.CASCADE
    )
```

### ✅ Un Solo Proyecto, Múltiples Responsabilidades
- Backend unificado con API REST
- Cada app maneja su dominio específico
- Conexión a SQL Server centralizada
- Frontend React + Vite consume APIs

## Comandos Importantes

### Regenerar Modelos DLL
```bash
python manage.py generate_entities
```

### Ver Modelos Generados (sin cambios)
```bash
python manage.py generate_entities --dry-run
```

### Crear Nueva App
```bash
cd apps
python ../manage.py startapp nueva_app
```

### Usar DLL en Nueva App
```python
# apps/nueva_app/models.py
from apps.entities.models import AlgunaEntity

class MiModelo(AlgunaEntity):
    # Campos adicionales específicos
    campo_extra = models.CharField(max_length=100)
    
    class Meta:
        db_table = "nueva_app_mimodelo"
```

## Estructura de Base de Datos Resultante

```sql
-- Tablas creadas por cada app (NO por entities)
auth_users              -- Creada por auth_app
auth_user_roles         -- Creada por auth_app  
auth_login_sessions     -- Creada por auth_app

plates_detections       -- Creada por plates_app
plates_analyses         -- Creada por plates_app
plates_vehicles         -- Creada por plates_app

traffic_analysis        -- Creada por traffic_app (futuro)
notifications          -- Creada por notifications_app (futuro)
```

## Patrón de Importación

```python
# ✅ CORRECTO - Importar desde entities DLL
from apps.entities.models import UserEntity, PlateDetectionEntity

# ✅ CORRECTO - Importar modelos concretos de otras apps  
from apps.auth_app.models import User
from apps.plates_app.models import PlateDetection

# ✅ CORRECTO - Heredar de DLL
class MiUsuario(UserEntity):
    pass

# ✅ CORRECTO - Relacionar con modelos de otras apps
class MiModelo(models.Model):
    usuario = models.ForeignKey('auth_app.User', on_delete=models.CASCADE)
```

## Frontend Integration

El frontend React + Vite consume las APIs de todas las apps:

```typescript
// Frontend puede usar las mismas interfaces TypeScript
import { UserEntity, PlateDetectionEntity } from '../shared/src/entities';

// Las APIs devuelven datos que coinciden con las entidades
const user: UserEntity = await api.get('/auth/user/1');
const plate: PlateDetectionEntity = await api.get('/plates/detection/1');
```

Esta arquitectura te permite mantener un proyecto unificado donde cada desarrollador puede trabajar de manera independiente en su dominio específico, mientras comparten las definiciones de entidades centralizadas.