import { z } from 'zod';
import { USER_ROLES } from '../types/roleTypes';


// Auth Schemas
export const LoginSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Password debe tener al menos 6 caracteres')
});

export const RegisterSchema = z.object({
  email: z.string().email('Email inválido'),
  password: z.string().min(6, 'Password debe tener al menos 6 caracteres'),
  confirmPassword: z.string()
}).refine((data) => data.password === data.confirmPassword, {
  message: "Las contraseñas no coinciden",
  path: ["confirmPassword"]
});

function createZodEnum<T extends Record<string, string>>(obj: T) {
  return z.enum(Object.values(obj) as [string, ...string[]]);
}

export const UserSchema = z.object({
  id: z.string().uuid(),
  email: z.string().email(),
  role: createZodEnum(USER_ROLES),
  isActive: z.boolean(),
  createdAt: z.date(),
  updatedAt: z.date()
});

export const TokenPayloadSchema = z.object({
  sub: z.string(),
  email: z.string().email(),
  role: z.string(),
  exp: z.number(),
  iat: z.number()
});

// Type exports for runtime validation
export type LoginSchemaType = z.infer<typeof LoginSchema>;
export type RegisterSchemaType = z.infer<typeof RegisterSchema>;
export type UserSchemaType = z.infer<typeof UserSchema>;
export type TokenPayloadSchemaType = z.infer<typeof TokenPayloadSchema>;