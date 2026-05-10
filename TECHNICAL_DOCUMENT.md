# Technical Architecture Document: GreenCloud Net Zero Optimizer

## 1. Executive Summary
GreenCloud is a modular, Django-based analytics application designed to solve the complex geospatial optimization problem of data center placement. By evaluating real-time grid carbon intensity, regional economy metrics, and environmental geography, the system calculates a weighted "Grid Score" to recommend optimal target zones for high-intensity AI workloads. The architecture is explicitly decoupled, supporting both Romanian (National Grid) and European-wide regional analyses independently.

## 2. System Architecture
The application utilizes a classic Monolithic MVC (Model-View-Template) architecture via **Django 5.0**, enhanced with asynchronous client-side rendering capabilities to emulate a Single Page Application (SPA) experience without the overhead of a heavy frontend framework.

* **Frontend Layer**: HTML5, CSS3, Vanilla JavaScript (ES6+), Bootstrap 5.
* **Controller Layer**: Django Views providing both standard HTML template rendering and RESTful JSON endpoints.
* **Service/Logic Layer**: The `AnalysisEngine` singleton, powered by Pandas and Shapely.
* **Visualization Layer**: Server-side map generation using Folium and Leaflet.js.

## 3. Data Processing Pipeline (ETL)
The core logic resides in `optimizer/services.py` within the `AnalysisEngine` class. To ensure sub-second response times during user interaction (e.g., rapid slider adjustments), the engine implements an aggressive in-memory caching strategy.

1. **Ingestion & Caching**: Raw telemetry datasets (CSV) are loaded based on the requested region (`ro` vs `eu`). The dataframes are cached at the class level (`_cached_df`), preventing repetitive disk I/O on subsequent requests.
2. **ETL Standardization**: Irrespective of upstream dataset schemas (e.g., `judet` vs `region`), the pipeline normalizes the spatial keys to a unified `county` namespace.
3. **Pre-computation**: Static metrics that do not depend on user input (e.g., Base Land Price, Total Capacity) are pre-normalized. Normalization maps raw values to a strictly bounded `0-100` scale. Metrics where lower is better (e.g., Land Price, Carbon Intensity) are reversed using `100 - normalized_value`.
4. **Vectorized Scoring**: Upon receiving an HTTP GET/AJAX request containing the user's custom weights, the engine performs a vectorized matrix multiplication across the pre-normalized columns to compute the dynamic `score`.

## 4. Geospatial Engine
Geospatial logic is handled using **Shapely** and **Folium**. 

* **Shapely Modifiers**: Geographic reality modifies raw economic data. For example, data centers located within the Carpathian Mountains polygon (`CARPATHIANS_SHAPE`) receive a 1.8x multiplier penalty to land development costs. Proximity to major waterways (`WATER_WAYS`) applies a 0.8x bonus modifier to water utility costs, calculated via the Haversine formula.
* **Folium Rendering**: The calculated top 3 optimal locations are injected into a Folium map instance. The backend generates raw HTML/JavaScript containing customized heat layers, bounding boxes, and interactive markers. 

## 5. Asynchronous Frontend Integration
To provide a fluid, "desktop-like" experience, the dashboard bypasses traditional page reloads:
* **AJAX Fetch**: When the user adjusts optimization weights and clicks "Recalculate", a `fetch()` API call transmits the form data to the backend asynchronously.
* **DOM Injection & Eval**: The backend responds with a JSON payload containing `map_html` and `dataframes_html`. The client replaces the DOM elements and utilizes `eval()` to execute the dynamically generated Folium JavaScript scripts embedded in the HTML fragment.
* **Cross-Frame Communication**: The Folium map (often rendered as an iframe or complex DOM structure) communicates with the parent DOM via the `window.postMessage` API. Hovering over a map node dispatches a payload containing the node's rank and score, which is caught by an event listener in the parent window to instantly update the "ML Location Insights" side panel.

## 6. Scalability & Security Constraints
* **Current State**: The application uses flat CSV files and in-memory singletons, optimized for the speed and specific constraints of a hackathon deployment.
* **Future Evolution**: For production deployment, the CSV datasets must be migrated to a relational database (PostgreSQL with PostGIS extensions) managed via the Django ORM. The `eval()` based JS injection should be replaced with a strict DOM parser or a dedicated frontend mapping library (e.g., Mapbox GL JS) querying a standardized GeoJSON REST API to enforce strict Content Security Policy (CSP) compliance.
