# 🔄 TRAFSMART ENTITIES SYNC REPORT
**Generated:** 2025-10-13 01:05:15

---

## 📊 Summary

- 🆕 **New Fields:** 90
- 🗑️ **Removed Fields:** 0
- ✏️ **Modified Fields:** 0
- 🆕 **New Models:** 0
- 🗑️ **Removed Models:** 0

## 🆕 New Fields Added

- **NotificationPayload.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationPayload.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficAnalysisEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **TrafficAnalysisEntity.isPlaying**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **TrafficAnalysisEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisEntity.isPaused**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **TrafficAnalysisEntity.currentTimestamp**
  - TypeScript Type: `number`
  - Django Field: `IntegerField`

- **EventDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleEntity.plateConfidence**
  - TypeScript Type: `number`
  - Django Field: `DecimalField`

- **VehicleEntity.detectedPlate**
  - TypeScript Type: `string`
  - Django Field: `CharField`

- **LocationEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **LocationEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **LocationEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetection.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetection.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **NotificationDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **ModelTrainingJobEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **RealtimeNotificationDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **RealtimeNotificationDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PredictiveAnalysis.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PredictiveAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **CameraStatsResponseDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **CameraStatsResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **UserDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **NotificationSettingsEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationSettingsEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **TrafficAnalysisResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **BatchPredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleDetectionResponseDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **CreateVehicleDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **NotificationEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **VehicleFrameResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **PlateDetectionResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **PlateAlertEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PlateAlertEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateAlertEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateAlertEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **Permission.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserInfoDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserInfoDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserInfoDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **VehicleDetection.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **LicensePlateEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LicensePlateEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LicensePlateEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CustomerEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserQueryDto.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PlateAlertQueryDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserRoleEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserRoleEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PredictionModelEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PredictionModelEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserSearchQuery.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PlateDetectionDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetectionDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficHistoricalDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficHistoricalDataEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **FileUploadResponseDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UpdatePlateAlertRequestDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **TrafficPredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficPredictionEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **RealTimePredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleFrameEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleFrameEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **UserEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficAnalysis.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PlateAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **WeatherDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationTemplate.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PlateAlertResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CameraEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **CameraEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **CameraEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CameraEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationTrafficPatternEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationTrafficPatternEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **LocationTrafficPatternEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

---

## ✅ Next Steps

1. **Review Changes:** Check the changes above
2. **Generate Migrations:** Run `python manage.py makemigrations`
3. **Review Migrations:** Check generated migration files
4. **Apply Migrations:** Run `python manage.py migrate`
5. **Test:** Verify everything works correctly
