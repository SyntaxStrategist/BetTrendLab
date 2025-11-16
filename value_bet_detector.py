"""
Value Bet Detector
Compares predicted win probabilities to betting odds to find value bets
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
from poisson_model import PoissonScoringModel


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
    
    def implied_probability_to_odds(self, prob: float, format: str = 'american') -> float:
        """
        Convert probability to betting odds
        
        Args:
            prob: Probability (0-1)
            format: 'american' or 'decimal'
        
        Returns:
            Betting odds
        """
        if format == 'american':
            if prob >= 0.5:
                # Favorite: negative odds
                return -100 * prob / (1 - prob)
            else:
                # Underdog: positive odds
                return 100 * (1 - prob) / prob
        elif format == 'decimal':
            return 1.0 / prob
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
    
    def find_value_bets(self, games: List[Dict], odds_source: Optional[str] = None) -> pd.DataFrame:
        """
        Find value bets from a list of games with odds
        
        Expected game format:
        {
            'home_team': str,
            'away_team': str,
            'home_odds': float (american format),
            'away_odds': float (american format),
            'odds_format': str (optional, default 'american')
        }
        
        Returns:
            DataFrame with value bet opportunities
        """
        value_bets = []
        
        for game in games:
            home_team = game.get('home_team')
            away_team = game.get('away_team')
            home_odds = game.get('home_odds')
            away_odds = game.get('away_odds')
            odds_format = game.get('odds_format', 'american')
            
            if not all([home_team, away_team, home_odds, away_odds]):
                continue
            
            # Get model prediction
            prediction = self.model.predict_with_elo(home_team, away_team)
            home_model_prob = prediction['home_win_probability']
            away_model_prob = prediction['away_win_probability']
            
            # Calculate implied probabilities from odds
            home_implied_prob = self.odds_to_implied_probability(home_odds, odds_format)
            away_implied_prob = self.odds_to_implied_probability(away_odds, odds_format)
            
            # Calculate expected values
            home_ev = self.calculate_expected_value(home_model_prob, home_odds, odds_format)
            away_ev = self.calculate_expected_value(away_model_prob, away_odds, odds_format)
            
            # Check for value bets
            if (home_ev >= self.min_value_threshold and 
                home_model_prob >= self.min_probability_threshold):
                value_bets.append({
                    'game': f"{home_team} vs {away_team}",
                    'team': home_team,
                    'bet_type': 'home_win',
                    'model_probability': home_model_prob,
                    'implied_probability': home_implied_prob,
                    'odds': home_odds,
                    'expected_value': home_ev,
                    'edge': home_model_prob - home_implied_prob,
                    'recommended_stake_pct': min(home_ev * 0.1, 0.05)  # Kelly criterion simplified
                })
            
            if (away_ev >= self.min_value_threshold and 
                away_model_prob >= self.min_probability_threshold):
                value_bets.append({
                    'game': f"{home_team} vs {away_team}",
                    'team': away_team,
                    'bet_type': 'away_win',
                    'model_probability': away_model_prob,
                    'implied_probability': away_implied_prob,
                    'odds': away_odds,
                    'expected_value': away_ev,
                    'edge': away_model_prob - away_implied_prob,
                    'recommended_stake_pct': min(away_ev * 0.1, 0.05)
                })
        
        if not value_bets:
            return pd.DataFrame()
        
        df = pd.DataFrame(value_bets)
        df = df.sort_values('expected_value', ascending=False)
        
        return df
    
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
    
    def get_kelly_stake(self, model_prob: float, odds: float, 
                       format: str = 'american', fraction: float = 0.25) -> float:
        """
        Calculate Kelly Criterion stake percentage
        
        Kelly % = (bp - q) / b
        where:
            b = odds - 1 (decimal)
            p = win probability
            q = loss probability (1 - p)
            fraction = fraction of Kelly to bet (typically 0.25 for "quarter Kelly")
        
        Args:
            model_prob: Model's predicted win probability
            odds: Betting odds
            format: 'american' or 'decimal'
            fraction: Fraction of full Kelly to bet (default 0.25)
        
        Returns:
            Recommended stake as percentage of bankroll
        """
        if format == 'american':
            if odds > 0:
                decimal_odds = (odds / 100) + 1
            else:
                decimal_odds = (100 / abs(odds)) + 1
        else:
            decimal_odds = odds
        
        b = decimal_odds - 1
        p = model_prob
        q = 1 - p
        
        if b == 0:
            return 0.0
        
        kelly = (b * p - q) / b
        kelly = max(0, kelly)  # No negative Kelly
        
        return kelly * fraction


if __name__ == "__main__":
    # Example usage
    from poisson_model import PoissonScoringModel
    from elo_ratings import ELORatingSystem
    
    elo = ELORatingSystem()
    model = PoissonScoringModel(elo_system=elo)
    detector = ValueBetDetector(model)
    
    # Example game with odds
    analysis = detector.analyze_single_game(
        home_team='Lakers',
        away_team='Warriors',
        home_odds=-150,  # Lakers favored
        away_odds=+130   # Warriors underdog
    )
    
    print("Value Bet Analysis:")
    print(f"Game: {analysis['home_team']} vs {analysis['away_team']}")
    print(f"\nHome Team ({analysis['home_team']}):")
    print(f"  Model Probability: {analysis['home_model_prob']:.2%}")
    print(f"  Implied Probability: {analysis['home_implied_prob']:.2%}")
    print(f"  Expected Value: {analysis['home_expected_value']:.2%}")
    print(f"  Value Bet: {'YES' if analysis['home_value_bet'] else 'NO'}")
    print(f"\nAway Team ({analysis['away_team']}):")
    print(f"  Model Probability: {analysis['away_model_prob']:.2%}")
    print(f"  Implied Probability: {analysis['away_implied_prob']:.2%}")
    print(f"  Expected Value: {analysis['away_expected_value']:.2%}")
    print(f"  Value Bet: {'YES' if analysis['away_value_bet'] else 'NO'}")

