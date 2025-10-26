# 🔄 TRAFSMART ENTITIES SYNC REPORT
**Generated:** 2025-10-25 13:56:49

---

## 📊 Summary

- 🆕 **New Fields:** 93
- 🗑️ **Removed Fields:** 0
- ✏️ **Modified Fields:** 0
- 🆕 **New Models:** 0
- 🗑️ **Removed Models:** 0

## 🆕 New Fields Added

- **PlateAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PredictionModelEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PredictionModelEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserQueryDto.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **CustomerEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **NotificationSettingsEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationSettingsEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CreateVehicleDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserInfoDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserInfoDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserInfoDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **RealTimePredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisEntity.isPlaying**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **TrafficAnalysisEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisEntity.currentTimestamp**
  - TypeScript Type: `number`
  - Django Field: `IntegerField`

- **TrafficAnalysisEntity.isPaused**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **TrafficAnalysisEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **PlateDetectionDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetectionDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **VehicleDetection.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficAnalysis.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficAnalysisResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **EventDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **RealtimeNotificationDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **RealtimeNotificationDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **VehicleEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleEntity.plateConfidence**
  - TypeScript Type: `number`
  - Django Field: `DecimalField`

- **VehicleEntity.detectedPlate**
  - TypeScript Type: `string`
  - Django Field: `CharField`

- **CameraStatsResponseDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **CameraStatsResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **VehicleDetectionResponseDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PredictiveAnalysis.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PredictiveAnalysis.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **ModelTrainingJobEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficHistoricalDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficHistoricalDataEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CameraEntity.thumbnailPath**
  - TypeScript Type: `string`
  - Django Field: `CharField`

- **CameraEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **CameraEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **CameraEntity.currentVideoPath**
  - TypeScript Type: `string`
  - Django Field: `CharField`

- **CameraEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **CameraEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **CameraEntity.currentAnalysisId**
  - TypeScript Type: `number`
  - Django Field: `ForeignKey`

- **FileUploadResponseDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **UserSearchQuery.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PlateAlertQueryDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **LocationEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **LocationEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **NotificationEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **VehicleFrameEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **VehicleFrameEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **TrafficAnalysisDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficAnalysisDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PlateDetectionResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **LicensePlateEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LicensePlateEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LicensePlateEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **NotificationPayload.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationPayload.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **BatchPredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **WeatherDataEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateAlertResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **NotificationTemplate.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **LocationTrafficPatternEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationTrafficPatternEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **LocationTrafficPatternEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **UserDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **UserDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **VehicleFrameResponseDTO.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **UpdatePlateAlertRequestDTO.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **NotificationDTO.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **NotificationDTO.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **Permission.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **TrafficPredictionEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **TrafficPredictionEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetection.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateDetection.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

- **PlateAlertEntity.updatedAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateAlertEntity.createdAt**
  - TypeScript Type: `Date`
  - Django Field: `DateTimeField`

- **PlateAlertEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **PlateAlertEntity.id**
  - TypeScript Type: `number`
  - Django Field: `BigAutoField`

- **UserRoleEntity.isActive**
  - TypeScript Type: `boolean`
  - Django Field: `BooleanField`

- **UserRoleEntity.id**
  - TypeScript Type: `string`
  - Django Field: `UUIDField`

---

## ✅ Next Steps

1. **Review Changes:** Check the changes above
2. **Generate Migrations:** Run `python manage.py makemigrations`
3. **Review Migrations:** Check generated migration files
4. **Apply Migrations:** Run `python manage.py migrate`
5. **Test:** Verify everything works correctly
