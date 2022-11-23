from .models import Trip
from rest_framework import serializers


class TripSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Trip
        fields = ['start_time', 'end_time', 'start_long', 'start_lat']
