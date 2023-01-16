from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..buisness_logic.router import Router
from ..models import EmergencyVehicle, Emergency, RouteRecommendation
from ..serializers import EmergencyVehicleSerializer, EmergencySerializer, IdSerializer, \
    RouteRecommendationJsonSerializer

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


@api_view(['GET'])
def get_recommended_vehicle_for_emergency(request):
    emergency_id_serializer = IdSerializer(data=request.data)
    if emergency_id_serializer.is_valid():
        try:
            emergency = Emergency.objects.get(
                id=emergency_id_serializer.validated_data['id'])
            route = router.get_recommended_vehicle_for_emergency(emergency)
            print(route)
            rrs = RouteRecommendationJsonSerializer(route)
            print(rrs.data)
            return Response(rrs.data)
        except Emergency.DoesNotExist:
            return Response("Can not find emergency with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(emergency_id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_map_of_route(request):
    id_serializer = IdSerializer(data=request.data)
    if id_serializer.is_valid():
        try:
            route = RouteRecommendation.objects.get(
                id=id_serializer.validated_data['id'])
            response = HttpResponse(router.create_map_from_recommended_route(route), content_type="image/png")
            return response
        except RouteRecommendation.DoesNotExist:
            return Response("Can not find route with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def dispatch_vehicle(request):
    id_serializer = IdSerializer(data=request.data)
    if id_serializer.is_valid():
        try:
            route = RouteRecommendation.objects.get(
                id=id_serializer.validated_data['id'])
            response = HttpResponse(router.dispatch_to_recommended_route(route))
            return response
        except RouteRecommendation.DoesNotExist:
            return Response("Can not find route with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
