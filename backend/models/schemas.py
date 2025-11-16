"""
Pydantic schemas for API requests and responses
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict
from datetime import datetime


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = "healthy"
    timestamp: datetime = Field(default_factory=datetime.now)


class TeamRating(BaseModel):
    """Team with ELO rating"""
    team: str
    elo_rating: float = Field(..., alias="eloRating")
    
    class Config:
        populate_by_name = True


class TeamsResponse(BaseModel):
    """Response for /teams endpoint"""
    teams: List[TeamRating]
    count: int


class RankingItem(BaseModel):
    """Single ranking entry"""
    rank: int
    team: str
    elo_rating: float = Field(..., alias="eloRating")
    
    class Config:
        populate_by_name = True


class RankingsResponse(BaseModel):
    """Response for /rankings endpoint"""
    rankings: List[RankingItem]
    updated_at: Optional[datetime] = Field(None, alias="updatedAt")
    
    class Config:
        populate_by_name = True


class PredictionResponse(BaseModel):
    """Response for /predict endpoint"""
    home_team: str = Field(..., alias="homeTeam")
    away_team: str = Field(..., alias="awayTeam")
    predicted_score: str = Field(..., alias="predictedScore")
    home_expected_score: float = Field(..., alias="homeExpectedScore")
    away_expected_score: float = Field(..., alias="awayExpectedScore")
    home_win_probability: float = Field(..., alias="homeWinProbability")
    away_win_probability: float = Field(..., alias="awayWinProbability")
    elo_prediction: Dict[str, float] = Field(..., alias="eloPrediction")
    poisson_prediction: Dict[str, float] = Field(..., alias="poissonPrediction")
    expected_total: float = Field(..., alias="expectedTotal")
    
    class Config:
        populate_by_name = True


class ValueBetAnalysis(BaseModel):
    """Value bet analysis for a team"""
    team: str
    bet_type: str = Field(..., alias="betType")
    model_probability: float = Field(..., alias="modelProbability")
    implied_probability: float = Field(..., alias="impliedProbability")
    odds: float
    expected_value: float = Field(..., alias="expectedValue")
    edge: float
    is_value_bet: bool = Field(..., alias="isValueBet")
    
    class Config:
        populate_by_name = True


class ValueBetsResponse(BaseModel):
    """Response for /value-bets endpoint"""
    home_team: str = Field(..., alias="homeTeam")
    away_team: str = Field(..., alias="awayTeam")
    home_analysis: ValueBetAnalysis = Field(..., alias="homeAnalysis")
    away_analysis: ValueBetAnalysis = Field(..., alias="awayAnalysis")
    expected_score: str = Field(..., alias="expectedScore")
    
    class Config:
        populate_by_name = True


class GamePrediction(BaseModel):
    """Game prediction for today's games"""
    home_team: str = Field(..., alias="homeTeam")
    away_team: str = Field(..., alias="awayTeam")
    game_time: Optional[str] = Field(None, alias="gameTime")
    home_win_probability: float = Field(..., alias="homeWinProbability")
    away_win_probability: float = Field(..., alias="awayWinProbability")
    predicted_score: str = Field(..., alias="predictedScore")
    expected_total: float = Field(..., alias="expectedTotal")
    
    class Config:
        populate_by_name = True


class TodaysGamesResponse(BaseModel):
    """Response for /games/today endpoint"""
    date: str
    games: List[GamePrediction]
    count: int


class ErrorResponse(BaseModel):
    """Error response"""
    error: str
    detail: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.now)

