from django.contrib import admin
from django.urls import path, include  # <-- Asigură-te că adaugi 'include' aici

urlpatterns = [
    path('admin/', admin.site.urls),
    # Legăm rutele din 'optimizer' de proiectul principal
    path('', include('optimizer.urls')), 
]