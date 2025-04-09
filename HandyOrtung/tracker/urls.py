from django.urls import path
from .views import collect_location

urlpatterns = [
    path('collect/', collect_location, name='collect_location'),
]
