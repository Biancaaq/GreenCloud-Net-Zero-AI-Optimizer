# pyrefly: ignore [missing-import]
from django.shortcuts import render
# pyrefly: ignore [missing-import]
from django.http import JsonResponse, HttpRequest, HttpResponse
# pyrefly: ignore [missing-import]
from django.views.decorators.http import require_GET
import pandas as pd
import os
import sys

from optimizer.services import AnalysisEngine, MissingDataException
from optimizer.map_builder import generate_infrastructure_map_html, get_fallback_map_html

# Add src/ to Python path so we can import the AI pipeline modules
SRC_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src')
if SRC_DIR not in sys.path:
    sys.path.insert(0, SRC_DIR)

def home_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'home.html')


def _safe_int(value, default: int) -> int:
    """Safely parse an integer from user input, returning default on failure."""
    try:
        return max(1, min(100, int(value)))
    except (ValueError, TypeError):
        return default

def login_view(request: HttpRequest) -> HttpResponse:
    return render(request, 'login.html')

def infrastructure_map_view(request: HttpRequest) -> HttpResponse:
    # Parse weights from GET request or use defaults
    weights_input = {
        'weight_land_price': _safe_int(request.GET.get('weight_land_price', 20), 20),
        'weight_water_price': _safe_int(request.GET.get('weight_water_price', 20), 20),
        'weight_climate': _safe_int(request.GET.get('weight_climate', 20), 20),
        'weight_green_energy': _safe_int(request.GET.get('weight_green_energy', 20), 20),
        'weight_energy_capacity': _safe_int(request.GET.get('weight_energy_capacity', 10), 10),
        'weight_gdp': _safe_int(request.GET.get('weight_gdp', 10), 10),
    }

    # Map inputs to AnalysisEngine expected keys
    ml_weights = {
        'land': weights_input['weight_land_price'] / 100.0,
        'water': weights_input['weight_water_price'] / 100.0,
        'climate': weights_input['weight_climate'] / 100.0,
        'green': weights_input['weight_green_energy'] / 100.0,
        'capacity': weights_input['weight_energy_capacity'] / 100.0,
        'gdp': weights_input['weight_gdp'] / 100.0
    }

    current_region = request.GET.get('region', 'ro')
    if current_region not in ('ro', 'eu'):
        current_region = 'ro'

    try:
        results = AnalysisEngine.process_ranking(ml_weights, region=current_region)
        if results:
            map_html = generate_infrastructure_map_html(results, current_region)
            df_results = pd.DataFrame([{
                "Rank": f"#{r['rank']}",
                "Region Node": r["county"],
                "Grid Score": f"{r['score']}%",
                "Lat / Lon": f"{r['center'][0]:.2f}, {r['center'][1]:.2f}"
            } for r in results])
        else:
            df_results = pd.DataFrame([{"Info": "No optimal regions found for given parameters."}])
            map_html = get_fallback_map_html(current_region)
            
    except MissingDataException as e:
        df_results = pd.DataFrame([{"Error": str(e)}])
        map_html = get_fallback_map_html(current_region)

    html_tables = df_results.to_html(classes="table table-custom text-sm mb-0", index=False, border=0)

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        return JsonResponse({
            'map_html': map_html,
            'dataframes_html': html_tables
        })

    return render(request, 'infrastructure_map.html', {
        'map_html': map_html,
        'dataframes_html': html_tables,
        'weights': weights_input,
        'current_region': current_region
    })

def cooling_analyzer_view(request):
    # Read available locations from the dataset
    try:
        dataset_path = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data', 'base_dataset_data_centers.csv')
        df = pd.read_csv(dataset_path)
        locations = df['Location'].tolist()
    except Exception:
        locations = []

    return render(request, 'cooling_analyzer.html', {'locations': locations})


@require_GET
def cooling_diagnostics_api(request):
    """API endpoint that runs the full AI pipeline from src/main.py."""
    location = request.GET.get('location', 'Dublin')
    # Sanitize: only allow alphanumeric, spaces, hyphens, dots, and dashes
    if not location or not all(c.isalnum() or c in ' .-' for c in location):
        return JsonResponse({'success': False, 'error': 'Invalid location name'}, status=400)

    try:
        # pyrefly: ignore [missing-import]
        from main import run_optimization_pipeline
        results = run_optimization_pipeline(location)

        if not results.get('success'):
            return JsonResponse({'success': False, 'error': results.get('error', 'Unknown error')}, status=400)

        # Shape the response for the frontend
        pred = results['prediction']
        sol = results['solution']
        cost = results['economics']
        inp = results['input_snapshot']

        return JsonResponse({
            'success': True,
            'input': {
                'location': str(inp['Location']),
                'ambient_temp': float(inp['Ambient_Temp_C']),
                'hvac_power': round(float(inp['HVAC_Power_kW']), 1),
                'pue': float(inp['PUE']),
                'it_load': float(inp['IT_Load_kW']),
                'fan_speed': float(inp['Fan_Speed_Pct']),
                'chiller_status': 'Active' if int(inp['Chiller_Status']) == 1 else 'Inactive',
            },
            'prediction': {
                'label': str(pred['label']),
                'confidence': float(pred['confidence']),
            },
            'rag': {
                'title': str(sol['title']),
                'risk_level': str(sol['risk_level']),
                'content': str(sol['content']),
                'recommended_actions': [str(a) for a in sol['recommended_actions']],
                'expected_impact': str(sol['expected_impact']),
            },
            'economics': {
                'current_monthly_cost': float(cost['current_monthly_cost_eur']),
                'optimized_monthly_cost': float(cost['optimized_monthly_cost_eur']),
                'monthly_saving': float(cost['estimated_monthly_saving_eur']),
                'annual_saving': round(float(cost['estimated_monthly_saving_eur']) * 12, 2),
                'saving_pct': float(cost['estimated_saving_pct']),
                'monthly_co2_kg': float(cost['current_monthly_co2_kg']),
                'co2_reduction_kg': float(cost['estimated_monthly_co2_reduction_kg']),
                'annual_co2_reduction_tons': round(float(cost['estimated_monthly_co2_reduction_kg']) * 12 / 1000, 1),
                'carbon_intensity': float(cost['carbon_intensity_gco2_per_kwh']),
                'current_pue': float(inp['PUE']),
                'optimized_pue': round(float(inp['PUE']) * (1 - float(cost['estimated_saving_pct']) / 200), 2),
            }
        })

    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)