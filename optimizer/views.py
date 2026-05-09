# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.http import JsonResponse, HttpRequest, HttpResponse
import pandas as pd

from optimizer.services import AnalysisEngine, MissingDataException
from optimizer.map_builder import generate_infrastructure_map_html, get_fallback_map_html

def home_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')

def login_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'login.html')

def infrastructure_map_view(request: HttpRequest) -> HttpResponse:
    # Parse weights from GET request or use defaults
    weights_input = {
        'weight_land_price': int(request.GET.get('weight_land_price', 20)),
        'weight_water_utilities': int(request.GET.get('weight_water_utilities', 20)),
        'weight_climate': int(request.GET.get('weight_climate', 20)),
        'weight_energy_price': int(request.GET.get('weight_energy_price', 20)),
        'weight_energy_capacity': int(request.GET.get('weight_energy_capacity', 10)),
        'weight_regional_economy': int(request.GET.get('weight_regional_economy', 10)),
    }

    # Map inputs to AnalysisEngine expected keys
    ml_weights = {
        'land': weights_input['weight_land_price'] / 100.0,
        'water': weights_input['weight_water_utilities'] / 100.0,
        'climate': weights_input['weight_climate'] / 100.0,
        'green': weights_input['weight_energy_price'] / 100.0,
        'capacity': weights_input['weight_energy_capacity'] / 100.0,
        'gdp': weights_input['weight_regional_economy'] / 100.0
    }

    try:
        results = AnalysisEngine.process_ranking(ml_weights)
        if results:
            map_html = generate_infrastructure_map_html(results)
            df_results = pd.DataFrame([{
                "Rank": f"#{r['rank']}",
                "Region Node": r["county"],
                "Grid Score": f"{r['score']}%",
                "Lat / Lon": f"{r['center'][0]:.2f}, {r['center'][1]:.2f}"
            } for r in results])
        else:
            df_results = pd.DataFrame([{"Info": "No optimal regions found for given parameters."}])
            map_html = get_fallback_map_html()
            
    except MissingDataException as e:
        df_results = pd.DataFrame([{"Error": str(e)}])
        map_html = get_fallback_map_html()

    html_tables = df_results.to_html(classes="table table-dark table-hover table-borderless text-sm mb-0", index=False)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'map_html': map_html,
            'dataframes_html': html_tables
        })

    return render(request, 'infrastructure_map.html', {
        'map_html': map_html,
        'dataframes_html': html_tables,
        'weights': weights_input
    })
