import React from 'react';

export const PredictionsPage: React.FC = () => {
  return (
    <div className="space-y-6">
      {/* Page Header */}
      <div>
        <h1 className="text-2xl font-bold text-gray-900">Análisis de Predicciones</h1>
        <p className="text-gray-600">Predicciones de tráfico basadas en Machine Learning</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 gap-5 sm:grid-cols-2 lg:grid-cols-4">
        {/* Accuracy */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🎯</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Precisión del Modelo
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    94.2%
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Predictions Today */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">📊</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Predicciones Hoy
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    847
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Active Models */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">🤖</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Modelos Activos
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    5
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>

        {/* Last Update */}
        <div className="bg-white overflow-hidden shadow rounded-lg">
          <div className="p-5">
            <div className="flex items-center">
              <div className="flex-shrink-0">
                <span className="text-2xl">⏰</span>
              </div>
              <div className="ml-5 w-0 flex-1">
                <dl>
                  <dt className="text-sm font-medium text-gray-500 truncate">
                    Última Actualización
                  </dt>
                  <dd className="text-lg font-medium text-gray-900">
                    2 min
                  </dd>
                </dl>
              </div>
            </div>
          </div>
        </div>
      </div>

      {/* Predictions Content */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Traffic Density Prediction */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Predicción de Densidad de Tráfico</h3>
            <p className="text-sm text-gray-500 mt-1">Próximas 24 horas</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {[
                { time: '08:00 - 10:00', density: 'Alta', confidence: '92%', color: 'red' },
                { time: '12:00 - 14:00', density: 'Media', confidence: '87%', color: 'yellow' },
                { time: '17:00 - 19:00', density: 'Alta', confidence: '94%', color: 'red' },
                { time: '22:00 - 24:00', density: 'Baja', confidence: '89%', color: 'green' },
              ].map((prediction, index) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className={`w-3 h-3 rounded-full ${
                      prediction.color === 'red' ? 'bg-red-500' :
                      prediction.color === 'yellow' ? 'bg-yellow-500' : 'bg-green-500'
                    }`}></div>
                    <div>
                      <p className="text-sm font-medium text-gray-900">{prediction.time}</p>
                      <p className="text-xs text-gray-500">Densidad {prediction.density}</p>
                    </div>
                  </div>
                  <span className="text-sm text-gray-600">Confianza: {prediction.confidence}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        {/* Model Performance */}
        <div className="bg-white shadow rounded-lg">
          <div className="px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-medium text-gray-900">Rendimiento de Modelos</h3>
            <p className="text-sm text-gray-500 mt-1">Métricas de evaluación</p>
          </div>
          <div className="p-6">
            <div className="space-y-4">
              {[
                { model: 'Traffic Density Predictor', accuracy: '94.2%', lastTrained: '2 días' },
                { model: 'Plate Detection Model', accuracy: '97.8%', lastTrained: '1 semana' },
                { model: 'Vehicle Count Estimator', accuracy: '91.5%', lastTrained: '3 días' },
                { model: 'Flow Pattern Analyzer', accuracy: '89.3%', lastTrained: '1 día' },
              ].map((model, index) => (
                <div key={index} className="border border-gray-200 rounded-lg p-4">
                  <div className="flex items-center justify-between mb-2">
                    <h4 className="text-sm font-medium text-gray-900">{model.model}</h4>
                    <span className="text-sm font-semibold text-green-600">{model.accuracy}</span>
                  </div>
                  <p className="text-xs text-gray-500">Último entrenamiento: hace {model.lastTrained}</p>
                  <div className="mt-2 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-600 h-2 rounded-full" 
                      style={{ width: model.accuracy }}
                    ></div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      {/* Recent Predictions */}
      <div className="bg-white shadow rounded-lg">
        <div className="px-6 py-4 border-b border-gray-200">
          <h3 className="text-lg font-medium text-gray-900">Predicciones Recientes</h3>
          <p className="text-sm text-gray-500 mt-1">Últimas predicciones generadas</p>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Fecha/Hora
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Tipo de Predicción
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Resultado
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Confianza
                </th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Estado
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {[
                {
                  datetime: '2025-09-18 14:30',
                  type: 'Densidad de Tráfico',
                  result: 'Tráfico Alto esperado a las 17:00',
                  confidence: '94%',
                  status: 'Completado'
                },
                {
                  datetime: '2025-09-18 14:25',
                  type: 'Conteo de Vehículos',
                  result: '450 vehículos/hora estimados',
                  confidence: '91%',
                  status: 'Completado'
                },
                {
                  datetime: '2025-09-18 14:20',
                  type: 'Patrón de Flujo',
                  result: 'Congestión en Av. Principal',
                  confidence: '88%',
                  status: 'En proceso'
                },
                {
                  datetime: '2025-09-18 14:15',
                  type: 'Detección de Incidentes',
                  result: 'Sin incidentes detectados',
                  confidence: '96%',
                  status: 'Completado'
                },
              ].map((prediction, index) => (
                <tr key={index}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.datetime}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    {prediction.type}
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-900">
                    {prediction.result}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className="inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-800">
                      {prediction.confidence}
                    </span>
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                    <span className={`inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium ${
                      prediction.status === 'Completado' 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-yellow-100 text-yellow-800'
                    }`}>
                      {prediction.status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

export default PredictionsPage;