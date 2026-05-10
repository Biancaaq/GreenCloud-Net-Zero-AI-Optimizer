# pyrefly: ignore [missing-import]
import folium
import json
from typing import List, Dict, Any

def get_fallback_map_html(current_region: str = 'ro') -> str:
    """Returns the HTML representation of a default fallback map based on the region."""
    if current_region == 'eu':
        map_center = [49.0, 14.0]
        zoom = 4
    else:
        map_center = [45.94, 24.96]
        zoom = 7

    fallback_map = folium.Map(
        location=map_center, 
        zoom_start=zoom, 
        min_zoom=4,
        tiles="CartoDB dark_matter", 
        control_scale=True
    )
    return fallback_map._repr_html_()

def generate_infrastructure_map_html(results: List[Dict[str, Any]], current_region: str = 'ro') -> str:
    """Generates the main infrastructure map with heat layers, markers, and bounds based on ML results."""
    if not results:
        return get_fallback_map_html()

    if current_region == 'eu':
        map_center = [49.0, 14.0]
        zoom = 4
    else:
        map_center = results[0]["center"]
        zoom = 7

    m = folium.Map(
        location=map_center, 
        zoom_start=zoom,
        min_zoom=4,
        tiles="CartoDB dark_matter",
        control_scale=True
    )

    for r in results:
        # Organic heat layers
        folium.Circle(
            location=r["center"],
            radius=35000,
            color=None,
            fill=True,
            fill_color='#70A288',
            fill_opacity=0.15
        ).add_to(m)

        folium.Circle(
            location=r["center"],
            radius=15000,
            color=None,
            fill=True,
            fill_color='#50886c',
            fill_opacity=0.4
        ).add_to(m)

        # Rectangular bounds
        folium.Rectangle(
            bounds=r["box_bounds"],
            color='#DAB785',
            fill=False,
            weight=2,
            dash_array='5, 5'
        ).add_to(m)

        # Interactive Marker
        payload = json.dumps({
            "type": "region_hover", 
            "county": r["county"], 
            "score": r["score"],
            "rank": r["rank"]
        })
        
        tooltip_html = f"""
        <div onmouseenter='window.parent.postMessage({payload}, "*");' style='padding: 5px; cursor: pointer;'>
            <span style='color: #04395E; font-weight: bold;'>{r['county']}</span><br>AI Score: {r['score']}%
        </div>
        """
        
        folium.Marker(
            location=r["center"],
            tooltip=tooltip_html,
            icon=folium.Icon(color='green', icon='bolt', prefix='fa')
        ).add_to(m)

    return m._repr_html_()
