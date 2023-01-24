from rest_framework import serializers

from .models import EmergencyVehicle, Emergency, RouteRecommendation


class EmergencyVehicleSerializer(serializers.ModelSerializer):
    class Meta:
        model = EmergencyVehicle
        fields = ['call_name', 'last_ping', 'lat', 'long', 'currently_dispatch']
        extra_kwargs = {'call_name': {'read_only': False}, 'last_ping': {'required': False},
                        'currently_dispatch': {'required': False}}


class EmergencySerializer(serializers.ModelSerializer):

    class Meta:
        model = Emergency
        fields = ['lat', 'long', 'type', 'dispatched_vehicle', 'resolved', 'timestamp']
        extra_kwargs = {'dispatched_vehicle': {'required': False}, 'resolved': {'required': False},
                        'timestamp': {'required': False}}


class EmergencyResponseSerializer(serializers.ModelSerializer):
    dispatched_vehicle = EmergencyVehicleSerializer()

    class Meta:
        model = Emergency
        fields = ['lat', 'long', 'type', 'dispatched_vehicle', 'resolved', 'timestamp']
        extra_kwargs = {'dispatched_vehicle': {'required': False}, 'resolved': {'required': False},
                        'timestamp': {'required': False}}

class RoteRecommendationSerializer(serializers.ModelSerializer):
    class Meta:
        model = RouteRecommendation


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class RouteRecommendationJsonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vehicle = EmergencyVehicleSerializer()
    emergency = EmergencyResponseSerializer()
    weight = serializers.FloatField()
    length = serializers.FloatField()

class DispatchSerializer(serializers.Serializer):
    emergency_id = serializers.IntegerField()
    route = serializers.CharField()
    type = serializers.CharField()
    timestamp = serializers.DateTimeField()