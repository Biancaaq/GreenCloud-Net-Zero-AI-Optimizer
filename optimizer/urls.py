from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('map/', views.map_view, name='map'),
    path('api/date-harta/', views.api_date_harta, name='api_date_harta'),
]