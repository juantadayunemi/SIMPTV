import { CongestionData, VelocityData, VolumeData, TrafficType } from '../types/historyTraffic';
import api from './api';

export const getHistoryTraffic = async (
  trafficType: TrafficType,
  locationId: number,
  dateFrom: string,
  dateTo: string
): Promise<CongestionData | VelocityData | VolumeData>=>{
  console.log('Type Traffic:', trafficType);
  const resp = await api.get(
    `/api/predictions/history-traffic/?${trafficType}=true&locationId=${locationId}&dateFrom=${dateFrom}&dateTo=${dateTo}`
);
  return resp.data
}


