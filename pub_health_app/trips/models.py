import datetime
from django.db import models
from django.utils import timezone

# Create your models here.

class Trip(models.Model):
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    start_long = models.DecimalField(max_digits=8, decimal_places=6)
    start_lat = models.DecimalField(max_digits=8, decimal_places=6)
    end_long = models.DecimalField(max_digits=8, decimal_places=6)
    end_lat = models.DecimalField(max_digits=8, decimal_places=6)

    def __str__(self):
        return f'Trip Start: {self.start_time} at {self.start_long} - {self.start_lat} :::: Trip End: {self.end_time} at {self.end_long} - {self.end_lat}'

    def was_published_recently(self):
        return self.start_time >= timezone.now() - datetime.timedelta(days=1)