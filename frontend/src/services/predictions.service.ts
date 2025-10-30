import { ForecastData, ImpactMetrics, PeriodComparison } from '../types/forecast';

const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:3000/api';

export async function fetchForecast(
  location: string,
  date: string,
  time: string
): Promise<ForecastData[]> {
  try {
    const response = await fetch(
      `${BACKEND_URL}/forecast?location=${location}&date=${date}&time=${time}`
    );

    if (!response.ok) {
      throw new Error('Error fetching forecast data');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching forecast:', error);
    return generateMockForecast();
  }
}

export async function fetchImpactMetrics(
  location: string,
  date: string
): Promise<ImpactMetrics> {
  try {
    const response = await fetch(
      `${BACKEND_URL}/impact?location=${location}&date=${date}`
    );

    if (!response.ok) {
      throw new Error('Error fetching impact metrics');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching impact metrics:', error);
    return {
      holidays_impact: -15.3,
      seasonality_impact: 8.7
    };
  }
}

export async function fetchPeriodComparison(
  location: string,
  date: string,
  time: string,
  period: 'day' | 'month' | 'year'
): Promise<PeriodComparison> {
  try {
    const response = await fetch(
      `${BACKEND_URL}/comparison?location=${location}&date=${date}&time=${time}&period=${period}`
    );

    if (!response.ok) {
      throw new Error('Error fetching period comparison');
    }

    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching comparison:', error);
    return generateMockComparison(period);
  }
}

function generateMockForecast(): ForecastData[] {
  const data: ForecastData[] = [];
  const baseVehicles = 150;

  for (let hour = 0; hour < 24; hour++) {
    let vehicles = baseVehicles;

    if (hour >= 6 && hour <= 9) {
      vehicles += 50 + Math.random() * 30;
    } else if (hour >= 18 && hour <= 21) {
      vehicles += 40 + Math.random() * 25;
    } else if (hour >= 0 && hour <= 5) {
      vehicles -= 80 + Math.random() * 20;
    }

    vehicles += (Math.random() - 0.5) * 20;

    data.push({
      timestamp: `${hour.toString().padStart(2, '0')}:00`,
      yhat: vehicles,
      trend: vehicles * 0.9,
      seasonality: (Math.sin(hour / 24 * Math.PI * 2) * 20),
      holidays: -5,
      vehicles_per_hour: Math.round(vehicles),
      confidence_level: 75 + Math.random() * 15
    });
  }

  return data;
}

function generateMockComparison(period: 'day' | 'month' | 'year'): PeriodComparison {
  const ranges = {
    day: { min: -5, max: 5 },
    month: { min: -15, max: 15 },
    year: { min: -25, max: 25 }
  };

  const range = ranges[period];

  return {
    yhat_change: (Math.random() * (range.max - range.min) + range.min),
    trend_change: (Math.random() * (range.max - range.min) + range.min)
  };
}
