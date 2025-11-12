export interface ForecastData {
  traffic: ForecastDataTraffic;
  speed: ForecastDataSpeed;
  level: LevelTrafficData;
}

export interface ForecastDataTraffic {
  yhat: number;
  trend: number;
  seasonality: number;
  holidays: number;
  holidays_name: string;
  confidenceLevel: number;
  variation_forecast_metrics: ChangePercent;
  forecast: forecast[];
  is_reliable: boolean;
}

export interface ForecastDataSpeed {
    yhat_speed: number;
    forecast_speed: forecast[];
    is_reliable: boolean;
}

export interface LevelTrafficData {
    level: string;
    IC: number;
}

export interface ImpactMetrics {
  holidays_impact: number;
  seasonality_impact: number;
}

export interface ChangePercent {
  yhat_change: number;
  trend_change: number;
}

export interface forecast {
  ds: string;
  yhat: number
}

export interface Location {
  id: number;
  description: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}

export interface Camera {
  id: number;
  locationId: number;
  name: string;
  createdAt: string;
  updatedAt: string;
  isActive: boolean;
}
export interface ComparisonPeriod {
  label: string;
  value: "daily" | "monthly" | "yearly";
}
