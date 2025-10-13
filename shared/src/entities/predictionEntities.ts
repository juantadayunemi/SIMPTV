/**
 * Entidades de Predicción de Tráfico
 * Modelos para análisis predictivo, machine learning y forecasting
 * 
 * ANOTACIONES PARA GENERADOR DJANGO (SQL Server):
 * @db:primary - Campo primary key
 * @db:identity - IDENTITY(1,1) autoincremental
 * @db:foreignKey ModelName - Foreign Key a otro modelo
 * @db:varchar(n) - VARCHAR(n)
 * @db:int - INT
 * @db:bigint - BIGINT
 * @db:float - FLOAT
 * @db:decimal(p,s) - DECIMAL(precision, scale)
 * @db:text - TEXT/NVARCHAR(MAX)
 * @db:datetime - DATETIME2
 * @default(value) - Valor por defecto
 */

import { DensityLevelKey, VehicleTypeKey } from "../types/trafficTypes";

// ============= HISTORICAL DATA ENTITIES (Datos Históricos) =============

/**
 * TrafficHistoricalDataEntity - Datos Históricos de Tráfico
 * Almacena registros históricos agregados por hora para análisis y entrenamiento de modelos
 */
export interface TrafficHistoricalDataEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la cámara)
  date: Date; // @db:datetime - Fecha del registro histórico
  hour: number; // @db:int - Hora del día (0-23)
  dayOfWeek: number; // @db:int - Día de la semana (0=Domingo, 1=Lunes, ..., 6=Sábado)
  month: number; // @db:int - Mes del año (1-12)
  vehicleCount: number; // @db:int @default(0) - Cantidad de vehículos detectados en esa hora
  avgSpeed: number; // @db:decimal(6,2) @default(0) - Velocidad promedio en km/h
  densityLevel: DensityLevelKey; // @db:varchar(20) - Nivel de densidad del tráfico (LOW, MEDIUM, HIGH, CRITICAL)
  weatherConditions?: string; // @db:varchar(100) - Condiciones climáticas (Ej: "Soleado", "Lluvioso")
  temperature?: number; // @db:decimal(5,2) - Temperatura en grados Celsius
  isHoliday: boolean; // @default(false) - Si es día festivo
  isWeekend: boolean; // @default(false) - Si es fin de semana (sábado o domingo)
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}

/**
 * LocationTrafficPatternEntity - Patrones de Tráfico por Ubicación
 * Almacena patrones detectados (horario, diario, semanal, mensual) para cada ubicación
 */
export interface LocationTrafficPatternEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la cámara)
  patternType: string; // @db:varchar(20) - Tipo de patrón: 'hourly' (por hora), 'daily' (diario), 'weekly' (semanal), 'monthly' (mensual)
  patternData: string; // @db:text - JSON serializado con datos del patrón detectado
  confidence: number; // @db:decimal(5,4) - Nivel de confianza del patrón (0-1, donde 1 = 100% confiable)
  validFrom: Date; // @db:datetime - Fecha desde la cual el patrón es válido
  validTo: Date; // @db:datetime - Fecha hasta la cual el patrón es válido
  createdAt: Date; // @db:datetime - Fecha de creación del patrón
  updatedAt: Date; // @db:datetime - Fecha de última actualización
}

// ============= PREDICTION MODEL ENTITIES (Modelos de Predicción) =============

/**
 * PredictionModelEntity - Modelo de Machine Learning
 * Almacena información sobre modelos entrenados (LSTM, ARIMA, Random Forest, etc.)
 */
export interface PredictionModelEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID único del modelo
  modelName: string; // @db:varchar(100) - Nombre descriptivo del modelo (Ej: "LSTM-LOC001-2024")
  modelType: string; // @db:varchar(50) - Tipo de modelo: 'linear_regression', 'arima', 'lstm', 'random_forest'
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación para la que fue entrenado)
  features: string; // @db:text - JSON array de nombres de features usadas en el modelo
  hyperparameters: string; // @db:text - JSON serializado con configuración del modelo (ej: learning_rate, epochs, etc.)
  trainingDataPeriod: string; // @db:varchar(50) - Período de datos de entrenamiento (Ej: "2024-01-01_2024-12-31")
  accuracy: number; // @db:decimal(5,4) - Exactitud del modelo (0-1, donde 1 = 100% exacto)
  mse: number; // @db:decimal(12,6) - Mean Square Error (error cuadrático medio)
  mae: number; // @db:decimal(12,6) - Mean Absolute Error (error absoluto medio)
  r2Score: number; // @db:decimal(5,4) - R-squared score (coeficiente de determinación)
  isActive: boolean; // @default(true) - Si el modelo está activo para hacer predicciones
  trainedAt: Date; // @db:datetime - Fecha/hora de entrenamiento del modelo
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}

