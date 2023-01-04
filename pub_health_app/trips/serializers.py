from .models import Trip
from .models import Map
from rest_framework import serializers


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ['start_time', 'end_time', 'start_long', 'start_lat', 'end_long', 'end_lat']


class MapSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'

