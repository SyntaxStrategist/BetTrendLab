"""
Value Bet Detector
Compares predicted win probabilities to betting odds to find value bets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from .poisson_model import PoissonScoringModel


class ValueBetDetector:
    """
    Detects value bets by comparing model predictions to betting odds
    
    A value bet exists when: implied_probability < model_probability
    Value = (model_probability * odds) - 1
    """
    
    def __init__(self, model: PoissonScoringModel):
        """
        Initialize value bet detector
        
        Args:
            model: Prediction model (PoissonScoringModel)
        """
        self.model = model
        self.min_value_threshold = 0.05  # Minimum 5% expected value
        self.min_probability_threshold = 0.10  # Minimum 10% win probability
    
    def odds_to_implied_probability(self, odds: float, format: str = 'american') -> float:
        """
        Convert betting odds to implied probability
        
        Args:
            odds: Betting odds
            format: 'american' (e.g., -150, +200) or 'decimal' (e.g., 1.67, 3.00)
        
        Returns:
            Implied probability (0-1)
        """
        if format == 'american':
            if odds > 0:
                # Positive odds: probability = 100 / (odds + 100)
                return 100 / (odds + 100)
            else:
                # Negative odds: probability = |odds| / (|odds| + 100)
                return abs(odds) / (abs(odds) + 100)
        elif format == 'decimal':
            # Decimal odds: probability = 1 / odds
            return 1.0 / odds
        else:
            raise ValueError(f"Unknown odds format: {format}")
    
    def calculate_expected_value(self, model_prob: float, odds: float, 
                                format: str = 'american') -> float:
        """
        Calculate expected value of a bet
        
        EV = (model_probability * payout) - 1
        
        Args:
            model_prob: Model's predicted win probability
            odds: Betting odds
            format: 'american' or 'decimal'
        
        Returns:
            Expected value (positive = value bet)
        """
        if format == 'american':
            if odds > 0:
                # Positive odds: payout = (odds / 100) + 1
                payout = (odds / 100) + 1
            else:
                # Negative odds: payout = (100 / |odds|) + 1
                payout = (100 / abs(odds)) + 1
        elif format == 'decimal':
            payout = odds
        else:
            raise ValueError(f"Unknown odds format: {format}")
        
        ev = (model_prob * payout) - 1.0
        return ev
    
    def analyze_single_game(self, home_team: str, away_team: str,
                           home_odds: float, away_odds: float,
                           odds_format: str = 'american') -> Dict:
        """
        Analyze a single game for value betting opportunities
        
        Returns:
            Dictionary with analysis results
        """
        # Get prediction
        prediction = self.model.predict_with_elo(home_team, away_team)
        
        # Calculate probabilities and values
        home_implied_prob = self.odds_to_implied_probability(home_odds, odds_format)
        away_implied_prob = self.odds_to_implied_probability(away_odds, odds_format)
        
        home_ev = self.calculate_expected_value(
            prediction['home_win_probability'], home_odds, odds_format
        )
        away_ev = self.calculate_expected_value(
            prediction['away_win_probability'], away_odds, odds_format
        )
        
        # Determine value bets
        home_value = home_ev >= self.min_value_threshold
        away_value = away_ev >= self.min_value_threshold
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_model_prob': prediction['home_win_probability'],
            'away_model_prob': prediction['away_win_probability'],
            'home_implied_prob': home_implied_prob,
            'away_implied_prob': away_implied_prob,
            'home_odds': home_odds,
            'away_odds': away_odds,
            'home_expected_value': home_ev,
            'away_expected_value': away_ev,
            'home_value_bet': home_value,
            'away_value_bet': away_value,
            'home_edge': prediction['home_win_probability'] - home_implied_prob,
            'away_edge': prediction['away_win_probability'] - away_implied_prob,
            'expected_score': f"{prediction['home_expected_score']:.1f}-{prediction['away_expected_score']:.1f}"
        }

