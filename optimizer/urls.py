from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('infrastructure-map/', views.infrastructure_map_view, name='infrastructure_map'),
    path('api/date-harta/', views.api_date_harta, name='api_date_harta'),
]