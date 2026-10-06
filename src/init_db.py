import sqlite3
import os

# Ensure 'data/' directory exists
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
os.makedirs(DATA_DIR, exist_ok=True)

# Full path to the database file
DB_PATH = os.path.join(DATA_DIR, 'zone_logs.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
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

if __name__ == "__main__":
    if not os.path.exists(DB_PATH):
        init_db()
    else:
        print(f"DB already exists at {os.path.realpath(DB_PATH)}. Skipping initialization")
