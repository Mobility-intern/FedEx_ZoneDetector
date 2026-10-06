#!/bin/sh
set -e

echo "[INFO][$(date)] Running init_db.py..."
python src/init_db.py

echo "[INFO][$(date)] Starting FastAPI app..."
uvicorn src.main:app --host 0.0.0.0 --port 8000
