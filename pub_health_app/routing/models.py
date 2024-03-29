from django.db import models
from shapely import from_geojson

from .fields import IntegerListField


# Create your models here.
class EmergencyVehicle(models.Model):
    call_name = models.CharField(max_length=128)
    last_ping = models.DateTimeField(auto_now_add=True, blank=True)
    lat = models.DecimalField(max_digits=17, decimal_places=15)
    long = models.DecimalField(max_digits=17, decimal_places=15)
    currently_dispatch = models.BooleanField(default=False)
    currently_checked_in = models.BooleanField(default=False)

    def __str__(self):
        return f'Emergency Vehicle: {self.call_name} at Position {self.lat},{self.long} at: {self.last_ping}, currently dispatched {self.currently_dispatch} '


class Emergency(models.Model):
    lat = models.DecimalField(max_digits=17, decimal_places=15)
    long = models.DecimalField(max_digits=17, decimal_places=15)
    type = models.CharField(max_length=128)
    dispatched_vehicle = models.ForeignKey(EmergencyVehicle, on_delete=models.CASCADE, null=True)
    resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True, blank=True)

    def __str__(self):
        return f'Emergency: {self.type} at Position {self.lat},{self.long}, dispatched vehicle: {self.dispatched_vehicle}, is resolved: {self.resolved} '


class RouteRecommendation(models.Model):
    vehicle = models.ForeignKey(EmergencyVehicle, on_delete=models.CASCADE, null=True)
    emergency = models.ForeignKey(Emergency, on_delete=models.CASCADE, unique=True)
    nodes = IntegerListField(max_length=2000, null=True)
    start_linestring = models.CharField(max_length=1000, null=True)
    end_linestring = models.CharField(max_length=1000, null=True)
    weight = models.FloatField(null=True)
    length = models.FloatField(null=True)
    route_geo_json = models.CharField(max_length=9000, null=True)

    def get_tc_tupel(self):
        start_linestring = self.start_linestring
        end_linestring = self.end_linestring
        if start_linestring == "[]":
            start_linestring = None
        if end_linestring == "[]":
            end_linestring = None
            print("here")

        print(end_linestring)

        return self.length, self.nodes, from_geojson(start_linestring), from_geojson(end_linestring)

    def get_start_linestring(self):
        return from_geojson(self.start_linestring)

    def get_end_linestring(self):
        return from_geojson(self.end_linestring)

    def __str__(self):
        return f'RouteRecommendation - Emergency: {self.emergency}, Vehicle: {self.vehicle}, Weight: {self.weight}, Length: {self.length}'
