# How to Run Zone Detector

You can run this project either using **Docker** (recommended for ease) or **Manually**.

## Option 1: Using Docker (Recommended)

If you have Docker and Docker Compose installed:

1. Open a terminal in the project root (`/zone_detector`).
2. Run the following command:
   ```bash
   docker-compose up --build
   ```
3. Access the application:
   - Frontend: [http://localhost:3000](http://localhost:3000)
   - Backend API: [http://localhost:8000/docs](http://localhost:8000/docs)

## Option 2: Manual Setup

### 1. Backend

**Prerequisites:** Python 3.9+

1. Open a terminal in the project root (`/zone_detector`).
2. (Optional) Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows use: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Initialize the database:
   ```bash
   python src/init_db.py
   ```
5. Run the backend server:
   ```bash
   uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
   ```
   The backend will start at http://localhost:8000.

### 2. Frontend

**Prerequisites:** Node.js and npm

1. Open a **new** terminal window.
2. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```
3. Install dependencies:
   ```bash
   npm install
   ```
4. Start the development server:
   ```bash
   npm start
   ```
   The frontend will start at http://localhost:3000.
