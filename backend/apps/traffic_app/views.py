from rest_framework import viewsets, status
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import TrafficAnalysis, TrafficReport
from .serializers import TrafficAnalysisSerializer, TrafficReportSerializer


class TrafficAnalysisViewSet(viewsets.ModelViewSet):
    queryset = TrafficAnalysis.objects.all()
    serializer_class = TrafficAnalysisSerializer


class TrafficReportViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = TrafficReport.objects.all()
    serializer_class = TrafficReportSerializer


class TrafficMonitoringView(APIView):
    def get(self, request):
        # Simulación de dashboard
        return Response({"monitoring": "ok"})


class TrafficStatisticsView(APIView):
    def get(self, request):
        # Simulación de estadísticas
        return Response({"statistics": "ok"})


class TrafficUploadVideoView(APIView):
    def post(self, request):
        # Simulación de subida de video
        return Response({"upload": "ok"})
