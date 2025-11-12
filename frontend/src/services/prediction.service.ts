import api from "./api";
import { ForecastData,ForecastDataTraffic,ForecastDataSpeed, LevelTrafficData, ChangePercent } from '../types/forecast';

export const getAllForecast = async (
  locationId: string,
  selectedCamera: string,
  date: string,
  hour: string,
  minute: string,
  selectedPeriod: 'daily' | 'monthly' | 'yearly'
):Promise<ForecastData[]>=>{
  const resp = await api.get(
    `/api/predictions/traffic-predictions/?locationId=${locationId}&cameraId=${selectedCamera}&date=${date}&hour=${hour}&minute=${minute}&periodsType=${selectedPeriod}`
);
  return resp.data
}


export const getForecastTraffic = async (
  locationId: string,
  selectedCamera: string,
  date: string,
  hour: string,
  minute: string,
  selectedPeriod: 'daily' | 'monthly' | 'yearly'
):Promise<ForecastDataTraffic[]>=>{
  const resp = await api.get(
    `/api/predictions/traffic-predictions/?locationId=${locationId}&cameraId=${selectedCamera}&date=${date}&hour=${hour}&minute=${minute}&periodsType=${selectedPeriod}`
);
  return resp.data
}

export const getForecastSpeed = async (
  locationId: string,
  selectedCamera: string,
  date: string,
  hour: string,
  minute: string,
):Promise<ForecastDataSpeed[]>=>{
  console.log("Desde servicio: ",locationId, selectedCamera, date, hour, minute);
  const resp = await api.get(
    `/api/predictions/speed-predictions/?locationId=${locationId}&cameraId=${selectedCamera}&date=${date}&hour=${hour}&minute=${minute}`
);
  return resp.data
}


export const getLevelTraffic = async (
  locationId: string,
  selectedCamera: string,
  yhat_count: number,
  yhat_speed: number,
):Promise<LevelTrafficData[]>=>{
  console.log("Desde servicio: ",locationId, selectedCamera, yhat_count, yhat_speed);
  const resp = await api.get(
    `/api/predictions/level-traffic/?locationId=${locationId}&cameraId=${selectedCamera}&yhat_count=${yhat_count}&yhat_speed=${yhat_speed}`
);
  return resp.data
}

export const getForecastChangePercent = async (
  locationId: string,
  selectedCamera: string,
  date: string,
  hour: string,
  minute: string,
  selectedPeriod: 'daily' | 'monthly' | 'yearly'
):Promise<ChangePercent>=>{
  const resp = await api.get(
    `/api/predictions/forecast-change-percentage/?locationId=${locationId}&cameraId=${selectedCamera}&date=${date}&hour=${hour}&minute=${minute}&periodsType=${selectedPeriod}`
);
  return resp.data
}