"""
FastAPI routes for NBA prediction API
"""

import logging
from fastapi import APIRouter, HTTPException, Query, BackgroundTasks
from typing import Optional, Dict
from datetime import datetime

from backend.models.schemas import (
    HealthResponse,
    TeamsResponse,
    RankingsResponse,
    PredictionResponse,
    ValueBetsResponse,
    TodaysGamesResponse,
    ErrorResponse
)
from backend.services.prediction_service import get_prediction_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint"""
    return HealthResponse()


@router.get("/teams", response_model=TeamsResponse)
async def get_teams():
    """Get all teams with ELO ratings"""
    try:
        service = get_prediction_service()
        teams = service.get_all_teams()
        return TeamsResponse(teams=teams, count=len(teams))
    except Exception as e:
        logger.error(f"Error getting teams: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/rankings", response_model=RankingsResponse)
async def get_rankings():
    """Get full ELO rankings table"""
    try:
        service = get_prediction_service()
        rankings = service.get_rankings()
        return RankingsResponse(rankings=rankings)
    except Exception as e:
        logger.error(f"Error getting rankings: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/predict", response_model=PredictionResponse)
async def predict_game(
    team1: str = Query(..., description="First team name"),
    team2: str = Query(..., description="Second team name"),
    home_team: Optional[str] = Query(None, description="Home team name (optional, defaults to team1)")
):
    """
    Predict a game between two teams
    
    Returns win probabilities, predicted score, ELO prediction, and Poisson prediction
    """
    try:
        service = get_prediction_service()
        prediction = service.predict_game(team1, team2, home_team)
        return PredictionResponse(**prediction)
    except KeyError as e:
        logger.error(f"Team not found: {e}")
        raise HTTPException(status_code=404, detail=f"Team not found: {e}")
    except Exception as e:
        logger.error(f"Error making prediction: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/value-bets", response_model=ValueBetsResponse)
async def analyze_value_bets(
    team1: str = Query(..., description="First team name"),
    team2: str = Query(..., description="Second team name"),
    odds1: float = Query(..., description="Odds for team1 (American format)"),
    odds2: float = Query(..., description="Odds for team2 (American format)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional, defaults to team1)")
):
    """
    Analyze value bets by comparing predictions to betting odds
    """
    try:
        service = get_prediction_service()
        analysis = service.analyze_value_bets(team1, team2, odds1, odds2, home_team)
        return ValueBetsResponse(**analysis)
    except KeyError as e:
        logger.error(f"Team not found: {e}")
        raise HTTPException(status_code=404, detail=f"Team not found: {e}")
    except Exception as e:
        logger.error(f"Error analyzing value bets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/value-bet", response_model=ValueBetsResponse)
async def analyze_value_bet(
    team1: str = Query(..., description="First team name"),
    team2: str = Query(..., description="Second team name"),
    odds1: float = Query(..., description="Odds for team1 (American format)"),
    odds2: float = Query(..., description="Odds for team2 (American format)"),
    home_team: Optional[str] = Query(None, description="Home team name (optional, defaults to team1)")
):
    """
    Analyze value bets by comparing predictions to betting odds (singular endpoint)
    Returns: edge %, expected value, win probabilities, predicted score
    """
    try:
        service = get_prediction_service()
        analysis = service.analyze_value_bets(team1, team2, odds1, odds2, home_team)
        return ValueBetsResponse(**analysis)
    except KeyError as e:
        logger.error(f"Team not found: {e}")
        raise HTTPException(status_code=404, detail=f"Team not found: {e}")
    except Exception as e:
        logger.error(f"Error analyzing value bets: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/games/today", response_model=TodaysGamesResponse)
async def get_todays_games(background_tasks: BackgroundTasks):
    """
    Get today's games and run predictions automatically
    
    Also triggers background task to update ELO ratings if new game results are available
    """
    try:
        service = get_prediction_service()
        
        # Trigger background update
        background_tasks.add_task(update_elo_daily)
        
        predictions = service.get_todays_games_with_predictions()
        return TodaysGamesResponse(
            date=datetime.now().strftime('%Y-%m-%d'),
            games=predictions,
            count=len(predictions)
        )
    except Exception as e:
        logger.error(f"Error getting today's games: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/update")
async def force_update():
    """
    Force update of stats and ELO ratings by scraping latest data
    
    Returns status of the update operation
    """
    try:
        service = get_prediction_service()
        result = service.force_update_stats_and_elo()
        return result
    except Exception as e:
        logger.error(f"Error in force update: {e}")
        raise HTTPException(status_code=500, detail=str(e))


async def update_elo_daily():
    """Background task to update ELO ratings daily"""
    try:
        logger.info("Running daily ELO update task")
        service = get_prediction_service()
        
        # Try to get recent game results and update
        # This would fetch actual game results from data sources
        # For now, this is a placeholder that can be extended
        
        logger.info("Daily ELO update completed")
    except Exception as e:
        logger.error(f"Error in daily ELO update: {e}")