/**
 * ModelTrainingJobEntity - Trabajo de Entrenamiento de Modelo
 * Almacena información sobre el proceso de entrenamiento de un modelo de ML
 * modelId: Es el ID del PredictionModelEntity que se está entrenando
 */
export interface ModelTrainingJobEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID del trabajo de entrenamiento
  modelId: string; // @db:foreignKey PredictionModel @db:varchar(50) - FK al modelo que se está entrenando
  status: string; // @db:varchar(20) - Estado: 'pending' (pendiente), 'running' (ejecutando), 'completed' (completado), 'failed' (fallido)
  startTime: Date; // @db:datetime - Hora de inicio del entrenamiento
  endTime?: Date; // @db:datetime - Hora de finalización del entrenamiento
  trainingLogs?: string; // @db:text - Logs del proceso de entrenamiento (salida de consola)
  errorMessage?: string; // @db:text - Mensaje de error si status = 'failed'
  dataPointsUsed: number; // @db:int @default(0) - Cantidad de registros históricos usados para entrenar
  validationScore: number; // @db:decimal(5,4) @default(0) - Score de validación del modelo
  createdAt: Date; // @db:datetime - Fecha de creación del trabajo
}

// ============= PREDICTION ENTITIES (Predicciones de Tráfico) =============

/**
 * TrafficPredictionEntity - Predicción de Tráfico
 * Almacena predicciones generadas por los modelos de ML para diferentes horizontes temporales
 */
export interface TrafficPredictionEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID único de la predicción
  modelId: string; // @db:foreignKey PredictionModel @db:varchar(50) - FK al modelo usado para predecir
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la predicción)
  predictionDate: Date; // @db:datetime - Fecha/hora para la que se hizo la predicción
  predictionHour: number; // @db:int - Hora específica predicha (0-23)
  predictedVehicleCount: number; // @db:int @default(0) - Cantidad predicha de vehículos
  predictedAvgSpeed: number; // @db:decimal(6,2) @default(0) - Velocidad predicha en km/h
  predictedDensityLevel: DensityLevelKey; // @db:varchar(20) - Nivel de densidad predicho (LOW, MEDIUM, HIGH, CRITICAL)
  confidence: number; // @db:decimal(5,4) - Confianza de la predicción (0-1, donde 1 = 100% confiable)
  predictionHorizon: number; // @db:int - Horizonte de predicción en horas adelante (1, 6, 12, 24, 48, etc.)
  actualVehicleCount?: number; // @db:int - Cantidad real (se llena después de que pase el tiempo)
  actualAvgSpeed?: number; // @db:decimal(6,2) - Velocidad real
  actualDensityLevel?: DensityLevelKey; // @db:varchar(20) - Nivel de densidad real
  predictionError?: number; // @db:decimal(10,4) - Error calculado después de obtener datos reales
  createdAt: Date; // @db:datetime - Fecha de creación de la predicción
  updatedAt?: Date; // @db:datetime - Fecha de actualización (cuando se compara con datos reales)
}

/**
 * BatchPredictionEntity - Lote de Predicciones
 * Almacena información sobre un batch de predicciones generadas para un rango de tiempo
 */
export interface BatchPredictionEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID del lote de predicciones
  modelId: string; // @db:foreignKey PredictionModel @db:varchar(50) - FK al modelo usado
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación del batch)
  predictionStartDate: Date; // @db:datetime - Fecha de inicio del rango de predicción
  predictionEndDate: Date; // @db:datetime - Fecha de fin del rango de predicción
  totalPredictions: number; // @db:int @default(0) - Total de predicciones generadas en el batch
  avgConfidence: number; // @db:decimal(5,4) @default(0) - Confianza promedio del batch
  status: string; // @db:varchar(20) - Estado: 'pending' (pendiente), 'completed' (completado), 'failed' (fallido)
  executionTime: number; // @db:int @default(0) - Tiempo de ejecución en milisegundos
  createdAt: Date; // @db:datetime - Fecha de creación del batch
}

// ============= PREDICTION ACCURACY ENTITIES (Precisión de Predicciones) =============

/**
 * PredictionAccuracyEntity - Precisión del Modelo
 * Almacena métricas de precisión calculadas comparando predicciones vs datos reales
 */
export interface PredictionAccuracyEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID del registro de precisión
  modelId: string; // @db:foreignKey PredictionModel @db:varchar(50) - FK al modelo evaluado
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación evaluada)
  evaluationPeriod: string; // @db:varchar(50) - Período de evaluación (Ej: "2024-01-01_2024-01-31")
  predictionHorizon: number; // @db:int - Horizonte evaluado en horas adelante (1, 6, 24, etc.)
  totalPredictions: number; // @db:int @default(0) - Total de predicciones evaluadas
  correctPredictions: number; // @db:int @default(0) - Predicciones correctas (con error < 5 vehículos)
  accuracy: number; // @db:decimal(5,4) @default(0) - Exactitud en porcentaje (0-1, donde 1 = 100%)
  avgError: number; // @db:decimal(10,4) @default(0) - Error promedio (MAE)
  maxError: number; // @db:decimal(10,4) @default(0) - Error máximo
  minError: number; // @db:decimal(10,4) @default(0) - Error mínimo
  evaluatedAt: Date; // @db:datetime - Fecha de evaluación
}

