# DTOs Architecture - TrafiSmart

## Nueva Arquitectura de DTOs

Los DTOs han sido reorganizados para mejorar la mantenibilidad y separación de responsabilidades:

### Archivos Nuevos (RECOMENDADOS)

#### 📊 `trafficDto.ts`
DTOs específicos para análisis de tráfico:
- `TrafficAnalysisResponseDTO` - Respuestas de análisis completo
- `VehicleDetectionResponseDTO` - Detección de vehículos individual
- `TrafficSearchQueryDTO` - Consultas de búsqueda de tráfico
- `CreateTrafficAnalysisRequestDTO` - Creación de nuevos análisis
- `TrafficStatsDTO` - Estadísticas de tráfico para dashboard

#### 🚗 `plateDto.ts`
DTOs específicos para detección de placas:
- `PlateDetectionResponseDTO` - Respuestas de detección de placas
- `PlateAlertResponseDTO` - Alertas de placas
- `PlateSearchQueryDTO` - Consultas de búsqueda de placas
- `PlateValidationDTO` - Validación de placas
- `PlateFrequencyAnalysisDTO` - Análisis de frecuencia de placas

#### 🔧 `commonDto.ts`
DTOs compartidos para funcionalidades comunes:
- `ApiResponseDTO<T>` - Respuestas estándar de API
- `PaginatedResponseDTO<T>` - Respuestas paginadas
- `LoginRequestDTO` / `LoginResponseDTO` - Autenticación
- `UserSearchQueryDTO` - Consultas de usuarios
- `NotificationDTO` - Notificaciones del sistema
- `DashboardStatsDTO` - Estadísticas del dashboard
- `WebSocketMessageDTO<T>` - Mensajes de WebSocket

### Archivos Legacy (COMPATIBILIDAD)

#### ⚠️ `responseDto.ts` (DEPRECATED)
- Mantiene interfaces antiguas para compatibilidad
- Todas las interfaces están marcadas como `@deprecated`
- Migrar gradualmente a los nuevos archivos

#### ⚠️ `requestDto.ts` (DEPRECATED)
- Mantiene DTOs de request antiguos
- Todas las interfaces están marcadas como `@deprecated`
- Migrar gradualmente a los nuevos archivos

## Guía de Migración

### Para código nuevo:
```typescript
// ✅ CORRECTO - Usar nuevos DTOs
import { TrafficAnalysisResponseDTO } from '@shared/dto/trafficDto';
import { ApiResponseDTO } from '@shared/dto/commonDto';
import { PlateDetectionResponseDTO } from '@shared/dto/plateDto';

// ❌ EVITAR - DTOs legacy
import { TrafficAnalysisDTO } from '@shared/dto/responseDto';
```

### Para código existente:
1. Identificar qué DTOs legacy se están usando
2. Importar el equivalente de los nuevos archivos
3. Actualizar los tipos gradualmente
4. Verificar que todo funcione correctamente

## Ventajas de la Nueva Arquitectura

1. **Separación de Responsabilidades**: Cada archivo maneja un dominio específico
2. **Mantenibilidad**: Más fácil encontrar y modificar DTOs relacionados
3. **Escalabilidad**: Agregar nuevos DTOs sin contaminar archivos existentes
4. **Tipado Mejorado**: DTOs más específicos y descriptivos
5. **Menor Acoplamiento**: Imports más granulares y específicos

## Estructura de Naming

### DTOs de Request:
- `Create[Entity]RequestDTO` - Crear nueva entidad
- `Update[Entity]RequestDTO` - Actualizar entidad existente
- `[Entity]SearchQueryDTO` - Consultas de búsqueda
- `[Entity]ValidationDTO` - Validación de datos

### DTOs de Response:
- `[Entity]ResponseDTO` - Respuesta individual
- `[Entity]ListResponseDTO` - Lista de entidades
- `[Entity]StatsDTO` - Estadísticas de la entidad
- `[Entity]SummaryDTO` - Resumen de la entidad

### DTOs Compartidos:
- `ApiResponseDTO<T>` - Respuesta estándar de API
- `PaginatedResponseDTO<T>` - Respuesta paginada
- `BaseQueryDTO` - Consulta base con paginación
- `WebSocketMessageDTO<T>` - Mensaje de WebSocket

## Próximos Pasos

1. Actualizar servicios para usar nuevos DTOs
2. Migrar componentes de frontend gradualmente
3. Actualizar documentación de API
4. Eliminar DTOs legacy cuando no se usen más