# BetTrendLab Backend API

FastAPI backend for the NBA prediction system.

## Features

- RESTful API with FastAPI
- ELO rating system
- Poisson scoring model
- Value bet detection
- Automatic daily ELO updates
- Comprehensive logging
- Production-ready Docker setup

## API Endpoints

### Health Check
- `GET /api/v1/health` - Health check endpoint

### Teams
- `GET /api/v1/teams` - Get all teams with ELO ratings

### Rankings
- `GET /api/v1/rankings` - Get full ELO rankings table

### Predictions
- `GET /api/v1/predict?team1=...&team2=...` - Predict a game
  - Optional: `home_team=...` parameter

### Value Bets
- `GET /api/v1/value-bets?team1=...&team2=...&odds1=...&odds2=...` - Analyze value bets
  - Optional: `home_team=...` parameter

### Today's Games
- `GET /api/v1/games/today` - Get today's games with predictions

## Running Locally

1. Install dependencies:
```bash
pip install -r backend/requirements.txt
```

2. Run the server:
```bash
cd backend
uvicorn main:app --reload
```

Or from project root:
```bash
uvicorn backend.main:app --reload
```

## Running with Docker

1. Build the image:
```bash
docker build -t bettrendlab-api .
```

2. Run the container:
```bash
docker run -p 8000:8000 bettrendlab-api
```

## API Documentation

Once the server is running, visit:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Environment Variables

- `PYTHONPATH` - Set to `/app` in Docker
- `PYTHONUNBUFFERED` - Set to `1` for logging

## Logging

Logs are written to:
- Console (stdout)
- File: `backend.log`

## Background Tasks

The API includes a background task that runs daily to update ELO ratings. This is triggered when accessing `/api/v1/games/today`.

