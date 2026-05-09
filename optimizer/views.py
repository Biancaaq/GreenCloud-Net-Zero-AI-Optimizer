from django.shortcuts import render

def map_view(request):
    # Aici, mai târziu, colegii de pe ML vor trimite datele către hartă
    return render(request, 'map.html')