 
export const DATA_TYPES = {
  STRING: 'string' as const,
  NUMBER: 'number' as const,
  DATE: 'date' as const,
  BOOLEAN: 'boolean' as const,
} as const;

export type DataTypeKey = typeof DATA_TYPES[keyof typeof DATA_TYPES];

// to group by
export const GROUP_BY_DATA = {
  HOUR: 'hour' as const,
  DAY: 'day' as const,
  WEEK: 'week' as const,
  MONTH: 'month' as const,
} as const;

export type GroupByDataKey = typeof GROUP_BY_DATA[keyof typeof GROUP_BY_DATA];
