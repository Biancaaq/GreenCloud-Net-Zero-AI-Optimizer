from django.shortcuts import render
from django.http import JsonResponse

def map_view(request):
    # Date fictive pe care ulterior le vei înlocui cu rezultatul din ML
    context = {
        'centre_date': [
            {'nume': 'București Node', 'lat': 44.4268, 'lng': 26.1025, 'status': 'critic', 'co2': 850},
            {'nume': 'Reykjavik Node', 'lat': 64.1466, 'lng': -21.9426, 'status': 'verde', 'co2': 120},
        ],
        'recomandare_curenta': 'Islanda - Retea Geotermala 98%'
    }
    return render(request, 'map.html', context)

def api_date_harta(request):
    # Aici vei apela modelul de ML pentru a obține coordonatele
    date = {"lat": 44.4, "lng": 26.1, "scor_verde": 85}
    return JsonResponse(date)