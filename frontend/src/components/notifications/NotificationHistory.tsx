import React, { useEffect, useState } from 'react';
import {
  Bell,
  AlertTriangle,
  AlertCircle,
  Info,
  CheckCircle,
  Search,
  Calendar,
  Filter,
  ChevronDown,
  ChevronUp,
  X,
} from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '../ui/card';
import { Button } from '../ui/Button';
import { api } from '../../services/api';

interface NotificationData {
  type?: string;
  plate_number?: string;
  owner_name?: string;
  complaints_count?: string;
  severity?: string;
  case_number?: string;
  location?: string;
  time?: string;
  is_grouped?: string;
  detection_count?: string;
  time_window_minutes?: string;
  locations?: string;
}

interface NotificationLog {
  id: number;
  notification_type: string;
  title: string;
  body: string;
  data: NotificationData;
  success: boolean;
  sent_at: string;
  vehicle_image?: {
    path: string;
    type: string;
    captured_at: string;
  } | null;
}

interface PaginatedResponse {
  count: number;
  next: string | null;
  previous: string | null;
  results: NotificationLog[];
}

const SEVERITY_CONFIG = {
  NONE: { emoji: '✅', label: 'Ninguna', color: 'bg-gray-100 text-gray-800', borderColor: 'border-gray-300' },
  LOW: { emoji: '⚠️', label: 'Baja', color: 'bg-blue-100 text-blue-800', borderColor: 'border-blue-300' },
  MEDIUM: { emoji: '🚨', label: 'Media', color: 'bg-yellow-100 text-yellow-800', borderColor: 'border-yellow-300' },
  HIGH: { emoji: '🔴', label: 'Alta', color: 'bg-orange-100 text-orange-800', borderColor: 'border-orange-300' },
  CRITICAL: { emoji: '🆘', label: 'Crítica', color: 'bg-red-100 text-red-800', borderColor: 'border-red-300' },
};

