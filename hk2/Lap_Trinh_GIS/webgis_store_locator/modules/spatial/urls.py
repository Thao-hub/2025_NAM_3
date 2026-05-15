from django.urls import path
from . import controllers

urlpatterns = [
    path('geocode/', controllers.geocode),
    path('stores-in-bounds/', controllers.stores_in_bounds),
    path('stores-in-radius/', controllers.stores_in_radius),
    path('smart-search/', controllers.smart_search),
    path('reverse-geo/', controllers.reverse),
    path('suggest/', controllers.suggest),
    path('districts/', controllers.districts),
    path('search-stores/', controllers.search_stores),
    path('route-osrm/', controllers.route_osrm),
    path('ping/', controllers.ping),
]
