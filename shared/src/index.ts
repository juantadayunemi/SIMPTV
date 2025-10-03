// Main exports for the shared library - Nueva estructura organizada

//----- MODELOS -----
export * from './models/queries';
export * from './models/trafficModels';
export * from './models/plateModels';
export * from './models/notificatiosModels';   
export * from './models/authModels';   

//----- TIPOS -----
export * from './types/roleTypes';
export * from './types/trafficTypes';
export * from './types/notificationTypes';
export * from './types/dataTypes';      

// ----- ENTIDADES -----
export * from './entities/indexEntities';

// ----- SCHEMAS -----
export * from './schemas/auth.schemas';
export * from './schemas/traffic.schemas';
export * from './schemas/plate.schemas';

// ----- DTOs NUEVOS (RECOMENDADOS) ----- 
export * from './dto/trafficDto';
export * from './dto/plateDto';
export * from './dto/commonDto';

// ----- DTOs LEGACY (COMPATIBILIDAD) ----- 
export * from './dto/responseDto';
export * from './dto/requestDto';   



