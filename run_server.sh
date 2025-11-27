#!/bin/bash
# Activate venv and run FastAPI server
source venv/bin/activate
python -m uvicorn scripts.app:app --reload --host 127.0.0.1 --port 8000

