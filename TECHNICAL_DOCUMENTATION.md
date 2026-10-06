# FedEx ZoneDetector (Airspace Guardian)
## Technical Documentation & Technical Aides Guide

---

## 1. Executive Summary
**FedEx Airspace Guardian (ZoneDetector)** is an automated airspace verification system designed to determine drone flight restrictions and regulatory airspace classifications (Red, Yellow, Green Zones) across India.

By integrating **FastAPI**, **Selenium WebDriver**, **Geopy**, and **React 19**, the application allows FedEx logistics and safety teams to query delivery locations via exact GPS coordinates or address/city names. It automatically scrapes DGCA’s (Directorate General of Civil Aviation) official **DigitalSky Airspace Map**, extracts restrictive airspace polygons/warnings, watermarks a cropped satellite screenshot of the location, and caches results into a local **SQLite** database for high-throughput operational efficiency.

---

## 2. Technical Stack & Dependencies (Technical Aides)

| Layer | Technology | Version | Purpose |
| :--- | :--- | :--- | :--- |
| **Backend Framework** | [FastAPI](https://fastapi.tiangolo.com/) | `0.115.12` | High-performance asynchronous REST API framework |
| **ASGI Server** | [Uvicorn](https://www.uvicorn.org/) | `0.34.2` | Production ASGI web server |
| **Web Scraping / Automation** | [Selenium](https://www.selenium.dev/) | `4.27.1` | Headless browser automation for DGCA DigitalSky portal |
| **Driver Management** | [webdriver-manager](https://pypi.org/project/webdriver-manager/) | `4.0.2` | Automated ChromeDriver binary installation & lifecycle |
| **Geocoding Engine** | [Geopy](https://geopy.readthedocs.io/) | `2.4.1` | Address and city name forward-geocoding to coordinates |
| **Image Processing** | [Pillow (PIL)](https://pillow.readthedocs.io/) | `9.5.0` | Center-crop airspace map screenshots and render GPS labels |
| **Database & Cache** | [SQLite3](https://www.sqlite.org/) | Built-in | Query caching and audit logging of zone classifications |
| **Frontend Framework** | [React](https://react.dev/) | `19.1.0` | Single-Page Application (SPA) UI with Dark/Light mode |
| **Component Library** | [Ant Design (antd)](https://ant.design/) | `5.26.2` | Enterprise UI components (Form, Switch, Spin, Typography) |
| **Web Server (Frontend)** | [Nginx Alpine](https://nginx.org/) | Stable | Production reverse proxy & static asset server in Docker |
| **Containerization** | [Docker & Compose](https://www.docker.com/) | 3.8+ spec | Multi-container orchestrated development and deployment |
| **Testing Suite** | [Pytest](https://pytest.org/) & [pytest-mock](https://pypi.org/project/pytest-mock/) | `8.3.5` / `3.14.1` | Automated unit, endpoint, and mock integration tests |
| **HTTP Client (Testing)** | [HTTPX](https://www.python-httpx.org/) | `0.28.1` | Asynchronous test client for FastAPI endpoints |

---

## 3. High-Level Architecture & Workflow

```mermaid
flowchart TD
    User["FedEx Dispatcher / User"] -->|Coordinates or Location Name| ReactUI["React 19 Frontend (Port 3000)"]
    ReactUI -->|GET /detect_zones| FastAPIServer["FastAPI Backend (Port 8000)"]
    
    FastAPIServer --> CacheCheck{"Cache Hit in SQLite?"}
    CacheCheck -->|Yes| ReturnCache["Return Cached Response & Base64 Image"]
    ReturnCache --> ReactUI

    CacheCheck -->|No| CheckInputType{"Is Input Location Name?"}
    CheckInputType -->|Yes| GeopyEngine["Geopy (Nominatim Geocoder) -> Converts to Lat/Lon"]
    CheckInputType -->|No (Direct Coords)| Scraper["Headless Selenium Engine"]
    GeopyEngine --> Scraper

    Scraper --> DGCA["DGCA DigitalSky Portal (Airspace Map)"]
    DGCA --> ExtractZones["Extract Restricted Zones & Airport Warnings"]
    DGCA --> CaptureScreen["Capture Screen & Crop via Pillow (PIL)"]
    
    ExtractZones --> SaveDB["Persist to SQLite (zone_logs.db)"]
    CaptureScreen --> SaveDB
    SaveDB --> APIResponse["Return JSON Response + Base64 Visual Proof"]
    APIResponse --> ReactUI
```

---

## 4. REST API Specification

### Endpoint: `GET /detect_zones`

#### Query Parameters
- `coordinates` *(string, optional)*: Geographic coordinates in format `"latitude,longitude"` (e.g. `28.6139,77.2090`).
- `location` *(string, optional)*: Text string describing address or city (e.g. `IGI Airport New Delhi`).

> **Note:** At least one parameter (`coordinates` or `location`) is strictly required.

#### Success Response (`200 OK`)
```json
{
  "zones": [
    "Airport Red",
    "Airspace - Red Zone"
  ],
  "zones_info": [
    {
      "zone_name": "Indira Gandhi International Airport",
      "zone_detail": "Airport Red"
    }
  ],
  "screenshot_uri": "data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAA..."
}
```

#### Safe / Unrestricted Response (`200 OK`)
```json
{
  "zones": [
    "Green Zone"
  ],
  "zones_info": [
    {
      "message": "No restricted zones detected. Area is in Green Zone."
    }
  ],
  "screenshot_uri": "data:image/png;base64,iVBORw0KGgo..."
}
```

#### Error Codes
- **`400 Bad Request`**: Neither coordinates nor location were provided.
- **`404 Not Found`**: Address could not be resolved by the geocoding service.
- **`500 Internal Server Error`**: Unexpected scraper or geocoding failure.

---

## 5. Database Schema & Data Dictionary

Database engine: **SQLite3**  
Database file path: `data/zone_logs.db`

### Table: `zone_logs`
| Column Name | Data Type | Constraints | Description |
| :--- | :--- | :--- | :--- |
| `id` | `INTEGER` | Primary Key, Auto Increment | Unique log record identifier |
| `timestamp` | `TEXT` | `YYYY-MM-DD HH:MM:SS` | Timestamp when the zone check was executed |
| `input_type` | `TEXT` | `"coordinates"` \| `"keyword"` | Format of the query used |
| `input_value` | `TEXT` | Not Null | Queried coordinates or lowercased location query |
| `detected_zones` | `TEXT` | JSON Array | Array of classified zone labels (e.g. `["Airport Red"]`) |
| `zone_names` | `TEXT` | JSON Array | Names of surrounding air facilities / points of interest |
| `zone_details` | `TEXT` | JSON Array | Detailed categories extracted from DGCA visual cards |
| `screenshot_base64`| `TEXT` | Base64 Encoded PNG | Cropped screenshot with coordinate overlay for visual verification |

---

## 6. Deployment & Execution Runbook

### Option 1: Docker Compose (Production / Staging Emulation)
Runs both Backend (FastAPI + Headless Chrome) and Frontend (React + Nginx) with networking pre-configured.

```bash
# Build and run all services
docker-compose up --build

# Run in background (detached)
docker-compose up -d

# View live logs
docker-compose logs -f
```

- **Frontend Application:** [http://localhost:3000](http://localhost:3000)
- **Backend Swagger Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)
- **Backend OpenAPI JSON:** [http://localhost:8000/openapi.json](http://localhost:8000/openapi.json)

---

### Option 2: Local Manual Setup (Developer Environment)

#### 1. Backend Setup
**Prerequisites:** Python 3.9+ & Google Chrome installed.

```bash
# 1. Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Initialize SQLite database
python src/init_db.py

# 4. Start FastAPI server with live reload
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

#### 2. Frontend Setup
**Prerequisites:** Node.js 18+ and npm.

```bash
# 1. Navigate to frontend directory
cd frontend

# 2. Install dependencies
npm install

# 3. Start development server
npm start
```

---

## 7. Testing & Quality Assurance

The project includes an automated test suite under `tests/` utilizing **Pytest**, **HTTPX**, and **pytest-mock** to test components in isolation without launching real browsers in CI:

```bash
# Run full test suite with verbose output
pytest tests -v
```

### Test Coverage Overview:
1. `tests/test_endpoint.py`: Validates FastAPI routing, input validation (coordinates vs keywords), error handling (400, 404, 500), and response payloads.
2. `tests/test_database.py`: Tests SQLite read/write operations, cache hits, record insertion, and format transformations.
3. `tests/test_scraper.py`: Validates screenshot cropping, base64 encoding, and Selenium lifecycle mocking.
4. `tests/test_selenium_operations.py`: Tests Selenium DOM interactions (dropdown selection, coordinate input, Leaflet marker interaction, card parsing).

---

## 8. Operational Constraints & Key Recommendations
1. **DGCA DigitalSky UI Updates:** The scraper targets specific CSS classes (`.visual_card`, `img.leaflet-marker-icon`, etc.). If DGCA updates its web UI layout, the selectors in `src/operations.py` must be adjusted accordingly.
2. **Geocoding Fair-Use Rate Limits:** Geopy uses OpenStreetMap's Nominatim service. For high-volume production use, configure a dedicated geocoder (e.g., Google Maps Geocoding API or self-hosted Pelias/Nominatim).
3. **Headless Chrome in Containers:** Flags `--no-sandbox`, `--disable-dev-shm-usage`, and `--headless` are strictly enforced to prevent Linux shared memory exhaustion.
