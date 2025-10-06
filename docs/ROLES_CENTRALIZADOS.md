# Sistema de Roles Centralizados

## 📋 Descripción

Este proyecto utiliza un sistema de roles y permisos centralizado ubicado en el paquete `@traffic-analysis/shared`, lo que garantiza consistencia entre el frontend y backend.

## 🎯 Ubicación

```
shared/
  └── src/
      └── types/
          └── roleTypes.ts  ← Definición centralizada de roles
```

## 🔑 Roles Disponibles

```typescript
export const USER_ROLES = {
  ADMIN: 'ADMIN' as const,      // Administrador del sistema
  OPERATOR: 'OPERATOR' as const, // Operador de monitoreo
  VIEWER: 'VIEWER' as const      // Usuario de solo lectura
} as const;
```

## 📦 Uso en el Frontend

### Importación

```typescript
import { USER_ROLES, type UserRoleType } from '@traffic-analysis/shared';
```

### Ejemplo en Sidebar

```typescript
const navigationItems = [
  {
    name: 'Inicio',
    href: '/dashboard',
    icon: <HomeIcon />,
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR, USER_ROLES.VIEWER] as UserRoleType[]
  },
  {
    name: 'Configuración',
    href: '/settings',
    icon: <SettingsIcon />,
    roles: [USER_ROLES.ADMIN] as UserRoleType[]
  }
];
```

## 🔐 Permisos Disponibles

```typescript
export const PERMISSIONS = {
  // Traffic Analysis
  TRAFFIC_CREATE: 'traffic:create',
  TRAFFIC_READ: 'traffic:read',
  TRAFFIC_UPDATE: 'traffic:update',
  TRAFFIC_DELETE: 'traffic:delete',
  
  // Plate Detection
  PLATE_CREATE: 'plate:create',
  PLATE_READ: 'plate:read',
  PLATE_UPDATE: 'plate:update',
  PLATE_DELETE: 'plate:delete',
  
  // Users Management
  USER_CREATE: 'user:create',
  USER_READ: 'user:read',
  USER_UPDATE: 'user:update',
  USER_DELETE: 'user:delete',
  
  // System
  SYSTEM_ADMIN: 'system:admin',
  SETTINGS_MANAGE: 'settings:manage',
  NOTIFICATIONS_MANAGE: 'notifications:manage'
} as const;
```

## 🎪 Mapeo de Roles a Permisos

```typescript
export const ROLE_PERMISSIONS = {
  [USER_ROLES.ADMIN]: [
    // Todos los permisos del sistema
    PERMISSIONS.TRAFFIC_CREATE,
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.TRAFFIC_UPDATE,
    PERMISSIONS.TRAFFIC_DELETE,
    // ... más permisos
    PERMISSIONS.SYSTEM_ADMIN
  ],
  [USER_ROLES.OPERATOR]: [
    // Permisos de operación
    PERMISSIONS.TRAFFIC_CREATE,
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.TRAFFIC_UPDATE,
    // ... permisos limitados
  ],
  [USER_ROLES.VIEWER]: [
    // Solo lectura
    PERMISSIONS.TRAFFIC_READ,
    PERMISSIONS.PLATE_READ,
    PERMISSIONS.USER_READ
  ]
} as const;
```

## ✅ Ventajas del Sistema Centralizado

### 1. **Consistencia**
- Los mismos roles en frontend y backend
- No hay desincronización de valores
- Tipos TypeScript compartidos

### 2. **Mantenibilidad**
- Un solo lugar para modificar roles
- Cambios automáticos en todo el proyecto
- Menos errores de duplicación

### 3. **Type Safety**
- TypeScript valida los roles en tiempo de compilación
- Autocomplete en el IDE
- Errores detectados antes de runtime

### 4. **Escalabilidad**
- Fácil agregar nuevos roles
- Fácil agregar nuevos permisos
- Sistema de permisos granular

## 🔧 Compilación del Paquete Shared

Cada vez que modifiques `roleTypes.ts`, debes recompilar:

```bash
# Opción 1: Build manual
cd shared
npm run build

# Opción 2: Build con watch (desarrollo)
cd shared
npm run build:watch

# Opción 3: Build automático desde el frontend
cd frontend
npm install  # Ejecuta postinstall que compila shared
```

## 📝 Ejemplo Completo

```typescript
// shared/src/types/roleTypes.ts
export const USER_ROLES = {
  ADMIN: 'ADMIN' as const,
  OPERATOR: 'OPERATOR' as const,
  VIEWER: 'VIEWER' as const
} as const;

export type UserRoleType = typeof USER_ROLES[keyof typeof USER_ROLES];

// frontend/src/components/layout/Sidebar.tsx
import { USER_ROLES, type UserRoleType } from '@traffic-analysis/shared';

const navigationItems = [
  {
    name: 'Dashboard',
    roles: [USER_ROLES.ADMIN, USER_ROLES.OPERATOR] as UserRoleType[]
  }
];
```

## 🚀 Mejores Prácticas

1. **Siempre importar desde `@traffic-analysis/shared`**
   ```typescript
   ✅ import { USER_ROLES } from '@traffic-analysis/shared';
   ❌ import { USER_ROLES } from '../../../shared/src/types/roleTypes';
   ```

2. **Usar tipado explícito**
   ```typescript
   ✅ roles: [USER_ROLES.ADMIN] as UserRoleType[]
   ❌ roles: ['ADMIN']  // String literal sin tipo
   ```

3. **Validar roles en componentes**
   ```typescript
   const hasAccess = (userRole: UserRoleType, allowedRoles: UserRoleType[]) => {
     return allowedRoles.includes(userRole);
   };
   ```

4. **Usar permisos granulares cuando sea necesario**
   ```typescript
   import { PERMISSIONS, ROLE_PERMISSIONS } from '@traffic-analysis/shared';
   
   const canCreateTraffic = ROLE_PERMISSIONS[userRole].includes(
     PERMISSIONS.TRAFFIC_CREATE
   );
   ```

## 🔄 Flujo de Actualización

```
1. Modificar roleTypes.ts en shared/
2. Compilar: cd shared && npm run build
3. Los cambios se reflejan automáticamente en frontend y backend
4. TypeScript valida en tiempo de compilación
```

## 📊 Estructura de Archivos

```
TrafiSmart/
├── shared/                          # Paquete compartido
│   ├── src/
│   │   ├── types/
│   │   │   └── roleTypes.ts        # ⭐ Definición de roles
│   │   └── index.ts                # Export central
│   ├── dist/                       # Archivos compilados
│   │   ├── index.js
│   │   ├── index.mjs
│   │   └── index.d.ts
│   └── package.json
│
├── frontend/
│   ├── src/
│   │   └── components/
│   │       └── layout/
│   │           └── Sidebar.tsx     # ⭐ Uso de roles
│   └── package.json                # Depende de @traffic-analysis/shared
│
└── backend/
    └── apps/
        └── auth_app/
            └── models.py           # Roles sincronizados
```

## 🎓 Resumen

El sistema de roles centralizados en `@traffic-analysis/shared` proporciona:

- ✅ **Una fuente de verdad** para todos los roles y permisos
- ✅ **Type safety** completo con TypeScript
- ✅ **Sincronización automática** entre frontend y backend
- ✅ **Fácil mantenimiento** y escalabilidad
- ✅ **Prevención de errores** en tiempo de compilación

---

**Última actualización:** Octubre 2025
**Autor:** TrafiSmart Development Team
