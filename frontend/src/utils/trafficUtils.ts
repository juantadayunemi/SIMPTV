import { BottleneckData } from '@/types/bottlenecl';

export const getStatusColor = (status: string): string => {
  switch (status) {
    case 'Fluido':
      return 'text-green-600';
    case 'Denso':
      return 'text-yellow-600';
    case 'Embotellamiento':
      return 'text-red-600';
    default:
      return 'text-gray-600';
  }
};

export const getStatusBgColor = (status: string): string => {
  switch (status) {
    case 'Fluido':
      return 'bg-green-50';
    case 'Denso':
      return 'bg-yellow-50';
    case 'Embotellamiento':
      return 'bg-red-50';
    default:
      return 'bg-gray-50';
  }
};

export const filterDataByTime = (data: BottleneckData[], time: string): BottleneckData | undefined => {
  return data.find(item => item.ds === time);
};

export const generateTimeSlots = (): string[] => {
  const slots: string[] = [];
  for (let hour = 0; hour < 24; hour++) {
    for (let minute = 0; minute < 60; minute += 60) {
      const timeString = `${hour.toString().padStart(2, '0')}:${minute.toString().padStart(2, '0')}`;
      slots.push(timeString);
    }
  }
  return slots;
};
