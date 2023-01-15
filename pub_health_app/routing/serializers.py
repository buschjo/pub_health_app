from rest_framework import serializers

from .models import EmergencyVehicle, Emergency


class EmergencyVehicleSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = EmergencyVehicle
        fields = ['call_name', 'last_ping', 'lat', 'long', 'currently_dispatch']
        extra_kwargs = {'call_name': {'read_only': False}, 'last_ping': {'required': False}, 'currently_dispatch': {'required': False}}


class EmergencySerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Emergency
        fields = ['lat', 'long', 'type', 'dispatched_to', 'resolved', 'timestamp']
        extra_kwargs = {'dispatched_to': {'required': False}, 'resolved': {'required': False}, 'timestamp': {'required': False}}
