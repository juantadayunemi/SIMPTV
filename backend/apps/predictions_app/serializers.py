from apps.traffic_app import serializers
from rest_framework import serializers
from apps.predictions_app.models import NotificationBottleNeck


class NotificationBottleNeckSerializer(serializers.ModelSerializer):
    class Meta:
        model = NotificationBottleNeck
        exclude = ["userId", "createdAt"]
