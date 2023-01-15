from django.db import models
from django.utils import timezone


# Create your models here.
class EmergencyVehicle(models.Model):
    call_name = models.CharField(max_length=128)
    last_ping = models.DateTimeField(default=timezone.now())
    lat = models.DecimalField(max_digits=17, decimal_places=15)
    long = models.DecimalField(max_digits=17, decimal_places=15)
    currently_dispatch = models.BooleanField(default=False)

    def __str__(self):
        return f'Emergency Vehicle: {self.call_name} at Position {self.lat},{self.long} at: {self.last_ping}, currently dispatched {self.currently_dispatch} '


class Emergency(models.Model):
    lat = models.DecimalField(max_digits=17, decimal_places=15)
    long = models.DecimalField(max_digits=17, decimal_places=15)
    type = models.CharField(max_length=128)
    dispatched_to = models.BooleanField(default=False)
    resolved = models.BooleanField(default=False)
    timestamp = models.DateTimeField(default=timezone.now())

    def __str__(self):
        return f'Emergency: {self.type} at Position {self.lat},{self.long}, is vehicle dispatched to:  {self.dispatched_to}, is resolved: {self.resolved} '

