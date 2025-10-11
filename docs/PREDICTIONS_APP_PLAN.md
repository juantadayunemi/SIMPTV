# 🔮 Predictions App - Plan de Implementación

## 📋 Descripción General

**App:** `apps.predictions_app`

Sistema de predicción de tráfico con Machine Learning que analiza datos históricos para pronosticar:
- 🚗 **Cantidad de vehículos** por hora/día/semana
- 📊 **Nivel de congestión** (LOW, MEDIUM, HIGH, CRITICAL)
- ⚠️ **Embotellamiento probable** (probabilidad de congestión)
- 🕐 **Horarios pico** para cada ubicación
- 📈 **Tendencias temporales** (patrones semanales, mensuales, anuales)

---

## 🎯 Objetivos

1. **Recolectar datos históricos** de `TrafficAnalysisEntity` automáticamente
2. **Entrenar modelos** de ML (LSTM, ARIMA, Random Forest) con datos históricos
3. **Generar predicciones** para 1h, 6h, 24h, 48h adelante
4. **Evaluar precisión** comparando predicciones vs. datos reales
5. **Servir predicciones** vía API REST para visualización en frontend
6. **Alertas automáticas** cuando se detecta probabilidad de embotellamiento

---

## 🏗️ Arquitectura

```
┌─────────────────────────────────────────────────────────────┐
│                    SHARED/ENTITIES                          │
│  predictionEntities.ts (con @db: annotations)              │
└────────────────────┬────────────────────────────────────────┘
                     ↓
         python manage.py generate_entities
                     ↓
┌─────────────────────────────────────────────────────────────┐
│              APPS/ENTITIES/MODELS                           │
│  prediction.py (modelos abstractos DLL)                    │
└────────────────────┬────────────────────────────────────────┘
                     ↓ herencia
┌─────────────────────────────────────────────────────────────┐
│            APPS/PREDICTIONS_APP                             │
│                                                             │
│  models.py          - Modelos concretos (heredan de DLL)   │
│  tasks.py           - Celery tasks para predicciones       │
│  ml/                - Lógica de Machine Learning           │
│    ├── models/      - Implementaciones de modelos ML       │
│    ├── training.py  - Entrenamiento de modelos             │
│    ├── prediction.py- Generación de predicciones           │
│    └── evaluation.py- Evaluación de precisión              │
│  serializers.py     - DRF Serializers                      │
│  views.py           - API ViewSets                         │
│  urls.py            - URL routing                          │
└─────────────────────────────────────────────────────────────┘
```

---

## 📊 Modelos de Datos (con @db: annotations)

### ✅ Ya completado en `predictionEntities.ts`

Las siguientes entidades tienen todas sus anotaciones @db: completas:

1. **TrafficHistoricalDataEntity** - Datos históricos agregados por hora
2. **LocationTrafficPatternEntity** - Patrones detectados (hourly, daily, weekly)
3. **PredictionModelEntity** - Modelos de ML entrenados
4. **ModelTrainingJobEntity** - Jobs de entrenamiento
5. **TrafficPredictionEntity** - Predicciones generadas
6. **BatchPredictionEntity** - Batches de predicciones
7. **PredictionAccuracyEntity** - Métricas de precisión
8. **RealTimePredictionEntity** - Predicciones en tiempo real (caché)
9. **WeatherDataEntity** - Datos climáticos (factor externo)
10. **EventDataEntity** - Eventos especiales (factor externo)

---

## 🔄 Flujo de Trabajo

### 1. **Recolección de Datos Históricos**

**Celery Task:** `collect_historical_data_task()`

- Se ejecuta cada hora (Celery Beat)
- Lee `TrafficAnalysisEntity` completados en la última hora
- Agrega datos por ubicación/hora
- Guarda en `TrafficHistoricalDataEntity`

