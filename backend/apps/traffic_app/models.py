from django.db import models


class TrafficAnalysis(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    video = models.FileField(upload_to="traffic_videos/")
    result = models.JSONField(default=dict)
    status = models.CharField(max_length=32, default="pending")
    # Puedes agregar más campos según necesidades


class TrafficReport(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    analysis = models.ForeignKey(TrafficAnalysis, on_delete=models.CASCADE)
    report_data = models.JSONField(default=dict)
