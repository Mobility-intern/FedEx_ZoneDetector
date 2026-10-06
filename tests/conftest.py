import sqlite3
import tempfile
import os
import pytest
from src import db as db_module
from src.main import app
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from PIL import Image
from io import BytesIO

@pytest.fixture
def temp_db(monkeypatch):
    """Provides a temporary database and patches the app to use it."""
    temp = tempfile.NamedTemporaryFile(delete=False, suffix='.db')
    temp.close()

    # Monkeypatch the global DB_FILE used in src/db.py
    monkeypatch.setattr(db_module, "DB_FILE", temp.name)

    # Initialize schema
    conn = sqlite3.connect(temp.name)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS zone_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT,
            input_type TEXT,
            input_value TEXT,
            detected_zones TEXT,
            zone_names TEXT,
            zone_details TEXT,
            screenshot_base64 TEXT
        )
    ''')
    conn.commit()
    conn.close()

    yield temp.name

    os.unlink(temp.name)
    
@pytest.fixture
def client(temp_db):
    """
    Returns a TestClient instance using the app and patched DB.
    """
    return TestClient(app)

@pytest.fixture
def mock_driver():
    driver = MagicMock()
    driver.get_screenshot_as_png.return_value = create_dummy_png()
    return driver

def create_dummy_png():
    img = Image.new('RGB', (100, 100), color='white')
    buf = BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()
