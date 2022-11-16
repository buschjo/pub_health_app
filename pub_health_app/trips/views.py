from django.shortcuts import get_object_or_404, render
from django.http import Http404

from .models import Trip

def index(request):
    latest_trips_list = Trip.objects.order_by('-start_time')[:5]
    context = {'latest_trips_list': latest_trips_list}
    return render(request, 'trips/index.html', context)

def detail(request, trip_id):
    # trip = Trip.objects.get(pk=trip_id)
    # context = {'start_time': trip.start_time, 'end_time': trip.end_time, 'trip_id': trip.id}
    # return render(request, 'trips/details.html', context)
    trip = get_object_or_404(Trip, pk=trip_id)
    return render(request, 'trips/detail.html', {'trip': trip})