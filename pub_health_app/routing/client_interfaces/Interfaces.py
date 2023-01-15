from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..buisness_logic.router import Router
from ..models import EmergencyVehicle
from ..serializers import EmergencyVehicleSerializer, EmergencySerializer

router = Router()


@api_view(['POST'])
def get_map(request):
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
def update_emergency_vehicle(request):
    emergency_vehicle_serializer = EmergencyVehicleSerializer(data=request.data)
    if emergency_vehicle_serializer.is_valid():
        emergency_vehicle = None
        try:
            emergency_vehicle = EmergencyVehicle.objects.get(
                call_name=emergency_vehicle_serializer.validated_data['call_name'])
        except EmergencyVehicle.DoesNotExist:
            emergency_vehicle = emergency_vehicle_serializer.save()
        emergency_vehicle.last_ping = timezone.now()
        emergency_vehicle.save()
        response = HttpResponse(router.update_map(), content_type="image/png")
        return response
    return Response(emergency_vehicle_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def add_emergency(request):
    emergency_serializer = EmergencySerializer(data=request.data)
    if emergency_serializer.is_valid():
        emergency = emergency_serializer.save()
        response = HttpResponse(router.update_map(), content_type="image/png")
        return response
    return Response(emergency_serializer.errors, status=status.HTTP_400_BAD_REQUEST)