```python
# apps/predictions_app/tasks.py
@shared_task
def collect_historical_data_task():
    """
    Agrega datos de TrafficAnalysis completados
    en la última hora y guarda en TrafficHistoricalData
    """
    from apps.traffic_app.models import TrafficAnalysis
    from .models import TrafficHistoricalData
    
    # Obtener análisis completados en última hora
    one_hour_ago = timezone.now() - timedelta(hours=1)
    analyses = TrafficAnalysis.objects.filter(
        status='COMPLETED',
        endedAt__gte=one_hour_ago
    )
    
    # Agrupar por ubicación + hora
    for location in set(a.locationId for a in analyses):
        hour_data = analyses.filter(locationId=location)
        
        # Calcular agregados
        avg_speed = hour_data.aggregate(Avg('avgSpeed'))['avgSpeed__avg']
        total_vehicles = hour_data.aggregate(Sum('totalVehicleCount'))['totalVehicleCount__sum']
        
        # Guardar en histórico
        TrafficHistoricalData.objects.create(
            location=f"LOC-{location}",
            date=timezone.now(),
            hour=timezone.now().hour,
            dayOfWeek=timezone.now().weekday(),
            month=timezone.now().month,
            vehicleCount=total_vehicles or 0,
            avgSpeed=avg_speed or 0,
            densityLevel=calculate_density(total_vehicles),
            isHoliday=is_holiday_today(),
            isWeekend=timezone.now().weekday() >= 5
        )
```

---

### 2. **Detección de Patrones**

**Celery Task:** `detect_traffic_patterns_task(location_id)`

- Se ejecuta diariamente (Celery Beat)
- Analiza datos históricos de los últimos 30 días
- Detecta patrones horarios, diarios, semanales
- Guarda en `LocationTrafficPatternEntity`

```python
@shared_task
def detect_traffic_patterns_task(location_id):
    """
    Detecta patrones de tráfico para una ubicación
    usando datos de los últimos 30 días
    """
    from .ml.training import PatternDetector
    from .models import TrafficHistoricalData, LocationTrafficPattern
    
    # Obtener datos históricos
    thirty_days_ago = timezone.now() - timedelta(days=30)
    historical_data = TrafficHistoricalData.objects.filter(
        location=f"LOC-{location_id}",
        date__gte=thirty_days_ago
    ).order_by('date', 'hour')
    
    # Detectar patrones
    detector = PatternDetector()
    patterns = detector.detect_patterns(historical_data)
    
    # Guardar patrones detectados
    for pattern_type, pattern_data in patterns.items():
        LocationTrafficPattern.objects.update_or_create(
            location=f"LOC-{location_id}",
            patternType=pattern_type,
            defaults={
                'patternData': json.dumps(pattern_data),
                'confidence': pattern_data.get('confidence', 0.8),
                'validFrom': timezone.now(),
                'validTo': timezone.now() + timedelta(days=30)
            }
        )
```

---

### 3. **Entrenamiento de Modelos**

**Celery Task:** `train_prediction_model_task(location_id, model_type)`

- Se ejecuta semanalmente o bajo demanda
- Entrena modelos con datos históricos (3-6 meses)
- Evalúa precisión con validación cruzada
- Guarda modelo entrenado en `PredictionModelEntity`

```python
@shared_task
def train_prediction_model_task(location_id, model_type='lstm'):
    """
    Entrena un modelo de predicción para una ubicación
    
    Args:
        location_id: ID de la ubicación
        model_type: 'lstm', 'arima', 'random_forest'
    """
    from .ml.training import ModelTrainer
    from .models import PredictionModel, ModelTrainingJob
    
    # Crear job de entrenamiento
    job = ModelTrainingJob.objects.create(
        modelId=generate_cuid(),
        status='running',
        startTime=timezone.now()
    )
    
    try:
        # Obtener datos de entrenamiento (6 meses)
        six_months_ago = timezone.now() - timedelta(days=180)
        training_data = TrafficHistoricalData.objects.filter(
            location=f"LOC-{location_id}",
            date__gte=six_months_ago
        )
        
        # Entrenar modelo
        trainer = ModelTrainer(model_type=model_type)
        model, metrics = trainer.train(training_data)
        
        # Guardar modelo
        prediction_model = PredictionModel.objects.create(
            id=job.modelId,
            modelName=f"{model_type.upper()}-LOC{location_id}-{timezone.now().strftime('%Y%m')}",
            modelType=model_type,
            location=f"LOC-{location_id}",
            features=json.dumps(trainer.feature_names),
            hyperparameters=json.dumps(trainer.hyperparameters),
            trainingDataPeriod=f"{six_months_ago.date()}_{timezone.now().date()}",
            accuracy=metrics['accuracy'],
            mse=metrics['mse'],
            mae=metrics['mae'],
            r2Score=metrics['r2_score'],
            trainedAt=timezone.now()
        )
        
        # Actualizar job
        job.status = 'completed'
        job.endTime = timezone.now()
        job.dataPointsUsed = training_data.count()
        job.validationScore = metrics['validation_score']
        job.save()
        
    except Exception as e:
        job.status = 'failed'
        job.errorMessage = str(e)
        job.endTime = timezone.now()
        job.save()
        raise
```

