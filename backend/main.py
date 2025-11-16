"""
FastAPI main application
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from datetime import datetime

from backend.api.routes import router
from backend.services.prediction_service import get_prediction_service

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('backend.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown"""
    # Startup
    logger.info("Starting BetTrendLab API...")
    try:
        # Initialize prediction service
        service = get_prediction_service()
        logger.info("Prediction service initialized")
    except Exception as e:
        logger.error(f"Error initializing service: {e}")
    
    yield
    
    # Shutdown
    logger.info("Shutting down BetTrendLab API...")


# Create FastAPI app
app = FastAPI(
    title="BetTrendLab API",
    description="NBA Prediction System with ELO ratings, Poisson model, and value bet detection",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify actual origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers with prefix
app.include_router(router, prefix="/api/v1", tags=["predictions"])

# Include root-level routes for simpler access
app.include_router(router, tags=["predictions"])


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Global exception handler"""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal server error",
            "detail": str(exc),
            "timestamp": datetime.now().isoformat()
        }
    )


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "BetTrendLab API",
        "version": "1.0.0",
        "docs": "/docs",
        "health": "/api/v1/health"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

