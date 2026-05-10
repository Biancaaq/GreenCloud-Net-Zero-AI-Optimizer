# Technical Architecture Document: GreenCloud Net Zero Optimizer

## 1. Executive Summary
GreenCloud is a modular analytics platform designed to optimize data center sustainability through two primary modules:
1.  **Geospatial Smart Placement**: A multi-criteria decision-support system for locating new facilities.
2.  **HVAC Optimization Engine**: An AI-driven diagnostic tool for existing infrastructure.

The system is built on a decoupled architecture that bridges high-performance data processing (Pandas/NumPy) with advanced AI diagnostics (RandomForest/RAG).

---

## 2. System Architecture
The application follows a modern **Monolithic MVC** architecture, optimized for the speed and specific constraints of a hackathon while maintaining enterprise-grade security standards.

### 2.1 Technology Stack
*   **Backend Framework**: Django 6.0
*   **AI/ML Pipeline**: Scikit-Learn (RandomForest), JSON-based Retrieval-Augmented Generation (RAG)
*   **Data Processing**: Pandas, NumPy
*   **Geospatial Logic**: Shapely (Geometric modifiers), Folium (Mapping)
*   **UI Foundation**: Bootstrap 5, Vanilla JS (ES6), Glassmorphic CSS

---

## 3. The AI & Optimization Pipeline

### 3.1 Geospatial Ranking Engine (`AnalysisEngine`)
Located in `optimizer/services.py`, this engine performs real-time scoring of geographic regions.
*   **Normalization**: Raw metrics (Land Price, Energy Capacity, etc.) are scaled to a `0-100` range using vectorized Pandas operations.
*   **Vectorized Scoring**: User weights are applied as a matrix multiplication across normalized columns, ensuring sub-second response times even with large datasets.
*   **Geospatial Modifiers**: Proximity to water bodies (cooling bonus) and mountainous terrain (construction penalty) are computed using Shapely's geometric intersection logic.

### 3.2 HVAC Diagnostic Pipeline
The Cooling Analyzer uses a multi-stage AI pipeline:
1.  **Classification Layer**: A `RandomForestClassifier` trained on historical telemetry (Ambient Temp, IT Load, Fan Speed) predicts the facility's efficiency label (e.g., `OPTIMAL`, `INEFFICIENT_COOLING`, `PUE_ANOMALY`).
2.  **Knowledge Retrieval (RAG)**: The efficiency label serves as a query to a structured JSON knowledge base. The engine retrieves targeted solutions, including "Recommended Actions" and "Expected Impact."
3.  **Economic Impact Engine**: A specialized module (`cost_analyzer.py`) calculates the Euro-denominated savings and CO2 reduction by cross-referencing local energy prices and grid carbon intensity.

---

## 4. Implementation Details

### 4.1 Path Management & Modularity
To ensure the AI pipeline (`src/`) operates seamlessly within the Django framework, the system utilizes absolute path resolution:
*   `PROJECT_ROOT` is dynamically calculated.
*   `sys.path` injection allows Django views to invoke the pipeline as a standalone service.
*   All data/model paths are resolved relative to the project root, ensuring portability.

### 4.2 Frontend Integration (AJAX)
The application emulates a Single Page Application (SPA) feel using asynchronous updates:
*   **Infrastructure Map**: Fetches new Folium map fragments and raw data tables via AJAX, injecting them into the DOM without a page reload.
*   **Cooling Analyzer**: Transmits telemetry to the AI backend; the response is a JSON payload used by client-side JS to animate ROI counters and display diagnostic cards.

---

## 5. Security & Robustness

### 5.1 Input Sanitization
The platform implements strict validation for all user-facing endpoints:
*   **Safe Parsing**: A `_safe_int` helper clamps and validates numeric weights (1-100), preventing `ValueError` crashes.
*   **Parameter Whitelisting**: The `region` parameter is restricted to a set of valid keys (`ro`, `eu`).
*   **Location Sanitization**: API inputs are filtered to allow only alphanumeric characters, preventing path traversal or injection attacks.

### 5.2 Deployment Hardening
The `settings.py` includes a security block that automatically activates when `DEBUG=False`:
*   **HSTS & SSL Redirects**: Enforces secure connections.
*   **Secure Cookies**: Enables `SESSION_COOKIE_SECURE` and `CSRF_COOKIE_SECURE`.
*   **Frame Protection**: Set to `DENY` to prevent clickjacking.
*   **MIME Sniffing**: `SECURE_CONTENT_TYPE_NOSNIFF` is enabled.

---

## 6. Future Roadmap
*   **Relational Migration**: Transition from CSV-based flat files to PostgreSQL with PostGIS for advanced geospatial queries.
*   **Real-time IoT Integration**: Replace manual telemetry selection with a live MQTT/Websocket feed from actual data center sensors.
*   **Expanded RAG**: Integrate a vector database (e.g., Chroma or FAISS) to allow the RAG engine to digest hundreds of PDF sustainability reports.

---
**Net Zero Mission 2026**
*Technical Documentation Version 1.1*
