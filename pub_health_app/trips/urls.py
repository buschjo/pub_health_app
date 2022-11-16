from django.urls import path

from . import views

app_name = 'trips'
urlpatterns = [
    path('', views.index, name='index'),
    # ex: /polls/5/
    path('<int:trip_id>/', views.detail, name='detail'),
]