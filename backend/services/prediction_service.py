"""
Prediction service that manages the prediction engine
"""

import os
import logging
from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime
from pathlib import Path

from backend.core.elo_ratings import ELORatingSystem
from backend.core.poisson_model import PoissonScoringModel
from backend.core.value_bet_detector import ValueBetDetector
from backend.core.data_scraper import DataManager

logger = logging.getLogger(__name__)


def get_project_root() -> Path:
    """Get the project root directory"""
    # Go up from backend/services/prediction_service.py to project root
    current_file = Path(__file__).resolve()
    # backend/services/prediction_service.py -> backend/services -> backend -> project root
    return current_file.parent.parent.parent


class PredictionService:
    """Service for managing predictions and models"""
    
    def __init__(self, data_dir: Optional[str] = None):
        """
        Initialize prediction service
        
        Args:
            data_dir: Directory to store data files (defaults to project_root/data)
        """
        if data_dir is None:
            # Use absolute path to project root/data
            project_root = get_project_root()
            self.data_dir = str(project_root / "data")
        else:
            self.data_dir = data_dir
        
        os.makedirs(self.data_dir, exist_ok=True)
        
        # Initialize components
        self.elo = ELORatingSystem()
        self.poisson_model = PoissonScoringModel(elo_system=self.elo)
        self.value_detector = ValueBetDetector(self.poisson_model)
        self.data_manager = DataManager()
        
        # Load existing ratings
        ratings_file = os.path.join(self.data_dir, 'elo_ratings.json')
        logger.info(f"Looking for ELO ratings file at: {ratings_file}")
        logger.info(f"File exists: {os.path.exists(ratings_file)}")
        
        if os.path.exists(ratings_file):
            try:
                self.elo.load_ratings(ratings_file)
                num_teams = len(self.elo.get_all_ratings())
                logger.info(f"Successfully loaded ELO ratings from {ratings_file}")
                logger.info(f"Loaded {num_teams} teams")
            except Exception as e:
                logger.error(f"Error loading ratings from {ratings_file}: {e}", exc_info=True)
                self._initialize_default_teams()
        else:
            logger.warning(f"ELO ratings file not found at {ratings_file}")
            logger.info("Initializing default teams...")
            self._initialize_default_teams()
    
    def _initialize_default_teams(self):
        """Initialize default NBA teams with default ELO ratings"""
        default_teams = {
            "Miami Heat": 1512.99,
            "Milwaukee Bucks": 1456.09,
            "Boston Celtics": 1517.73,
            "Philadelphia 76ers": 1498.67,
            "Phoenix Suns": 1507.00,
            "Denver Nuggets": 1515.39,
            "Los Angeles Lakers": 1521.34,
            "Dallas Mavericks": 1437.34,
            "Golden State Warriors": 1507.48,
            "Brooklyn Nets": 1525.97
        }
        
        for team, rating in default_teams.items():
            self.elo.set_rating(team, rating)
        
        logger.info(f"Initialized {len(default_teams)} default teams")
        
        # Try to save the ratings
        try:
            ratings_file = os.path.join(self.data_dir, 'elo_ratings.json')
            self.elo.save_ratings(ratings_file)
            logger.info(f"Saved default ratings to {ratings_file}")
        except Exception as e:
            logger.warning(f"Could not save ratings to {ratings_file}: {e}")
    
    def get_all_teams(self) -> List[Dict[str, float]]:
        """Get all teams with their ELO ratings"""
        ratings = self.elo.get_all_ratings()
        return [{"team": team, "eloRating": rating} for team, rating in ratings.items()]
    
    def get_rankings(self) -> List[Dict]:
        """Get team rankings sorted by ELO"""
        df = self.elo.get_ratings_df()
        rankings = []
        
        for idx, row in df.iterrows():
            rankings.append({
                "rank": idx + 1,
                "team": row['Team'],
                "eloRating": float(row['ELO_Rating'])
            })
        
        return rankings
    
    def predict_game(self, team1: str, team2: str, home_team: Optional[str] = None) -> Dict:
        """
        Predict a game between two teams
        
        Args:
            team1: First team name
            team2: Second team name
            home_team: Optional home team name (if None, team1 is assumed home)
        
        Returns:
            Prediction dictionary
        """
        if home_team is None:
            home_team = team1
        
        home_team = team1 if home_team == team1 else team2
        away_team = team2 if home_team == team1 else team1
        
        prediction = self.poisson_model.predict_with_elo(home_team, away_team)
        
        # Get ELO-only prediction
        elo_home_prob = self.elo.predict_win_probability(
            home_team, away_team, home_team=home_team
        )
        
        # Get Poisson-only prediction
        poisson_only = self.poisson_model.predict_game(home_team, away_team)
        
        return {
            "homeTeam": home_team,
            "awayTeam": away_team,
            "predictedScore": f"{prediction['home_expected_score']:.1f}-{prediction['away_expected_score']:.1f}",
            "homeExpectedScore": round(prediction['home_expected_score'], 2),
            "awayExpectedScore": round(prediction['away_expected_score'], 2),
            "homeWinProbability": round(prediction['home_win_probability'], 4),
            "awayWinProbability": round(prediction['away_win_probability'], 4),
            "eloPrediction": {
                "homeWinProbability": round(elo_home_prob, 4),
                "awayWinProbability": round(1 - elo_home_prob, 4)
            },
            "poissonPrediction": {
                "homeWinProbability": round(poisson_only['home_win_probability'], 4),
                "awayWinProbability": round(poisson_only['away_win_probability'], 4)
            },
            "expectedTotal": round(prediction['expected_total'], 2)
        }
    
    def analyze_value_bets(self, team1: str, team2: str, 
                          odds1: float, odds2: float,
                          home_team: Optional[str] = None) -> Dict:
        """
        Analyze value bets for a game
        
        Args:
            team1: First team name
            team2: Second team name
            odds1: Odds for team1 (American format)
            odds2: Odds for team2 (American format)
            home_team: Optional home team name
        
        Returns:
            Value bet analysis dictionary
        """
        if home_team is None:
            home_team = team1
        
        home_team = team1 if home_team == team1 else team2
        away_team = team2 if home_team == team1 else team1
        home_odds = odds1 if home_team == team1 else odds2
        away_odds = odds2 if home_team == team1 else odds1
        
        analysis = self.value_detector.analyze_single_game(
            home_team, away_team, home_odds, away_odds
        )
        
        return {
            "homeTeam": home_team,
            "awayTeam": away_team,
            "homeAnalysis": {
                "team": home_team,
                "betType": "home_win",
                "modelProbability": round(analysis['home_model_prob'], 4),
                "impliedProbability": round(analysis['home_implied_prob'], 4),
                "odds": home_odds,
                "expectedValue": round(analysis['home_expected_value'], 4),
                "edge": round(analysis['home_edge'], 4),
                "isValueBet": analysis['home_value_bet']
            },
            "awayAnalysis": {
                "team": away_team,
                "betType": "away_win",
                "modelProbability": round(analysis['away_model_prob'], 4),
                "impliedProbability": round(analysis['away_implied_prob'], 4),
                "odds": away_odds,
                "expectedValue": round(analysis['away_expected_value'], 4),
                "edge": round(analysis['away_edge'], 4),
                "isValueBet": analysis['away_value_bet']
            },
            "expectedScore": analysis['expected_score']
        }
    
    def get_todays_games_with_predictions(self) -> List[Dict]:
        """Get today's games with predictions"""
        games = self.data_manager.get_todays_games()
        predictions = []
        
        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            
            if not home_team or not away_team:
                continue
            
            try:
                prediction = self.predict_game(home_team, away_team, home_team=home_team)
                predictions.append({
                    "homeTeam": home_team,
                    "awayTeam": away_team,
                    "gameTime": game.get('time'),
                    "homeWinProbability": prediction['homeWinProbability'],
                    "awayWinProbability": prediction['awayWinProbability'],
                    "predictedScore": prediction['predictedScore'],
                    "expectedTotal": prediction['expectedTotal']
                })
            except Exception as e:
                logger.error(f"Error predicting game {home_team} vs {away_team}: {e}")
                continue
        
        return predictions
    
    def update_elo_ratings(self, games_df: pd.DataFrame):
        """
        Update ELO ratings with new game results
        
        Args:
            games_df: DataFrame with game results
        """
        try:
            logger.info(f"Updating ELO ratings with {len(games_df)} games")
            self.elo.process_game_history(games_df)
            self.poisson_model.calculate_team_ratings(games_df)
            
            # Save ratings
            ratings_file = os.path.join(self.data_dir, 'elo_ratings.json')
            self.elo.save_ratings(ratings_file)
            logger.info(f"Saved ELO ratings to {ratings_file}")
        except Exception as e:
            logger.error(f"Error updating ELO ratings: {e}")
            raise
    
    def force_update_stats_and_elo(self) -> Dict:
        """
        Force update of stats and ELO ratings by scraping latest data
        
        Returns:
            Dictionary with update status and results
        """
        try:
            logger.info("Starting forced update of stats and ELO ratings")
            
            # Try to get recent game results
            recent_games = self.data_manager.get_recent_results(days=7)
            
            if recent_games:
                # Convert to DataFrame
                games_df = pd.DataFrame(recent_games)
                
                # Update ELO and stats
                self.update_elo_ratings(games_df)
                
                return {
                    "status": "success",
                    "message": f"Updated with {len(recent_games)} recent games",
                    "games_processed": len(recent_games),
                    "teams_updated": len(self.elo.get_all_ratings())
                }
            else:
                # If no recent games found, return partial status
                logger.info("No recent games found, ELO ratings unchanged")
                
                return {
                    "status": "partial",
                    "message": "No recent game results found. ELO ratings unchanged.",
                    "games_processed": 0,
                    "teams_updated": len(self.elo.get_all_ratings())
                }
                
        except Exception as e:
            logger.error(f"Error in force update: {e}")
            return {
                "status": "error",
                "message": str(e),
                "games_processed": 0,
                "teams_updated": 0
            }


# Global service instance
_prediction_service: Optional[PredictionService] = None


def get_prediction_service() -> PredictionService:
    """Get or create prediction service singleton"""
    global _prediction_service
    if _prediction_service is None:
        _prediction_service = PredictionService()
    return _prediction_service

