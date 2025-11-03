import { DateRangeType, DateRange } from '../types/historyTraffic';

export function getDateRangeFromType(type: DateRangeType): DateRange | null {
  const today = new Date();
  const dateTo = getLocalDateString(today);

  switch (type) {
    case 'today':
      return { dateFrom: dateTo, dateTo };

    case '7days': {
      const date7DaysAgo = new Date(today);
      date7DaysAgo.setDate(today.getDate() - 7);
      return { dateFrom: date7DaysAgo.toISOString().split('T')[0], dateTo };
    }

    case '30days': {
      const date30DaysAgo = new Date(today);
      date30DaysAgo.setDate(today.getDate() - 30);
      return { dateFrom: date30DaysAgo.toISOString().split('T')[0], dateTo };
    }

    case 'custom':
      return null;

    default:
      return null;
  }
}

export function formatDateForDisplay(dateStr: string): string {
  const date = new Date(dateStr);
  return date.toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'long',
    day: 'numeric'
  });
}


export function getNextDate(date: Date): string {
  const tomorrow = new Date(date);
  tomorrow.setDate(date.getDate() + 1);

  return tomorrow.toLocaleDateString('en-CA', { timeZone: 'America/Guayaquil' });
}

export function getLocalDateString(date: Date): string {
  return date.toLocaleDateString('en-CA', { timeZone: 'America/Guayaquil' });
}