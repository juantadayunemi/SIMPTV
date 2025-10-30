import api from "./api";
import { ForecastData } from '../types/forecast';

export const getForecast = async (
  locationId: number,
  date: string,
  hour: string,
  minute: string,
  selectedPeriod: 'daily' | 'monthly' | 'yearly'
):Promise<ForecastData[]>=>{
  const resp = await api.get(
    `/api/predictions/traffic-predictions/?locationId=${locationId}&date=${date}&hour=${hour}&minute=${minute}&periodsType=${selectedPeriod}`
);
  return resp.data
}