---

### 4. **Generación de Predicciones**

**Celery Task:** `generate_predictions_task(location_id, horizon_hours)`

- Se ejecuta cada hora (Celery Beat)
- Genera predicciones para 1h, 6h, 24h adelante
- Usa el modelo activo más reciente
- Guarda en `TrafficPredictionEntity`

```python
@shared_task
def generate_predictions_task(location_id, horizon_hours=[1, 6, 24]):
    """
    Genera predicciones de tráfico para una ubicación
    
    Args:
        location_id: ID de la ubicación
        horizon_hours: Lista de horizontes (horas adelante)
    """
    from .ml.prediction import TrafficPredictor
    from .models import PredictionModel, TrafficPrediction
    
    # Obtener modelo activo más reciente
    model = PredictionModel.objects.filter(
        location=f"LOC-{location_id}",
        isActive=True
    ).order_by('-trainedAt').first()
    
    if not model:
        logger.warning(f"No hay modelo activo para ubicación {location_id}")
        return
    
    # Cargar predictor
    predictor = TrafficPredictor(model)
    
    # Generar predicciones para cada horizonte
    for hours_ahead in horizon_hours:
        prediction_datetime = timezone.now() + timedelta(hours=hours_ahead)
        
        # Predecir
        result = predictor.predict(prediction_datetime)
        
        # Guardar predicción
        TrafficPrediction.objects.create(
            id=generate_cuid(),
            modelId=model.id,
            location=f"LOC-{location_id}",
            predictionDate=prediction_datetime,
            predictionHour=prediction_datetime.hour,
            predictedVehicleCount=result['vehicle_count'],
            predictedAvgSpeed=result['avg_speed'],
            predictedDensityLevel=result['density_level'],
            confidence=result['confidence'],
            predictionHorizon=hours_ahead
        )
```

---

### 5. **Evaluación de Precisión**

**Celery Task:** `evaluate_predictions_task(location_id)`

- Se ejecuta diariamente
- Compara predicciones pasadas con datos reales
- Calcula métricas de error (MAE, MSE)
- Guarda en `PredictionAccuracyEntity`

```python
@shared_task
def evaluate_predictions_task(location_id):
    """
    Evalúa precisión de predicciones comparando con datos reales
    """
    from .models import TrafficPrediction, TrafficHistoricalData, PredictionAccuracy
    
    # Obtener predicciones de hace 24 horas que ahora tienen datos reales
    yesterday = timezone.now() - timedelta(days=1)
    predictions = TrafficPrediction.objects.filter(
        location=f"LOC-{location_id}",
        predictionDate__date=yesterday.date(),
        actualVehicleCount__isnull=True  # Aún no se han actualizado
    )
    
    for prediction in predictions:
        # Buscar dato real
        actual_data = TrafficHistoricalData.objects.filter(
            location=prediction.location,
            date__date=prediction.predictionDate.date(),
            hour=prediction.predictionHour
        ).first()
        
        if actual_data:
            # Actualizar predicción con dato real
            prediction.actualVehicleCount = actual_data.vehicleCount
            prediction.actualAvgSpeed = actual_data.avgSpeed
            prediction.actualDensityLevel = actual_data.densityLevel
            prediction.predictionError = abs(
                prediction.predictedVehicleCount - actual_data.vehicleCount
            )
            prediction.save()
    
    # Calcular métricas agregadas del último mes
    one_month_ago = timezone.now() - timedelta(days=30)
    evaluated_predictions = TrafficPrediction.objects.filter(
        location=f"LOC-{location_id}",
        predictionDate__gte=one_month_ago,
        actualVehicleCount__isnull=False
    )
    
    if evaluated_predictions.exists():
        errors = [p.predictionError for p in evaluated_predictions if p.predictionError]
        
        PredictionAccuracy.objects.create(
            id=generate_cuid(),
            modelId=evaluated_predictions.first().modelId,
            location=f"LOC-{location_id}",
            evaluationPeriod=f"{one_month_ago.date()}_{timezone.now().date()}",
            predictionHorizon=24,  # Evaluar predicciones a 24h
            totalPredictions=evaluated_predictions.count(),
            correctPredictions=sum(1 for e in errors if e < 5),  # Error < 5 vehículos
            accuracy=sum(1 for e in errors if e < 5) / len(errors),
            avgError=sum(errors) / len(errors),
            maxError=max(errors),
            minError=min(errors),
            evaluatedAt=timezone.now()
        )
```

