# pyrefly: ignore [missing-import]
from django.urls import path
from . import views

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.login_view, name='login'),
    path('infrastructure-map/', views.infrastructure_map_view, name='infrastructure_map'),
    path('solutions/hvac-optimizer/', views.cooling_analyzer_view, name='cooling_analyzer'),
    path('api/cooling-diagnostics/', views.cooling_diagnostics_api, name='cooling_diagnostics_api'),
]