/**
 * Entidades de Predicción de Tráfico
 * Modelos para análisis predictivo, machine learning y forecasting
 */

import { DensityLevelKey, VehicleTypeKey } from "../types/trafficTypes";

// ============= HISTORICAL DATA ENTITIES =============

export interface TrafficHistoricalDataEntity {
  id: number;
  location: string;
  date: Date;
  hour: number; // 0-23
  dayOfWeek: number; // 0-6 (0=Sunday)
  month: number; // 1-12
  vehicleCount: number;
  avgSpeed: number;
  densityLevel: DensityLevelKey;
  weatherConditions?: string;
  temperature?: number;
  isHoliday: boolean;
  isWeekend: boolean;
  createdAt: Date;
}

export interface LocationTrafficPatternEntity {
  id: number;
  location: string;
  patternType: string; // 'hourly', 'daily', 'weekly', 'monthly'
  patternData: string; // JSON serialized pattern data
  confidence: number;
  validFrom: Date;
  validTo: Date;
  createdAt: Date;
  updatedAt: Date;
}

// ============= PREDICTION MODEL ENTITIES =============

export interface PredictionModelEntity {
  id: string;
  modelName: string;
  modelType: string; // 'linear_regression', 'arima', 'lstm', 'random_forest'
  location: string;
  features: string; // JSON array of feature names
  hyperparameters: string; // JSON serialized model config
  trainingDataPeriod: string; // e.g., "2024-01-01_2024-12-31"
  accuracy: number;
  mse: number; // Mean Square Error
  mae: number; // Mean Absolute Error
  r2Score: number; // R-squared
  isActive: boolean;
  trainedAt: Date;
  createdAt: Date;
}

export interface ModelTrainingJobEntity {
  id: string;
  modelId: string;
  status: string; // 'pending', 'running', 'completed', 'failed'
  startTime: Date;
  endTime?: Date;
  trainingLogs?: string; // JSON serialized logs
  errorMessage?: string;
  dataPointsUsed: number;
  validationScore: number;
  createdAt: Date;
}

// ============= PREDICTION ENTITIES =============

export interface TrafficPredictionEntity {
  id: string;
  modelId: string;
  location: string;
  predictionDate: Date;
  predictionHour: number; // 0-23
  predictedVehicleCount: number;
  predictedAvgSpeed: number;
  predictedDensityLevel: DensityLevelKey;
  confidence: number;
  predictionHorizon: number; // hours ahead (1, 6, 12, 24, 48, etc.)
  actualVehicleCount?: number; // filled after real data comes in
  actualAvgSpeed?: number;
  actualDensityLevel?: DensityLevelKey;
  predictionError?: number; // calculated after actual data
  createdAt: Date;
  updatedAt?: Date;
}

export interface BatchPredictionEntity {
  id: string;
  modelId: string;
  location: string;
  predictionStartDate: Date;
  predictionEndDate: Date;
  totalPredictions: number;
  avgConfidence: number;
  status: string; // 'pending', 'completed', 'failed'
  executionTime: number; // milliseconds
  createdAt: Date;
}

// ============= PREDICTION ACCURACY ENTITIES =============

export interface PredictionAccuracyEntity {
  id: string;
  modelId: string;
  location: string;
  evaluationPeriod: string; // e.g., "2024-01-01_2024-01-31"
  predictionHorizon: number;
  totalPredictions: number;
  correctPredictions: number;
  accuracy: number; // percentage
  avgError: number;
  maxError: number;
  minError: number;
  evaluatedAt: Date;
}

export interface RealTimePredictionEntity {
  id: string;
  location: string;
  currentVehicleCount: number;
  currentDensityLevel: DensityLevelKey;
  next1HourPrediction: number;
  next6HourPrediction: number;
  next24HourPrediction: number;
  confidence1Hour: number;
  confidence6Hour: number;
  confidence24Hour: number;
  lastUpdated: Date;
  createdAt: Date;
}

// ============= EXTERNAL FACTORS ENTITIES =============

export interface WeatherDataEntity {
  id: string;
  location: string;
  date: Date;
  hour: number;
  temperature: number;
  humidity: number;
  precipitation: number;
  windSpeed: number;
  weatherCondition: string; // 'sunny', 'rainy', 'cloudy', 'stormy'
  visibility: number;
  createdAt: Date;
}

export interface EventDataEntity {
  id: string;
  location: string;
  eventName: string;
  eventType: string; // 'sports', 'concert', 'holiday', 'accident', 'construction'
  startDate: Date;
  endDate: Date;
  expectedAttendance?: number;
  trafficImpact: string; // 'low', 'medium', 'high', 'critical'
  createdAt: Date;
}