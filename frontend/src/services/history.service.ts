import { CongestionData, VelocityData, VolumeData, TrafficType } from '../types/historyTraffic';
import api from './api';

export const getHistoryTraffic = async (
  trafficType: TrafficType | null,
  locationId: string,
  cameraId: string,
  dateFrom: string,
  dateTo: string
): Promise<CongestionData | VelocityData | VolumeData>=>{
  console.log("Servicio>>>","TrafficType:", trafficType, "LocationId:", locationId, "CameraId:", cameraId, "DateFrom:", dateFrom, "DateTo:", dateTo);
  const resp = await api.get(
    `/api/predictions/history-traffic/?${trafficType}=true&locationId=${locationId}&cameraId=${cameraId}&dateFrom=${dateFrom}&dateTo=${dateTo}`
);
  return resp.data
}


