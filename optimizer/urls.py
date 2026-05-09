from django.urls import path
from . import views

urlpatterns = [
    path('map/', views.map_view, name='map'),
    path('api/date-harta/', views.api_date_harta, name='api_date_harta'),
]