 
 export const DataTypeKey = {
   STRING: 'string',
   NUMBER: 'number',
   DATE: 'date',
   BOOLEAN: 'boolean',
} as const;

// to group by
  export const GroupByDataKey = {
   HOUR: 'hour' as const,
   DAY: 'day' as const,
   WEEK: 'week' as const,
   MONTH: 'month' as const,
 } as const;

  export type GroupByDataKey = typeof GroupByDataKey[keyof typeof GroupByDataKey];
  export type DataTypeKey = typeof DataTypeKey[keyof typeof DataTypeKey];
