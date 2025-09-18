import { z } from 'zod';
import { BoundingBoxSchema } from './traffic.schemas';

// Plate Detection Schemas
export const PlateDetectionSchema = z.object({
  id: z.string().uuid(),
  plateNumber: z.string().min(1, 'Número de placa es requerido'),
  confidence: z.number().min(0).max(1),
  boundingBox: BoundingBoxSchema,
  vehicleType: z.string().optional(),
  trafficAnalysisId: z.string().uuid(),
  createdAt: z.date()
});

export const CreatePlateDetectionSchema = z.object({
  plateNumber: z.string().min(1, 'Número de placa es requerido'),
  confidence: z.number().min(0).max(1),
  boundingBox: BoundingBoxSchema,
  vehicleType: z.string().optional(),
  trafficAnalysisId: z.string().uuid()
});

export const PlateSearchSchema = z.object({
  plateNumber: z.string().optional(),
  location: z.string().optional(),
  startDate: z.date().optional(),
  endDate: z.date().optional(),
  vehicleType: z.string().optional(),
  minConfidence: z.number().min(0).max(1).optional(),
  page: z.number().positive().optional(),
  limit: z.number().positive().max(100).optional()
});

export const CharacterDetectionSchema = z.object({
  character: z.string().length(1),
  confidence: z.number().min(0).max(1),
  position: BoundingBoxSchema
});

export const PlateRecognitionResultSchema = z.object({
  text: z.string().min(1),
  confidence: z.number().min(0).max(1),
  characters: z.array(CharacterDetectionSchema)
});

export const PlateAnalysisSchema = z.object({
  id: z.string().uuid(),
  plateNumber: z.string(),
  detectionCount: z.number().min(0),
  firstDetected: z.date(),
  lastDetected: z.date(),
  locations: z.array(z.string()),
  vehicleType: z.string().optional()
});

// Type exports
export type PlateDetectionSchemaType = z.infer<typeof PlateDetectionSchema>;
export type CreatePlateDetectionSchemaType = z.infer<typeof CreatePlateDetectionSchema>;
export type PlateSearchSchemaType = z.infer<typeof PlateSearchSchema>;
export type CharacterDetectionSchemaType = z.infer<typeof CharacterDetectionSchema>;
export type PlateRecognitionResultSchemaType = z.infer<typeof PlateRecognitionResultSchema>;
export type PlateAnalysisSchemaType = z.infer<typeof PlateAnalysisSchema>;