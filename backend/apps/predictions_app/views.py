from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from apps.predictions_app.services.prediction_service import get_traffic_prediction


class PredictionView(APIView):
    """
    Endpoint: /api/predictions/traffic-predictions/?locationId=<id>&date=<date>&hour=<hour>&minute=<minute>
    &periodsType=<periodsType>
    """

    def get(self, request):
        try:
            result = get_traffic_prediction(request.query_params)

            return Response(result, status=status.HTTP_200_OK)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print(f"Error en PredictionView: {e}")
            return Response(
                {
                    "error": "Ocurrió un error al obtener las predicciones.",
                    "details": str(e),
                },
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )
