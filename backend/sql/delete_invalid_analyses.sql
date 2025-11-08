-- Script para eliminar análisis de tráfico con datos inválidos
-- Elimina análisis con menos de 10 vehículos (datos de prueba que no son realistas)

BEGIN TRANSACTION;

-- Mostrar cuántos análisis se van a eliminar
SELECT 
    COUNT(*) AS total_to_delete,
    MIN(totalVehicles) AS min_vehicles,
    MAX(totalVehicles) AS max_vehicles
FROM traffic_analyses
WHERE totalVehicles < 10;

-- Eliminar primero las referencias en otras tablas para evitar errores de FK
-- 1. Eliminar vehículos asociados a estos análisis
DELETE FROM traffic_vehicles
WHERE trafficAnalysisId IN (
    SELECT id 
    FROM traffic_analyses 
    WHERE totalVehicles < 10
);

-- 2. Eliminar frames de vehículos (si existen)
DELETE FROM traffic_vehicle_frames
WHERE vehicleId IN (
    SELECT v.id 
    FROM traffic_vehicles v
    INNER JOIN traffic_analyses a ON v.trafficAnalysisId = a.id
    WHERE a.totalVehicles < 10
);

-- 3. Actualizar cámaras que tengan referencia a estos análisis
UPDATE traffic_cameras
SET currentAnalysisId = NULL
WHERE currentAnalysisId IN (
    SELECT id 
    FROM traffic_analyses 
    WHERE totalVehicles < 10
);

-- 4. Finalmente, eliminar los análisis inválidos
DELETE FROM traffic_analyses
WHERE totalVehicles < 10;

-- Mostrar resumen de lo que quedó
SELECT 
    COUNT(*) AS remaining_analyses,
    MIN(totalVehicles) AS min_vehicles,
    MAX(totalVehicles) AS max_vehicles,
    AVG(totalVehicles) AS avg_vehicles
FROM traffic_analyses;

-- Si todo se ve bien, hacer commit
-- Si algo salió mal, hacer rollback
COMMIT;
-- ROLLBACK;

-- Verificar los análisis más recientes después de la limpieza
SELECT TOP 10
    id,
    cameraId,
    totalVehicles,
    avgSpeed,
    densityLevel,
    status,
    endedAt
FROM traffic_analyses
ORDER BY endedAt DESC;
