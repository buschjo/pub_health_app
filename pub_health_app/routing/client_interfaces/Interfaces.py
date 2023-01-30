import base64

from django.http import HttpResponse
from django.utils import timezone
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from ..buisness_logic.router import Router
from ..models import EmergencyVehicle, Emergency, RouteRecommendation
from ..serializers import EmergencyVehicleSerializer, EmergencySerializer, IdSerializer, \
    RouteRecommendationJsonSerializer, DispatchSerializer

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
            emergency_vehicle.lat = emergency_vehicle_serializer.validated_data['lat']
            emergency_vehicle.long = emergency_vehicle_serializer.validated_data['long']
        except EmergencyVehicle.DoesNotExist:
            emergency_vehicle = emergency_vehicle_serializer.save()
        emergency_vehicle.last_ping = timezone.now()
        emergency_vehicle.save()
        try:
            dispatchment: RouteRecommendation = RouteRecommendation.objects.get(emergency__resolved=False,
                                                                                emergency__dispatched_vehicle__id=emergency_vehicle.id)
        except RouteRecommendation.DoesNotExist:
            return Response(status=status.HTTP_200_OK)
        dispachmentResponseDict = {'emergency_id': dispatchment.emergency.id, 'route': dispatchment.route_geo_json,
                                   'type': dispatchment.emergency.type,
                                   'timestamp': dispatchment.emergency.timestamp}
        response = Response(DispatchSerializer(dispachmentResponseDict).data)
        return response
    return Response(emergency_vehicle_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
def add_emergency(request):
    emergency_serializer = EmergencySerializer(data=request.data)
    if emergency_serializer.is_valid():
        emergency = emergency_serializer.save()
        try:
            router.get_recommended_vehicle_for_emergency(emergency)
            response = HttpResponse(router.update_map(), content_type="image/png")
            return response
        except Exception as e:
            return Response(f"Error: {e}", status.HTTP_400_BAD_REQUEST)
    return Response(emergency_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_recommended_vehicle_for_emergency(request):
    emergency_id_serializer = IdSerializer(data=request.data)
    if emergency_id_serializer.is_valid():
        try:
            emergency = Emergency.objects.get(
                id=emergency_id_serializer.validated_data['id'])
            route = router.get_recommended_vehicle_for_emergency(emergency)
            rrs = RouteRecommendationJsonSerializer(route)
            return Response(rrs.data)
        except Emergency.DoesNotExist:
            return Response("Can not find emergency with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(emergency_id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_map_of_route(request, id):
    try:
        route = RouteRecommendation.objects.get(
            id=id)
        response = Response(base64.encodebytes(router.create_map_from_recommended_route(route)),
                            status=status.HTTP_200_OK)
        return response
    except RouteRecommendation.DoesNotExist:
        return Response("Can not find route with given id", status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def dispatch_vehicle(request):
    id_serializer = IdSerializer(data=request.data)
    if id_serializer.is_valid():
        try:
            route = RouteRecommendation.objects.get(
                id=id_serializer.validated_data['id'])
            response = Response(router.dispatch_to_recommended_route(route), status=status.HTTP_200_OK)
            return response
        except RouteRecommendation.DoesNotExist:
            return Response("Can not find route with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def resolve_emergency(request):
    id_serializer = IdSerializer(data=request.data)
    if id_serializer.is_valid():
        try:
            emergency = Emergency.objects.get(
                id=id_serializer.validated_data['id'])
            router.resolve_emergency(emergency)
            response = Response(status=status.HTTP_204_NO_CONTENT)
            return response
        except RouteRecommendation.DoesNotExist:
            return Response("Can not find emergency with given id", status=status.HTTP_400_BAD_REQUEST)
    return Response(id_serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def get_map(request):
    return Response(base64.encodebytes(router.update_map()), status=status.HTTP_200_OK)


@api_view(["GET"])
def get_unresolved_recommendations(request):
    return Response(
        RouteRecommendationJsonSerializer(RouteRecommendation.objects.filter(emergency__resolved=False),
                                          many=True).data)


@api_view(['GET'])
def reevaluate_recommendations(request):
    undispatched_recommendations = RouteRecommendation.objects.filter(emergency__resolved=False,
                                                                      emergency__dispatched_vehicle__isnull=True)
    for undispatched_recommendation in undispatched_recommendations:
        new_recommendation = router.get_recommended_vehicle_for_emergency(undispatched_recommendation.emergency,
                                                                          save=False)
        if undispatched_recommendation and new_recommendation:
            undispatched_recommendation.vehicle = new_recommendation.vehicle
            undispatched_recommendation.nodes = new_recommendation.nodes
            undispatched_recommendation.start_linestring = new_recommendation.start_linestring
            undispatched_recommendation.end_linestring = new_recommendation.end_linestring
            undispatched_recommendation.weight = new_recommendation.weight
            undispatched_recommendation.length = new_recommendation.length
            undispatched_recommendation.route_geo_json = new_recommendation.route_geo_json
            undispatched_recommendation.save()
    return Response(status=status.HTTP_200_OK)