---

## 🤖 Implementación de Modelos ML

### Estructura de `ml/` module

```
apps/predictions_app/ml/
├── __init__.py
├── models/
│   ├── __init__.py
│   ├── lstm_model.py       # LSTM (Long Short-Term Memory)
│   ├── arima_model.py      # ARIMA (AutoRegressive Integrated Moving Average)
│   └── rf_model.py         # Random Forest
├── training.py             # ModelTrainer class
├── prediction.py           # TrafficPredictor class
├── evaluation.py           # ModelEvaluator class
└── utils.py                # Feature engineering, preprocessing
```

### Ejemplo: LSTM Model

```python
# apps/predictions_app/ml/models/lstm_model.py
import numpy as np
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout

class LSTMTrafficModel:
    def __init__(self, sequence_length=24, features=10):
        self.sequence_length = sequence_length
        self.features = features
        self.model = self._build_model()
    
    def _build_model(self):
        model = Sequential([
            LSTM(64, return_sequences=True, input_shape=(self.sequence_length, self.features)),
            Dropout(0.2),
            LSTM(32, return_sequences=False),
            Dropout(0.2),
            Dense(16, activation='relu'),
            Dense(1)  # Predicción de vehicleCount
        ])
        
        model.compile(
            optimizer='adam',
            loss='mse',
            metrics=['mae']
        )
        
        return model
    
    def train(self, X_train, y_train, epochs=50, batch_size=32):
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_split=0.2,
            verbose=1
        )
        return history
    
    def predict(self, X):
        return self.model.predict(X)
    
    def save(self, path):
        self.model.save(path)
    
    @classmethod
    def load(cls, path):
        from tensorflow.keras.models import load_model
        instance = cls()
        instance.model = load_model(path)
        return instance
```

---

## 🛠️ API Endpoints

### Endpoints de Predicciones

```python
# apps/predictions_app/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'predictions', views.TrafficPredictionViewSet)
router.register(r'models', views.PredictionModelViewSet)
router.register(r'historical', views.TrafficHistoricalDataViewSet)
router.register(r'accuracy', views.PredictionAccuracyViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('predict/<int:location_id>/', views.generate_prediction_view),
    path('train/<int:location_id>/', views.train_model_view),
]
```

### ViewSets

