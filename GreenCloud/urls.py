# pyrefly: ignore [missing-import]
from django.contrib import admin
# pyrefly: ignore [missing-import]
from django.urls import path, include  # <-- Make sure to add 'include' here

urlpatterns = [
    path('admin/', admin.site.urls),
    # Link optimizer app routes to the main project
    path('', include('optimizer.urls')), 
]