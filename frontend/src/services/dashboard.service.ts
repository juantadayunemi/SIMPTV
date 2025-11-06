import api from './api';

export type CongestionLevel = 'low' | 'moderate' | 'high' | 'critical';

export interface CurrentTrafficData {
  cameraId: number;
  cameraName: string;
  location: string;
  congestionLevel: CongestionLevel;
  averageSpeed: number;
  vehicleCount: number;
  congestionIndex: number;
  timestamp: string;
}

export interface DashboardStats {
  activeCameras: number;
  avgSpeed: number;
  criticalAlerts: number;
  networkEfficiency: number;
  currentTrafficData: CurrentTrafficData[];
}

class DashboardService {
  /**
   * Obtener estadísticas del dashboard
   */
  async getDashboardStats(): Promise<DashboardStats> {
    const response = await api.get('/api/traffic/dashboard/stats');
    return response.data;
  }

  /**
   * Obtener datos de tráfico en tiempo real
   */
  async getCurrentTrafficData(): Promise<CurrentTrafficData[]> {
    const response = await api.get('/api/traffic/dashboard/current-traffic');
    return response.data;
  }

  /**
   * Obtener estadísticas por rango de fechas
   */
  async getStatsByDateRange(startDate: string, endDate: string): Promise<{
    avgSpeed: number;
    totalVehicles: number;
    peakHours: Array<{ hour: number; count: number }>;
    congestionTrends: Array<{ date: string; level: CongestionLevel; count: number }>;
  }> {
    const response = await api.get('/api/traffic/dashboard/stats-by-date', {
      params: { startDate, endDate }
    });
    return response.data;
  }

  /**
   * Obtener alertas críticas activas
   */
  async getCriticalAlerts(): Promise<Array<{
    id: number;
    cameraId: number;
    cameraName: string;
    alertType: string;
    severity: 'low' | 'medium' | 'high' | 'critical';
    message: string;
    timestamp: string;
  }>> {
    const response = await api.get('/api/traffic/dashboard/critical-alerts');
    return response.data;
  }
}

export const dashboardService = new DashboardService();
export default dashboardService;