```python
# apps/predictions_app/views.py
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import TrafficPrediction, PredictionModel
from .serializers import TrafficPredictionSerializer, PredictionModelSerializer

class TrafficPredictionViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrafficPrediction.objects.all()
    serializer_class = TrafficPredictionSerializer
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        GET /api/predictions/predictions/by_location/?location=LOC-1&hours=24
        
        Retorna predicciones para una ubicación en las próximas N horas
        """
        location = request.query_params.get('location')
        hours_ahead = int(request.query_params.get('hours', 24))
        
        predictions = TrafficPrediction.objects.filter(
            location=location,
            predictionDate__gte=timezone.now(),
            predictionDate__lte=timezone.now() + timedelta(hours=hours_ahead)
        ).order_by('predictionDate')
        
        serializer = self.get_serializer(predictions, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def real_time(self, request):
        """
        GET /api/predictions/predictions/real_time/?location=LOC-1
        
        Retorna predicción en tiempo real (caché) con 1h, 6h, 24h adelante
        """
        location = request.query_params.get('location')
        
        prediction = RealTimePrediction.objects.filter(
            location=location
        ).order_by('-lastUpdated').first()
        
        if not prediction:
            return Response({'error': 'No predictions available'}, status=404)
        
        return Response({
            'location': prediction.location,
            'current': {
                'vehicleCount': prediction.currentVehicleCount,
                'densityLevel': prediction.currentDensityLevel
            },
            'predictions': {
                '1h': {
                    'vehicleCount': prediction.next1HourPrediction,
                    'confidence': prediction.confidence1Hour
                },
                '6h': {
                    'vehicleCount': prediction.next6HourPrediction,
                    'confidence': prediction.confidence6Hour
                },
                '24h': {
                    'vehicleCount': prediction.next24HourPrediction,
                    'confidence': prediction.confidence24Hour
                }
            },
            'lastUpdated': prediction.lastUpdated
        })

class PredictionModelViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = PredictionModel.objects.filter(isActive=True)
    serializer_class = PredictionModelSerializer
    
    @action(detail=False, methods=['get'])
    def by_location(self, request):
        """
        GET /api/predictions/models/by_location/?location=LOC-1
        
        Retorna el modelo activo para una ubicación
        """
        location = request.query_params.get('location')
        
        model = PredictionModel.objects.filter(
            location=location,
            isActive=True
        ).order_by('-trainedAt').first()
        
        if not model:
            return Response({'error': 'No model found'}, status=404)
        
        serializer = self.get_serializer(model)
        return Response(serializer.data)
```

---

## ⏰ Celery Beat Schedule

```python
# config/settings.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Recolectar datos históricos cada hora
    'collect-historical-data': {
        'task': 'apps.predictions_app.tasks.collect_historical_data_task',
        'schedule': crontab(minute=5),  # Cada hora a los 5 minutos
    },
    
    # Generar predicciones cada hora
    'generate-predictions': {
        'task': 'apps.predictions_app.tasks.generate_all_predictions',
        'schedule': crontab(minute=10),  # Cada hora a los 10 minutos
    },
    
    # Detectar patrones diariamente a las 2 AM
    'detect-patterns': {
        'task': 'apps.predictions_app.tasks.detect_all_patterns',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Evaluar precisión diariamente a las 3 AM
    'evaluate-predictions': {
        'task': 'apps.predictions_app.tasks.evaluate_all_predictions',
        'schedule': crontab(hour=3, minute=0),
    },
    
    # Re-entrenar modelos semanalmente (domingos a las 4 AM)
    'retrain-models': {
        'task': 'apps.predictions_app.tasks.retrain_all_models',
        'schedule': crontab(hour=4, minute=0, day_of_week=0),
    },
}
```

---

## 📦 Dependencias Adicionales

```txt
# requirements.txt (agregar)

# Machine Learning
tensorflow==2.15.0           # LSTM models
scikit-learn==1.3.2          # Random Forest, preprocessing
statsmodels==0.14.1          # ARIMA models
pandas==2.1.4                # Data manipulation
numpy==1.26.2                # Numerical computing

# Feature Engineering
holidays==0.38               # Detección de festivos
geopy==2.4.1                 # Geocoding (si necesario)

# Visualization (opcional, para debugging)
matplotlib==3.8.2
seaborn==0.13.0
```

---

## 🚀 Pasos de Implementación

### Fase 1: Setup Inicial ✅
1. ✅ Agregar anotaciones @db: a `predictionEntities.ts`
2. [ ] Ejecutar `python manage.py generate_entities`
3. [ ] Crear app: `python manage.py startapp predictions_app`
4. [ ] Agregar `"apps.predictions_app"` a `INSTALLED_APPS`
5. [ ] Crear modelos en `models.py` (heredar de DLL)
6. [ ] Ejecutar `python manage.py makemigrations predictions_app`
7. [ ] Ejecutar `python manage.py migrate`

### Fase 2: Recolección de Datos ✅
1. [ ] Implementar `collect_historical_data_task()`
2. [ ] Configurar Celery Beat schedule
3. [ ] Probar recolección manual con análisis existentes

