# BetTrendLab Backend Structure

```
backend/
├── api/                    # API routes
│   ├── __init__.py
│   └── routes.py           # FastAPI route handlers
│
├── core/                   # Core prediction engine
│   ├── __init__.py
│   ├── elo_ratings.py     # ELO rating system
│   ├── poisson_model.py   # Poisson scoring model
│   ├── value_bet_detector.py  # Value bet analysis
│   └── data_scraper.py    # Data scraping from ESPN/NBA.com
│
├── models/                 # Pydantic schemas
│   ├── __init__.py
│   └── schemas.py         # Request/response models
│
├── services/              # Business logic layer
│   ├── __init__.py
│   └── prediction_service.py  # Main prediction service
│
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
├── .dockerignore          # Docker ignore file
├── run.sh                 # Startup script
└── README.md              # Backend documentation
```

## Architecture

### API Layer (`api/`)
- FastAPI route handlers
- Request validation
- Response formatting
- Error handling

### Core Layer (`core/`)
- ELO rating calculations
- Poisson model predictions
- Value bet detection
- Data scraping utilities

### Models Layer (`models/`)
- Pydantic schemas for type safety
- Request/response validation
- API documentation generation

### Services Layer (`services/`)
- Business logic orchestration
- Service initialization
- Data persistence
- Background task management

## Data Flow

1. **Request** → API Routes
2. **Routes** → Services Layer
3. **Services** → Core Engine
4. **Core** → Returns predictions
5. **Services** → Formats response
6. **Routes** → Returns JSON

## Key Features

- ✅ RESTful API with FastAPI
- ✅ Type-safe with Pydantic
- ✅ Comprehensive error handling
- ✅ Logging throughout
- ✅ Background tasks for updates
- ✅ Docker-ready for production
- ✅ CORS enabled
- ✅ Auto-generated API docs