export const NotificationHistory: React.FC = () => {
  const [notifications, setNotifications] = useState<NotificationLog[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [expandedId, setExpandedId] = useState<number | null>(null);
  
  // Filtros
  const [searchQuery, setSearchQuery] = useState('');
  const [severityFilter, setSeverityFilter] = useState<string>('');
  const [typeFilter, setTypeFilter] = useState<string>('');
  const [showFilters, setShowFilters] = useState(false);
  
  // Paginación
  const [page, setPage] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [hasNext, setHasNext] = useState(false);
  const [hasPrevious, setHasPrevious] = useState(false);

  useEffect(() => {
    fetchNotifications();
  }, [page, searchQuery, severityFilter, typeFilter]);

  const fetchNotifications = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const params = new URLSearchParams({
        page: page.toString(),
        ...(searchQuery && { search: searchQuery }),
        ...(severityFilter && { severity: severityFilter }),
        ...(typeFilter && { type: typeFilter }),
      });

      const url = `/api/notifications/notifications/?${params.toString()}`;
      console.log('🔍 Fetching notifications from:', url);
      
      const response = await api.get<PaginatedResponse>(url);
      
      console.log('📦 Response:', response);
      console.log('📊 Response data:', response.data);
      
      // Manejar respuesta paginada o array directo
      const data = response.data as any;
      
      // Si es un array directo (sin paginación)
      if (Array.isArray(data)) {
        setNotifications(data);
        setTotalCount(data.length);
        setHasNext(false);
        setHasPrevious(false);
        console.log('✅ Notifications loaded (array):', data.length);
      } else {
        // Si es respuesta paginada
        setNotifications(data.results || []);
        setTotalCount(data.count || 0);
        setHasNext(!!data.next);
        setHasPrevious(!!data.previous);
        console.log('✅ Notifications loaded (paginated):', data.results?.length || 0);
      }
    } catch (err: any) {
      console.error('❌ Error fetching notifications:', err);
      console.error('❌ Error response:', err.response);
      setError(err.response?.data?.detail || 'Error al cargar el historial de notificaciones');
    } finally {
      setLoading(false);
    }
  };

  const clearFilters = () => {
    setSearchQuery('');
    setSeverityFilter('');
    setTypeFilter('');
    setPage(1);
  };

  const getSeverityBadge = (severity: string) => {
    const config = SEVERITY_CONFIG[severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.NONE;
    return (
      <span className={`inline-flex items-center gap-1 px-2 py-1 text-xs font-medium rounded-full ${config.color}`}>
        <span>{config.emoji}</span>
        <span>{config.label}</span>
      </span>
    );
  };

  const getNotificationIcon = (type: string) => {
    switch (type) {
      case 'vehicle_complaint':
        return <AlertTriangle className="h-5 w-5 text-orange-500" />;
      case 'test':
        return <Info className="h-5 w-5 text-blue-500" />;
      default:
        return <Bell className="h-5 w-5 text-gray-500" />;
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    const now = new Date();
    const diffInHours = Math.floor((now.getTime() - date.getTime()) / (1000 * 60 * 60));
    
    if (diffInHours < 1) {
      const diffInMinutes = Math.floor((now.getTime() - date.getTime()) / (1000 * 60));
      return `Hace ${diffInMinutes} minuto${diffInMinutes !== 1 ? 's' : ''}`;
    } else if (diffInHours < 24) {
      return `Hace ${diffInHours} hora${diffInHours !== 1 ? 's' : ''}`;
    } else {
      return date.toLocaleString('es-ES', {
        day: '2-digit',
        month: '2-digit',
        year: 'numeric',
        hour: '2-digit',
        minute: '2-digit',
      });
    }
  };

  const toggleExpand = (id: number) => {
    setExpandedId(expandedId === id ? null : id);
  };

  if (loading && notifications.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Historial de Notificaciones
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center py-12">
            <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-primary"></div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (error) {
    return (
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Historial de Notificaciones
          </CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center justify-center py-12 text-red-500">
            <AlertCircle className="h-12 w-12 mb-4" />
            <p className="text-center">{error}</p>
            <Button onClick={fetchNotifications} variant="secondary" className="mt-4">
              Reintentar
            </Button>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle className="flex items-center justify-between">
          <div className="flex items-center gap-2">
            <Bell className="h-5 w-5" />
            Historial de Notificaciones
            {totalCount > 0 && (
              <span className="text-sm font-normal text-muted-foreground">
                ({totalCount} total{totalCount !== 1 ? 'es' : ''})
              </span>
            )}
          </div>
          <Button
            variant="secondary"
            size="sm"
            onClick={() => setShowFilters(!showFilters)}
            className="flex items-center gap-2"
          >
            <Filter className="h-4 w-4" />
            Filtros
            {showFilters ? <ChevronUp className="h-4 w-4" /> : <ChevronDown className="h-4 w-4" />}
          </Button>
        </CardTitle>
        <p className="text-sm text-muted-foreground">
          Historial completo de todas las notificaciones recibidas
        </p>
      </CardHeader>

      <CardContent className="space-y-4">
        {/* Filtros */}
        {showFilters && (
          <div className="p-4 bg-gray-50 rounded-lg space-y-3 border">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
              {/* Búsqueda por placa */}
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-gray-400" />
                <input
                  type="text"
                  placeholder="Buscar por placa..."
                  value={searchQuery}
                  onChange={(e) => {
                    setSearchQuery(e.target.value);
                    setPage(1);
                  }}
                  className="w-full pl-10 pr-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
                />
              </div>

              {/* Filtro por severidad */}
              <select
                value={severityFilter}
                onChange={(e) => {
                  setSeverityFilter(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Todas las severidades</option>
                <option value="NONE">✅ Ninguna</option>
                <option value="LOW">⚠️ Baja</option>
                <option value="MEDIUM">🚨 Media</option>
                <option value="HIGH">🔴 Alta</option>
                <option value="CRITICAL">🆘 Crítica</option>
              </select>

              {/* Filtro por tipo */}
              <select
                value={typeFilter}
                onChange={(e) => {
                  setTypeFilter(e.target.value);
                  setPage(1);
                }}
                className="px-3 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-primary"
              >
                <option value="">Todos los tipos</option>
                <option value="vehicle_complaint">🚗 Denuncia vehicular</option>
                <option value="test">🧪 Prueba</option>
              </select>
            </div>

            {/* Limpiar filtros */}
            {(searchQuery || severityFilter || typeFilter) && (
              <div className="flex justify-end">
                <Button
                  variant="secondary"
                  size="sm"
                  onClick={clearFilters}
                  className="flex items-center gap-2"
                >
                  <X className="h-4 w-4" />
                  Limpiar filtros
                </Button>
              </div>
            )}
          </div>
        )}

        {/* Lista de notificaciones */}
        {notifications.length === 0 ? (
          <div className="flex flex-col items-center justify-center py-12 text-gray-500">
            <Bell className="h-16 w-16 mb-4 opacity-50" />
            <p className="text-lg font-medium">No hay notificaciones</p>
            <p className="text-sm">
              {searchQuery || severityFilter || typeFilter
                ? 'No se encontraron notificaciones con los filtros aplicados'
                : 'Aún no has recibido ninguna notificación'}
            </p>
          </div>
        ) : (
          <div className="space-y-3">
            {notifications.map((notification) => {
              const isExpanded = expandedId === notification.id;
              const severity = notification.data?.severity || 'NONE';
              const isGrouped = notification.data?.is_grouped === 'true' || notification.data?.is_grouped === true;
              const severityConfig = SEVERITY_CONFIG[severity as keyof typeof SEVERITY_CONFIG] || SEVERITY_CONFIG.NONE;

              return (
                <div
                  key={notification.id}
                  className={`border-l-4 ${severityConfig.borderColor} bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow`}
                >
                  <div
                    className="p-4 cursor-pointer"
                    onClick={() => toggleExpand(notification.id)}
                  >
                    <div className="flex items-start justify-between gap-4">
                      {/* Thumbnail de la imagen del vehículo */}
                      {notification.vehicle_image && (
                        <div className="flex-shrink-0">
                          <img
                            src={`http://localhost:8000/media/${notification.vehicle_image.path}`}
                            alt="Vehículo detectado"
                            className="w-24 h-24 object-contain rounded-lg border-2 border-gray-200 bg-gray-50"
                            onError={(e) => {
                              // Si falla la carga, ocultar la imagen
                              e.currentTarget.style.display = 'none';
                            }}
                          />
                        </div>
                      )}
                      
                      <div className="flex items-start gap-3 flex-1">
                        <div className="mt-1">
                          {getNotificationIcon(notification.notification_type)}
                        </div>
                        <div className="flex-1 min-w-0">
                          <div className="flex items-center gap-2 flex-wrap mb-1">
                            <h3 className="font-semibold text-gray-900">
                              {notification.title}
                            </h3>
                            {isGrouped && (
                              <span className="px-2 py-0.5 text-xs bg-purple-100 text-purple-800 rounded-full">
                                📍 Agrupada
                              </span>
                            )}
                            {getSeverityBadge(severity)}
                            <span className={`px-2 py-0.5 text-xs rounded-full ${
                              notification.success
                                ? 'bg-green-100 text-green-800'
                                : 'bg-red-100 text-red-800'
                            }`}>
                              {notification.success ? '✓ Enviada' : '✗ Fallida'}
                            </span>
                          </div>
                          <p className="text-sm text-gray-600 mb-2">
                            {notification.body}
                          </p>
                          <div className="flex items-center gap-4 text-xs text-gray-500">
                            <span className="flex items-center gap-1">
                              <Calendar className="h-3 w-3" />
                              {formatDate(notification.sent_at)}
                            </span>
                            {notification.data?.plate_number && (
                              <span className="font-mono bg-gray-100 px-2 py-0.5 rounded">
                                🚗 {notification.data.plate_number}
                              </span>
                            )}
                            {isGrouped && notification.data?.detection_count && (
                              <span className="bg-purple-50 px-2 py-0.5 rounded">
                                {notification.data.detection_count} detecciones
                              </span>
                            )}
                          </div>
                        </div>
                      </div>
                      <button className="text-gray-400 hover:text-gray-600">
                        {isExpanded ? (
                          <ChevronUp className="h-5 w-5" />
                        ) : (
                          <ChevronDown className="h-5 w-5" />
                        )}
                      </button>
                    </div>

                    {/* Detalles expandidos */}
                    {isExpanded && notification.data && (
                      <div className="mt-4 pt-4 border-t space-y-2">
                        <h4 className="font-semibold text-sm text-gray-700 mb-2">Detalles:</h4>
                        <div className="grid grid-cols-1 md:grid-cols-2 gap-2 text-sm">
                          {notification.data.plate_number && (
                            <div>
                              <span className="text-gray-600">Placa:</span>{' '}
                              <span className="font-mono font-semibold">{notification.data.plate_number}</span>
                            </div>
                          )}
                          {notification.data.owner_name && (
                            <div>
                              <span className="text-gray-600">Propietario:</span>{' '}
                              <span className="font-medium">{notification.data.owner_name}</span>
                            </div>
                          )}
                          {notification.data.complaints_count && (
                            <div>
                              <span className="text-gray-600">Denuncias:</span>{' '}
                              <span className="font-semibold text-red-600">{notification.data.complaints_count}</span>
                            </div>
                          )}
                          {notification.data.case_number && (
                            <div>
                              <span className="text-gray-600">Expediente:</span>{' '}
                              <span className="font-mono">{notification.data.case_number}</span>
                            </div>
                          )}
                          {notification.data.location && (
                            <div>
                              <span className="text-gray-600">Ubicación:</span>{' '}
                              <span>{notification.data.location}</span>
                            </div>
                          )}
                          {notification.data.time && (
                            <div>
                              <span className="text-gray-600">Hora detección:</span>{' '}
                              <span>{new Date(notification.data.time).toLocaleString('es-ES')}</span>
                            </div>
                          )}
                          {isGrouped && (
                            <>
                              {notification.data.detection_count && (
                                <div>
                                  <span className="text-gray-600">Detecciones:</span>{' '}
                                  <span className="font-semibold text-purple-600">
                                    {notification.data.detection_count} veces
                                  </span>
                                </div>
                              )}
                              {notification.data.time_window_minutes && (
                                <div>
                                  <span className="text-gray-600">Ventana de tiempo:</span>{' '}
                                  <span>{notification.data.time_window_minutes} minutos</span>
                                </div>
                              )}
                              {notification.data.locations && (
                                <div className="md:col-span-2">
                                  <span className="text-gray-600">Ubicaciones:</span>{' '}
                                  <span>{notification.data.locations}</span>
                                </div>
                              )}
                            </>
                          )}
                        </div>
                      </div>
                    )}
                  </div>
                </div>
              );
            })}
          </div>
        )}

        {/* Paginación */}
        {totalCount > 0 && (
          <div className="flex items-center justify-between pt-4 border-t">
            <div className="text-sm text-gray-600">
              Mostrando {notifications.length} de {totalCount} notificaciones
            </div>
            <div className="flex items-center gap-2">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(page - 1)}
                disabled={!hasPrevious || loading}
              >
                Anterior
              </Button>
              <span className="text-sm text-gray-600 px-3">
                Página {page}
              </span>
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setPage(page + 1)}
                disabled={!hasNext || loading}
              >
                Siguiente
              </Button>
            </div>
          </div>
        )}
      </CardContent>
    </Card>
  );
};
