# def detail(request, trip_id):
#     # trip = Trip.objects.get(pk=trip_id)
#     # context = {'start_time': trip.start_time, 'end_time': trip.end_time, 'trip_id': trip.id}
#     # return render(request, 'trips/details.html', context)
#     trip = get_object_or_404(Trip, pk=trip_id)
#     return render(request, 'trips/detail.html', {'trip': trip})

from .models import Trip
from .models import Map
from rest_framework import viewsets
from rest_framework import permissions
from trips.serializers import TripSerializer
from trips.serializers import MapSerializer
# from django.shortcuts import get_object_or_404, render
from django.http import HttpResponse
# from django.http import Http404
from rest_framework.renderers import TemplateHTMLRenderer
from rest_framework.decorators import action
from rest_framework.response import Response
from django.views.generic.base import TemplateView
from rest_framework.views import APIView
from django.http import HttpResponse
from django.template import loader

# def detail(request):
#     latest_trips_list = Trip.objects.order_by('-start_time')[:5]
#     context = {'latest_trips_list': latest_trips_list}
#     return render(request, 'trips/index.html', context)

# def detail(request, trip_id):
#     return HttpResponse("You're looking at question %s." % trip_id)

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

class MapViewSet(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    renderer_classes = [TemplateHTMLRenderer]
    template_name = 'map.html'

    def get(self, request):
        queryset = Map.objects.all()
        return HttpResponse({'map': queryset})


def index(request):
    template = loader.get_template('trips/map.html')
    queryset = Trip.objects.all()
    context = {
        'test': 'test',
        'queryset': queryset
    }
    return HttpResponse(template.render(context, request))
