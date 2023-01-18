from rest_framework import serializers

from .models import EmergencyVehicle, Emergency, RouteRecommendation


class EmergencyVehicleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmergencyVehicle
        fields = ['call_name', 'last_ping', 'lat', 'long', 'currently_dispatch']
        extra_kwargs = {'call_name': {'read_only': False}, 'last_ping': {'required': False},
                        'currently_dispatch': {'required': False}}


class EmergencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Emergency
        fields = ['lat', 'long', 'type', 'dispatched_vehicle', 'resolved', 'timestamp']
        extra_kwargs = {'dispatched_vehicle': {'required': False}, 'resolved': {'required': False},
                        'timestamp': {'required': False}}


class RoteRecommendationSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = RouteRecommendation


class IdSerializer(serializers.Serializer):
    id = serializers.IntegerField()


class RouteRecommendationJsonSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    vehicle = EmergencyVehicleSerializer()
    emergency = EmergencySerializer()
    weight = serializers.FloatField()
    length = serializers.FloatField()
