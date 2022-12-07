# def detail(request, trip_id):
#     # trip = Trip.objects.get(pk=trip_id)
#     # context = {'start_time': trip.start_time, 'end_time': trip.end_time, 'trip_id': trip.id}
#     # return render(request, 'trips/details.html', context)
#     trip = get_object_or_404(Trip, pk=trip_id)
#     return render(request, 'trips/detail.html', {'trip': trip})

from .models import Trip
from rest_framework import viewsets
from rest_framework import permissions
from trips.serializers import TripSerializer
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
# from django.http import Http404
from rest_framework.decorators import action
from rest_framework.response import Response

# def detail(request):
#     latest_trips_list = Trip.objects.order_by('-start_time')[:5]
#     context = {'latest_trips_list': latest_trips_list}
#     return render(request, 'trips/index.html', context)

# def detail(request, trip_id):
#     return HttpResponse("You're looking at question %s." % trip_id)

def results(request, trip_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % trip_id)

class TripViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows trips to be viewed or edited.
    """
    queryset = Trip.objects.all().order_by('start_time')
    serializer_class = TripSerializer
    permission_classes = [permissions.IsAuthenticated]

    @action(detail=True)
    def test_this(self, request, pk=None):
        trip = Trip.objects.get(pk=pk)
        return Response({'status': 'password set'})