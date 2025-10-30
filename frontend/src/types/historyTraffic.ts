export interface DayData {
  day: string;
  total: number;
}

export interface RushData {
  hour: number;
  count_vehicles: number;
}

export interface CongestionData {
  avg_velocity: number;
  avg_congestion: number;
  rush_hour: RushData;
  days_analyzed: number;
  congestion_per_day: DayData[];
}

export interface VelocityData {
  avg_velocity: number;
  max_velocity: number;
  min_velocity: number;
  days_analyzed: number;
  velocity_per_day: DayData[];
}

export interface VolumeData {
  total_volume: number;
  avg_vehicles_per_hour: number;
  rush_hour: RushData;
  days_analyzed: number;
  volume_per_day: DayData[];
}

export type TrafficType = "congestion" | "velocity" | "volume";

export type DateRangeType = "today" | "7days" | "30days" | "custom";

export interface DateRange {
  dateFrom: string;
  dateTo: string;
}

export interface OptionsType {
  margin: number;
  filename?: string;
  html2canvas?: { scale: number };
  jsPDF?: { unit: string; format: string; orientation: string };
}
