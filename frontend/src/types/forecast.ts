export interface ForecastData {
  yhat: number;
  trend: number;
  seasonality: number;
  holidays: number;
  holidays_name: string;
  levelTraffic: string;
  confidenceLevel: number;
  variation_forecast_metrics: ChangePercent;
  forecast: forecast[]
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

export interface ComparisonPeriod {
  label: string;
  value: "daily" | "monthly" | "yearly";
}
