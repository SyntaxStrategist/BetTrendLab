"""
ELO Rating System for NBA Teams
Calculates team strength ratings based on game results
"""

import pandas as pd
import numpy as np
from typing import Dict, Optional
from datetime import datetime
import json
import os


class ELORatingSystem:
    """
    ELO rating system for NBA teams
    
    ELO Formula:
    - Expected score: E_A = 1 / (1 + 10^((R_B - R_A) / 400))
    - Rating update: R_A_new = R_A + K * (S_A - E_A)
    where:
        R_A = current rating of team A
        R_B = current rating of team B
        K = K-factor (weight of the game)
        S_A = actual score (1 for win, 0 for loss, 0.5 for tie)
    """
    
    DEFAULT_RATING = 1500.0
    K_FACTOR = 20.0  # Standard K-factor for chess, can be adjusted for NBA
    HOME_ADVANTAGE = 50.0  # Home team gets +50 rating boost
    
    def __init__(self, initial_ratings: Optional[Dict[str, float]] = None):
        """
        Initialize ELO system
        
        Args:
            initial_ratings: Optional dict of team names to initial ratings
        """
        if initial_ratings:
            self.ratings = initial_ratings.copy()
        else:
            self.ratings = {}
        
        self.game_history = []
    
    def get_rating(self, team: str) -> float:
        """Get current rating for a team"""
        return self.ratings.get(team, self.DEFAULT_RATING)
    
    def set_rating(self, team: str, rating: float):
        """Set rating for a team"""
        self.ratings[team] = rating
    
    def expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for team A against team B
        
        Returns:
            Expected score (0-1) for team A
        """
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    
    def update_ratings(self, team_a: str, team_b: str, score_a: float, 
                      home_team: Optional[str] = None, k_factor: Optional[float] = None):
        """
        Update ELO ratings after a game
        
        Args:
            team_a: Name of team A
            team_b: Name of team B
            score_a: Score for team A (1.0 for win, 0.0 for loss, 0.5 for tie)
            home_team: Name of home team (if None, no home advantage)
            k_factor: K-factor for this game (if None, uses default)
        """
        if k_factor is None:
            k_factor = self.K_FACTOR
        
        # Get current ratings
        rating_a = self.get_rating(team_a)
        rating_b = self.get_rating(team_b)
        
        # Apply home advantage
        if home_team == team_a:
            rating_a += self.HOME_ADVANTAGE
        elif home_team == team_b:
            rating_b += self.HOME_ADVANTAGE
        
        # Calculate expected scores
        expected_a = self.expected_score(rating_a, rating_b)
        expected_b = 1.0 - expected_a
        
        # Calculate score for team B
        score_b = 1.0 - score_a
        
        # Update ratings
        rating_a_new = rating_a + k_factor * (score_a - expected_a)
        rating_b_new = rating_b + k_factor * (score_b - expected_b)
        
        # Remove home advantage from new ratings
        if home_team == team_a:
            rating_a_new -= self.HOME_ADVANTAGE
        elif home_team == team_b:
            rating_b_new -= self.HOME_ADVANTAGE
        
        # Update ratings
        self.set_rating(team_a, rating_a_new)
        self.set_rating(team_b, rating_b_new)
        
        # Record game
        self.game_history.append({
            'team_a': team_a,
            'team_b': team_b,
            'score_a': score_a,
            'rating_a_before': rating_a,
            'rating_b_before': rating_b,
            'rating_a_after': rating_a_new,
            'rating_b_after': rating_b_new,
            'home_team': home_team
        })
    
    def process_game_result(self, home_team: str, away_team: str, 
                           home_score: int, away_score: int):
        """
        Process a game result and update ratings
        
        Args:
            home_team: Name of home team
            away_team: Name of away team
            home_score: Points scored by home team
            away_score: Points scored by away team
        """
        if home_score > away_score:
            # Home team wins
            self.update_ratings(home_team, away_team, 1.0, home_team=home_team)
        elif away_score > home_score:
            # Away team wins
            self.update_ratings(away_team, home_team, 1.0, home_team=home_team)
        else:
            # Tie (rare in NBA, but handle it)
            self.update_ratings(home_team, away_team, 0.5, home_team=home_team)
    
    def predict_win_probability(self, team_a: str, team_b: str, 
                               home_team: Optional[str] = None) -> float:
        """
        Predict win probability for team A against team B
        
        Args:
            team_a: Name of team A
            team_b: Name of team B
            home_team: Name of home team (if None, no home advantage)
        
        Returns:
            Win probability for team A (0-1)
        """
        rating_a = self.get_rating(team_a)
        rating_b = self.get_rating(team_b)
        
        # Apply home advantage
        if home_team == team_a:
            rating_a += self.HOME_ADVANTAGE
        elif home_team == team_b:
            rating_b += self.HOME_ADVANTAGE
        
        return self.expected_score(rating_a, rating_b)
    
    def process_game_history(self, games: pd.DataFrame):
        """
        Process a DataFrame of historical games
        
        Expected columns:
        - home_team: Name of home team
        - away_team: Name of away team
        - home_score: Points scored by home team
        - away_score: Points scored by away team
        """
        for _, game in games.iterrows():
            home_team = game.get('home_team', game.get('HOME_TEAM'))
            away_team = game.get('away_team', game.get('AWAY_TEAM'))
            home_score = game.get('home_score', game.get('HOME_SCORE', 0))
            away_score = game.get('away_score', game.get('AWAY_SCORE', 0))
            
            if pd.notna(home_team) and pd.notna(away_team):
                self.process_game_result(home_team, away_team, int(home_score), int(away_score))
    
    def get_ratings_df(self) -> pd.DataFrame:
        """Get current ratings as DataFrame"""
        teams = list(self.ratings.keys())
        ratings = [self.ratings[team] for team in teams]
        
        df = pd.DataFrame({
            'Team': teams,
            'ELO_Rating': ratings
        })
        
        return df.sort_values('ELO_Rating', ascending=False)
    
    def save_ratings(self, filepath: str):
        """Save ratings to JSON file"""
        with open(filepath, 'w') as f:
            json.dump(self.ratings, f, indent=2)
    
    def load_ratings(self, filepath: str):
        """Load ratings from JSON file"""
        if os.path.exists(filepath):
            with open(filepath, 'r') as f:
                self.ratings = json.load(f)
    
    def reset_ratings(self):
        """Reset all ratings to default"""
        self.ratings = {}
        self.game_history = []


if __name__ == "__main__":
    # Example usage
    elo = ELORatingSystem()
    
    # Example games
    example_games = pd.DataFrame([
        {'home_team': 'Lakers', 'away_team': 'Warriors', 'home_score': 110, 'away_score': 105},
        {'home_team': 'Celtics', 'away_team': 'Lakers', 'home_score': 98, 'away_score': 102},
        {'home_team': 'Warriors', 'away_team': 'Celtics', 'home_score': 115, 'away_score': 108},
    ])
    
    elo.process_game_history(example_games)
    
    print("Current ELO Ratings:")
    print(elo.get_ratings_df())
    
    print("\nWin Probability: Lakers vs Warriors (Lakers at home)")
    prob = elo.predict_win_probability('Lakers', 'Warriors', home_team='Lakers')
    print(f"Lakers win probability: {prob:.2%}")