### Fase 3: Modelos ML ✅
1. [ ] Crear estructura `ml/` module
2. [ ] Implementar `LSTMTrafficModel`
3. [ ] Implementar `ARIMATrafficModel`
4. [ ] Implementar `RandomForestModel`
5. [ ] Crear `ModelTrainer` class
6. [ ] Crear `TrafficPredictor` class

### Fase 4: Entrenamiento ✅
1. [ ] Implementar `train_prediction_model_task()`
2. [ ] Implementar `detect_traffic_patterns_task()`
3. [ ] Probar entrenamiento con datos sintéticos
4. [ ] Entrenar primer modelo real

### Fase 5: Predicciones ✅
1. [ ] Implementar `generate_predictions_task()`
2. [ ] Implementar caché de `RealTimePrediction`
3. [ ] Probar generación de predicciones

### Fase 6: API REST ✅
1. [ ] Crear serializers
2. [ ] Crear ViewSets
3. [ ] Configurar URLs
4. [ ] Documentar endpoints en Swagger

### Fase 7: Evaluación y Ajuste ✅
1. [ ] Implementar `evaluate_predictions_task()`
2. [ ] Crear dashboard de métricas
3. [ ] Ajustar hiperparámetros basado en resultados
4. [ ] Implementar re-entrenamiento automático

---

## 🎯 Casos de Uso

### 1. **Dashboard de Predicciones (Frontend)**

Usuario ve:
- Predicción de vehículos para próximas 1h, 6h, 24h
- Gráfico de tendencia semanal
- Alerta si se predice embotellamiento
- Horarios pico recomendados para evitar

**Endpoint:**
```http
GET /api/predictions/predictions/by_location/?location=LOC-1&hours=24

Response:
{
  "predictions": [
    {
      "predictionDate": "2025-10-10T15:00:00Z",
      "predictionHour": 15,
      "predictedVehicleCount": 45,
      "predictedDensityLevel": "MEDIUM",
      "confidence": 0.87
    },
    ...
  ]
}
```

### 2. **Alertas de Embotellamiento**

Sistema envía alerta si:
- Predicción de densityLevel = "CRITICAL" con confidence > 0.8
- En próximas 2 horas

**Celery Task:**
```python
@shared_task
def send_congestion_alerts():
    predictions = TrafficPrediction.objects.filter(
        predictionDate__gte=timezone.now(),
        predictionDate__lte=timezone.now() + timedelta(hours=2),
        predictedDensityLevel='CRITICAL',
        confidence__gte=0.8
    )
    
    for prediction in predictions:
        # Enviar notificación
        send_notification(
            title=f"⚠️ Embotellamiento Predicho",
            message=f"Se predice tráfico crítico en {prediction.location} a las {prediction.predictionHour}:00"
        )
```

### 3. **Re-entrenamiento Inteligente**

Si la precisión del modelo cae por debajo de 70% → re-entrenar automáticamente

```python
@shared_task
def check_model_accuracy_and_retrain():
    accuracies = PredictionAccuracy.objects.filter(
        evaluatedAt__gte=timezone.now() - timedelta(days=7)
    )
    
    for accuracy in accuracies:
        if accuracy.accuracy < 0.7:
            # Precisión muy baja, re-entrenar
            train_prediction_model_task.delay(
                location_id=extract_location_id(accuracy.location),
                model_type='lstm'
            )
```

---

## 📚 Recursos y Referencias

- **LSTM for Time Series:** https://www.tensorflow.org/tutorials/structured_data/time_series
- **ARIMA in Python:** https://www.statsmodels.org/stable/examples/notebooks/generated/tsa_arma.html
- **Scikit-learn:** https://scikit-learn.org/stable/modules/ensemble.html#random-forests
- **Traffic Forecasting Papers:** 
  - "Deep Learning for Traffic Prediction" (2019)
  - "LSTM Networks for Traffic Flow Prediction" (2020)

---

✅ **Plan de Predictions App Completo!**

🎯 **Próximo paso:** Generar entidades y crear la app Django.

**Comando:**
```bash
cd backend
python manage.py generate_entities
python manage.py startapp predictions_app apps/predictions_app
```

¿Procedo a generar las entidades? 🚀