/**
 * RealTimePredictionEntity - Predicción en Tiempo Real (Caché)
 * Almacena las predicciones más recientes para acceso rápido (sin consultar todas las predicciones)
 */
export interface RealTimePredictionEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID de la predicción en tiempo real
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la predicción)
  currentVehicleCount: number; // @db:int @default(0) - Cantidad actual de vehículos (última medición)
  currentDensityLevel: DensityLevelKey; // @db:varchar(20) - Nivel de densidad actual
  next1HourPrediction: number; // @db:int @default(0) - Predicción para la próxima 1 hora
  next6HourPrediction: number; // @db:int @default(0) - Predicción para las próximas 6 horas
  next24HourPrediction: number; // @db:int @default(0) - Predicción para las próximas 24 horas
  confidence1Hour: number; // @db:decimal(5,4) @default(0) - Confianza de predicción a 1h
  confidence6Hour: number; // @db:decimal(5,4) @default(0) - Confianza de predicción a 6h
  confidence24Hour: number; // @db:decimal(5,4) @default(0) - Confianza de predicción a 24h
  lastUpdated: Date; // @db:datetime - Última actualización de las predicciones
  createdAt: Date; // @db:datetime - Fecha de creación
}

// ============= EXTERNAL FACTORS ENTITIES (Factores Externos) =============

/**
 * WeatherDataEntity - Datos Climáticos
 * Almacena información meteorológica que puede afectar el tráfico
 */
export interface WeatherDataEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID del registro de clima
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación del registro climático)
  date: Date; // @db:datetime - Fecha/hora del registro
  hour: number; // @db:int - Hora del registro (0-23)
  temperature: number; // @db:decimal(5,2) @default(0) - Temperatura en grados Celsius
  humidity: number; // @db:decimal(5,2) @default(0) - Humedad en porcentaje (0-100)
  precipitation: number; // @db:decimal(6,2) @default(0) - Precipitación en milímetros
  windSpeed: number; // @db:decimal(5,2) @default(0) - Velocidad del viento en km/h
  weatherCondition: string; // @db:varchar(50) - Condición: 'sunny' (soleado), 'rainy' (lluvioso), 'cloudy' (nublado), 'stormy' (tormenta)
  visibility: number; // @db:decimal(6,2) @default(10) - Visibilidad en kilómetros
  createdAt: Date; // @db:datetime - Fecha de creación
}

/**
 * EventDataEntity - Eventos Especiales
 * Almacena información sobre eventos que pueden afectar el tráfico (conciertos, partidos, feriados, accidentes, construcciones)
 */
export interface EventDataEntity {
  id: string; // @db:primary @db:varchar(50) @default(cuid()) - CUID del evento
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación del evento)
  eventName: string; // @db:varchar(200) - Nombre del evento (Ej: "Concierto Estadio Monumental")
  eventType: string; // @db:varchar(50) - Tipo: 'sports' (deportivo), 'concert' (concierto), 'holiday' (feriado), 'accident' (accidente), 'construction' (construcción)
  startDate: Date; // @db:datetime - Fecha/hora de inicio del evento
  endDate: Date; // @db:datetime - Fecha/hora de fin del evento
  expectedAttendance?: number; // @db:int - Asistencia esperada (número de personas)
  trafficImpact: string; // @db:varchar(20) - Impacto en el tráfico: 'low' (bajo), 'medium' (medio), 'high' (alto), 'critical' (crítico)
  createdAt: Date; // @db:datetime - Fecha de creación del registro
}


export interface PredictionSourceEntity {
  id: number; // @db:primary @db:identity - ID autoincremental
  createdAt: Date; // @db:datetime - Fecha de creación del registro
  locationId: number; // @db:foreignKey traffic_app.Location @db:int - FK a Location (ubicación de la cámara)
  cameraId: number; // @db:foreignKey traffic_app.Camera @db:int - FK a Camera (cámara específica)
  startedAt: Date; // @db:datetime - Fecha/hora de inicio del análisis
  endedAt: Date; // @db:datetime - Fecha/hora de fin del análisis
  totalVehicleCount: number; // @db:int @default(0) - Total de vehículos analizados
  avgSpeed: number; // @db:decimal(6,2) @default(0) - Velocidad promedio en km/h
  isActive: boolean; // @default(true) - Si la fuente está activa
}
