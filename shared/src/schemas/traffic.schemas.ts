import { z } from 'zod';
import { ANALYSIS_STATUS, DENSITY_LEVELS, VEHICLE_TYPES } from '../types/trafficTypes';


// Traffic Analysis Schemas
export const BoundingBoxSchema = z.object({
  x: z.number().min(0),
  y: z.number().min(0),
  width: z.number().positive(),
  height: z.number().positive()
});


function createVehicleTypeEnum<T extends Record<string, string>>(obj: T) {
  return z.enum(Object.values(obj) as [string, ...string[]]);
}

export const VehicleDetectionSchema = z.object({
  id: z.string().uuid(),
  type: createVehicleTypeEnum(VEHICLE_TYPES),
  confidence: z.number().min(0).max(1),
  boundingBox: BoundingBoxSchema,
  speed: z.number().optional(),
  timestamp: z.date()
});


function createDensityLevelEnum<T extends Record<string, string>>(obj: T) {
  return z.enum(Object.values(obj) as [string, ...string[]]);
}


export const TrafficDataSchema = z.object({
  totalVehicles: z.number().min(0),
  vehicleTypes: z.array(z.object({
    type: createVehicleTypeEnum(VEHICLE_TYPES),
    count: z.number().min(0)
  })),
  avgSpeed: z.number().min(0),
  peakHours: z.array(z.object({
    startTime: z.string(),
    endTime: z.string(),
    vehicleCount: z.number().min(0)
  })),
  densityLevel: createDensityLevelEnum(DENSITY_LEVELS),
  weatherConditions: z.string().optional()
});


function createTrafficStatusEnum<T extends Record<string, string>>(obj: T) {
  return z.enum(Object.values(obj) as [string, ...string[]]);
}


export const TrafficAnalysisSchema = z.object({
  id: z.string().uuid(),
  location: z.string().min(1, 'Ubicación es requerida'),
  videoPath: z.string().optional(),
  vehicleCount: z.number().min(0),
  analysisData: TrafficDataSchema.optional(),
  status: createTrafficStatusEnum(ANALYSIS_STATUS),
  createdAt: z.date()
});

export const CreateTrafficAnalysisSchema = z.object({
  location: z.string().min(1, 'Ubicación es requerida'),
  videoPath: z.string().optional()
});

export const UpdateTrafficAnalysisSchema = z.object({
  location: z.string().min(1).optional(),
  status: createTrafficStatusEnum(ANALYSIS_STATUS).optional(),
  analysisData: TrafficDataSchema.optional()
});

// Type exports
export type BoundingBoxSchemaType = z.infer<typeof BoundingBoxSchema>;
export type VehicleDetectionSchemaType = z.infer<typeof VehicleDetectionSchema>;
export type TrafficDataSchemaType = z.infer<typeof TrafficDataSchema>;
export type TrafficAnalysisSchemaType = z.infer<typeof TrafficAnalysisSchema>;
export type CreateTrafficAnalysisSchemaType = z.infer<typeof CreateTrafficAnalysisSchema>;
export type UpdateTrafficAnalysisSchemaType = z.infer<typeof UpdateTrafficAnalysisSchema>;