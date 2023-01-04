from django.contrib import admin

# Register your models here.
from .models import Trip
from .models import Map


admin.site.register(Trip)
admin.site.register(Map)