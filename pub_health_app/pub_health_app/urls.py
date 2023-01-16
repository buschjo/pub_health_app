"""pub_health_app URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.urls import include, path
from rest_framework import routers
from trips import views


from django.contrib import admin

from routing.client_interfaces import Interfaces

router = routers.DefaultRouter()
router.register(r'trips', views.TripViewSet)


# Wire up our API using automatic URL routing
# Additionally, we include login URLs for the browsable API.
urlpatterns = [
    path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('admin/', admin.site.urls),
    path('map', views.MapViewSet.as_view(), name="Map"),
    path('map_josefine', views.index, name='index'),
    path('emergency-vehicle', Interfaces.update_emergency_vehicle),
    path('emergency', Interfaces.add_emergency),
    path('recommended-vehicle', Interfaces.get_recommended_vehicle_for_emergency),
    path('recommended-route-map', Interfaces.get_map_of_route),
    path('dispatch', Interfaces.dispatch_vehicle)
]
