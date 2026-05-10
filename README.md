# GreenCloud: Net Zero AI Optimizer

[![Hackathon](https://img.shields.io/badge/Hackathon-Net_Zero_Mission_2026-green.svg)](#)
[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](#)
[![Django](https://img.shields.io/badge/Django-6.0-092e20.svg)](#)
[![Scikit-Learn](https://img.shields.io/badge/AI-RandomForest_%2B_RAG-orange.svg)](#)

**GreenCloud** is an enterprise-grade AI decision-support platform designed to decarbonize cloud infrastructure. Built for the **Net Zero Mission Hackathon**, it combines geospatial intelligence with machine learning to solve two critical challenges: **Smart Infrastructure Placement** and **HVAC Cooling Efficiency.**

---

## Key Capabilities

### Geospatial Smart Placement
Find the most sustainable and cost-effective locations for new data centers.
*   **Multi-Criteria Ranking:** Evaluate regions based on Land Price, Water Utility costs, Climate (Free Cooling potential), Green Energy Mix, Grid Capacity, and Regional GDP.
*   **Geospatial Penalties/Bonuses:** Automated scoring modifiers using **Shapely** (e.g., elevation penalties in mountainous terrain or cooling bonuses near waterways).
*   **Heatmap Visualization:** Interactive **Folium** maps with real-time recalculations.

### HVAC Optimization Engine (AI Diagnostics)
Optimize existing facilities using a sophisticated AI pipeline.
*   **RandomForest Classifier:** Detects anomalies and cooling inefficiencies (e.g., `INEFFICIENT_COOLING`, `PUE_ANOMALY`) from real IT load and ambient telemetry.
*   **RAG (Retrieval-Augmented Generation):** Matches AI detections with high-precision mitigation strategies from a curated sustainability knowledge base.
*   **ROI Analyzer:** Instant quantification of monthly/annual savings in Euro and CO2e reduction.

---

## The AI Pipeline

The optimization engine follows a three-stage logic flow:

1.  **Diagnostic:** A `RandomForestClassifier` analyzes current IT Load, Ambient Temperature, and Fan Speeds to categorize the facility's efficiency state.
2.  **Prescription (RAG):** The detected state is passed to a RAG engine that retrieves the optimal "Net Zero" solution, including specific technical actions and expected impact.
3.  **Economic Simulation:** The system calculates the financial and environmental delta, adjusting PUE (Power Usage Effectiveness) based on local grid carbon intensity and energy prices.

---

## Technology Stack

| Layer | Technologies |
| :--- | :--- |
| **Backend** | Python 3.10+, Django 6.0 |
| **AI / ML** | Scikit-learn, joblib, RAG Architecture |
| **Data Science** | Pandas, NumPy, Shapely (Geospatial) |
| **Frontend** | Vanilla JS (ES6+), Bootstrap 5, CSS3 Glassmorphism |
| **Mapping** | Folium (Leaflet.js integration) |

---

## Installation & Setup

### 1. Prerequisites
*   Python 3.10 or higher
*   Pip / Venv

### 2. Clone & Environment
```bash
git clone https://github.com/your-repo/greencloud.git
cd greencloud

# Create and activate virtual environment
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/macOS:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configure Environment Variables
The project uses `django-environ` for security.
```bash
cp .env.example .env
```
Edit `.env` and set a random `SECRET_KEY`.

### 4. Database & Launch
```bash
python manage.py migrate
python manage.py runserver
```
Visit `http://127.0.0.1:8000` to access the dashboard.

---

## Project Structure

*   `GreenCloud/`: Core Django configuration and security settings.
*   `optimizer/`: Primary application logic, API views, and geospatial services.
*   `src/`: Modular AI pipeline (Classification, RAG, Cost Analysis).
*   `data/`: Datasets, AI models (`.pkl`), and knowledge bases (`.json`).
*   `templates/`: Modern, glassmorphic UI components.

---

## Security & Reliability
Designed with production-readiness in mind:
*   **Input Sanitization:** Whitelisted region parameters and alphanumeric location sanitization to prevent injection.
*   **Environment Isolation:** Secrets managed via `.env` with a committed `.env.example` for safe collaboration.
*   **Deployment Ready:** Pre-configured security headers (HSTS, XSS Filter, Frame Options) active when `DEBUG=False`.

---

## License
This project was developed for the **Net Zero Mission Hackathon**. 
Copyright © 2026 Team GreenCloud. All rights reserved.
