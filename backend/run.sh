#!/bin/bash
# Startup script for BetTrendLab API

# Activate virtual environment if it exists
if [ -d "../venv" ]; then
    source ../venv/bin/activate
fi

# Run the API
uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload

