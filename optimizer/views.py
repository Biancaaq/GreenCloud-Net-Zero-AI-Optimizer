from django.shortcuts import render
from django.http import JsonResponse
import folium

def home_view(request):
    return render(request, 'home.html')

def login_view(request):
    return render(request, 'login.html')

def infrastructure_map_view(request):
    # Inițializăm harta
    m = folium.Map(
        location=[44.6, 26.5], # Centrat mai jos pentru vizibilitate
        zoom_start=8,
        tiles="CartoDB dark_matter",
        control_scale=True
    )

    # Coordonatele centrale ale ariei returnate de modelul ML
    ai_lat, ai_lon = 44.35, 27.05 # Ex: Câmpia Bărăganului

    # 1. Stratul exterior (mai transparent, rază mare)
    folium.Circle(
        location=[ai_lat, ai_lon],
        radius=40000, # 40 km rază
        color=None,   # Fără margine pentru un look organic (heatmap)
        fill=True,
        fill_color='#70A288', # Verdele vostru Eco
        fill_opacity=0.15     # Foarte transparent
    ).add_to(m)

    # 2. Stratul interior (mai intens, rază mică - nucleul ariei)
    folium.Circle(
        location=[ai_lat, ai_lon],
        radius=18000, # 18 km rază
        color=None,
        fill=True,
        fill_color='#50886c', # Un verde ușor mai intens
        fill_opacity=0.4
    ).add_to(m)

    # 3. Markerul discret în centru pentru interactivitate cu panoul din dreapta
    # Folosim o iconiță minimalistă
    folium.Marker(
        location=[ai_lat, ai_lon],
        tooltip="<span style='color: #04395E; font-weight: bold;'>Bărăgan Solar Cluster</span><br>Click for ML Insights",
        icon=folium.Icon(color='green', icon='bolt', prefix='fa')
    ).add_to(m)

    # Convertim harta în HTML
    map_html = m._repr_html_()

    return render(request, 'infrastructure_map.html', {'map_html': map_html})

def api_date_harta(request):
    # Aici vei apela modelul de ML pentru a obține coordonatele
    date = {"lat": 44.4, "lng": 26.1, "scor_verde": 85}
    return JsonResponse(date)