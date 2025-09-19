from rest_framework import serializers
from .models import TrafficAnalysis, TrafficReport


class TrafficAnalysisSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficAnalysis
        fields = "__all__"


class TrafficReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrafficReport
        fields = "__all__"
