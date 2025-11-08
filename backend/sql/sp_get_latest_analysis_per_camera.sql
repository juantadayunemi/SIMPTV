-- Stored Procedure: Get Latest Traffic Analysis per Camera
-- Returns the most recent completed traffic analysis for each active camera
-- with location details and vehicle counts
-- Calculates avgSpeed from vehicles table

CREATE OR ALTER PROCEDURE sp_get_latest_analysis_per_camera
AS
BEGIN
    SET NOCOUNT ON;

    SELECT 
        a.id AS analysisId,
        a.cameraId,
        c.name AS cameraName,
        a.locationId,
        l.city,
        l.description AS locationDescription,
        a.videoPath,
        -- Calcular velocidad promedio desde la tabla de vehículos
        COALESCE(
            (SELECT AVG(v.avgSpeed) 
             FROM traffic_vehicles v 
             WHERE v.trafficAnalysisId = a.id 
             AND v.avgSpeed IS NOT NULL 
             AND v.avgSpeed > 0),
            a.avgSpeed,
            0
        ) AS avgSpeed,
        a.status,
        a.densityLevel,
        a.endedAt,
        a.totalVehicles,
        a.carCount,
        a.truckCount,
        a.motorcycleCount,
        a.busCount,
        a.bicycleCount,
        a.otherCount
    FROM traffic_analyses AS a
    INNER JOIN (
        SELECT 
            cameraId,
            MAX(id) AS maxId
        FROM traffic_analyses
        WHERE status = 'COMPLETED'
        GROUP BY cameraId
    ) AS latest ON a.id = latest.maxId
    LEFT JOIN traffic_cameras AS c ON a.cameraId = c.id
    LEFT JOIN traffic_locations AS l ON a.locationId = l.id
    WHERE c.status = 'ACTIVE'
    ORDER BY a.endedAt DESC;
END;
GO
