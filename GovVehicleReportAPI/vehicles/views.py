from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from .models import Vehicle


# view to get vehicle by placa,
def get_vehicle(request):
    placa = request.GET.get("placa")
    if not placa:
        return JsonResponse({"error": "Parameter placa required"}, status=400)

    try:
        vehicle = Vehicle.objects.get(pk=placa)
    except Vehicle.DoesNotExist:
        return JsonResponse(
            {"found": False, "message": "Placa no encontrada"}, status=404
        )

    # Return list of denuncias as objects with text and severidad (stored as uppercase in DB)
    denuncias = [
        {"denuncia": d.denuncia, "severidad": getattr(d, "severidad", "MEDIUM")}
        for d in vehicle.denuncias.all()
    ]  # type: ignore

    response = {
        "placa": vehicle.placa,
        "propietario": {
            "nombre": vehicle.propietario_nombre,
            "cedula": vehicle.propietario_cedula,
        },
        "ubicacion": {"direccion": vehicle.ubicacion_direccion},
        "denuncias": denuncias,
        "expediente": vehicle.expediente,
    }
    return JsonResponse(response)
