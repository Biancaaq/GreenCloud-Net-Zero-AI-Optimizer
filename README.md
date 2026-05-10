# GreenCloud Net Zero Optimizer

GreenCloud is an enterprise-grade analytics dashboard and decision-support tool designed to identify optimal geographic locations for AI and cloud workloads based on real-time grid carbon intensity, regional economy, and geographic factors.

Built as part of the Net Zero Mission hackathon, this project leverages geospatial analysis and machine learning scoring techniques to help organizations place data centers in the most sustainable and cost-effective regions.

---

# Core Features

## Geospatial Smart Placement
Interactive mapping powered by Folium, displaying heat layers, bounding boxes, and dynamically ranked optimal target zones.

## Dynamic Optimization Engine
Customizable weighting system allowing users to adjust the importance of parameters such as:
- Land Price
- Water Utilities
- Climate Conditions
- Energy Price
- Green Energy Capacity
- Regional GDP

## Multi-Region Architecture
Fully decoupled ETL pipelines supporting both the Romanian National Grid and broader European network nodes.

## Asynchronous User Experience
Seamless AJAX-based recalculations that update the map, raw telemetry tables, and ML insights panels without page reloads.

## Interactive ML Insights
Cross-frame communication that provides real-time location analytics, green scores, and deployment recommendations when hovering over map nodes.

---

# Technology Stack

## Backend
- Python 3
- Django 5

## Data Engineering & Analytics
- Pandas
- NumPy

## Geospatial Processing
- Shapely
- Folium

## Frontend
- HTML5
- CSS3
- Vanilla JavaScript
- Bootstrap 5

---

# Architecture & Logic Flow

## Data Ingestion
Raw telemetry datasets (CSV format) are loaded and cached via the `AnalysisEngine` singleton to prevent redundant disk I/O.

## ETL & Normalization
- Regional columns are standardized
- Metrics are normalized into a 0-100 scale
- Geospatial modifiers (e.g., proximity to water bodies, mountainous terrain penalties) are computed via Shapely polygons

## Scoring
User-defined weights are multiplied against the normalized metrics to produce a final **Grid Score** for each region.

## Visualization
The backend generates an HTML fragment using Folium and returns it alongside updated telemetry dataframes via a JSON payload.

## Frontend Injection
The client parses the JSON and injects the new DOM elements, subsequently executing any embedded Folium JavaScript.

---

# Installation and Setup

## Prerequisites
- Python 3.10 or higher
- Git

## Local Environment Setup

### Clone the repository
```bash
git clone <repository_url>
cd Papa-Louie
```

### Create and activate a virtual environment
```bash
python -m venv .venv
```

#### Windows
```bash
.venv\Scripts\activate
```

#### Linux/macOS
```bash
source .venv/bin/activate
```

### Install dependencies
```bash
pip install -r requirements.txt
```

### Apply database migrations
```bash
python manage.py migrate
```

### Run the development server
```bash
python manage.py runserver
```

### Access the application
Navigate to:

```text
http://127.0.0.1:8000
```

---

# Adding Datasets

To utilize the mapping functionality, ensure the appropriate CSV datasets are placed in the `optimizer/` directory.

## Romania
- `dataset1.csv`
- `dataset2.csv`

## Europe
- `dataset1_eu.csv`
- `dataset2_eu.csv`

The system requires specific column headers for standard operations.

If EU datasets are not present, the application will gracefully fall back to a centered, empty map for that specific region.

---

# License

This project was developed for the Net Zero Mission hackathon.

All rights reserved by the respective team members and organizers.
