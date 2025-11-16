"""
Main NBA Prediction Script
Combines all components to make predictions and find value bets
"""

import pandas as pd
import numpy as np
from datetime import datetime
import argparse
import json
import os

from data_scraper import DataManager
from elo_ratings import ELORatingSystem
from poisson_model import PoissonScoringModel
from value_bet_detector import ValueBetDetector


class NBAPredictionSystem:
    """Main prediction system that combines all components"""
    
    def __init__(self, data_dir: str = 'data'):
        """
        Initialize the prediction system
        
        Args:
            data_dir: Directory to store data files
        """
        self.data_dir = data_dir
        os.makedirs(data_dir, exist_ok=True)
        
        # Initialize components
        self.data_manager = DataManager()
        self.elo = ELORatingSystem()
        self.poisson_model = PoissonScoringModel(elo_system=self.elo)
        self.value_detector = ValueBetDetector(self.poisson_model)
        
        # Load existing ratings if available
        ratings_file = os.path.join(data_dir, 'elo_ratings.json')
        if os.path.exists(ratings_file):
            self.elo.load_ratings(ratings_file)
            print(f"Loaded ELO ratings from {ratings_file}")
    
    def update_with_historical_data(self, games_df: pd.DataFrame):
        """
        Update models with historical game data
        
        Args:
            games_df: DataFrame with historical games
        """
        print("Updating ELO ratings...")
        self.elo.process_game_history(games_df)
        
        print("Calculating team offensive/defensive ratings...")
        self.poisson_model.calculate_team_ratings(games_df)
        
        # Save updated ratings
        ratings_file = os.path.join(self.data_dir, 'elo_ratings.json')
        self.elo.save_ratings(ratings_file)
        print(f"Saved ELO ratings to {ratings_file}")
    
    def predict_game(self, home_team: str, away_team: str) -> dict:
        """
        Predict a single game
        
        Args:
            home_team: Name of home team
            away_team: Name of away team
        
        Returns:
            Prediction dictionary
        """
        return self.poisson_model.predict_with_elo(home_team, away_team)
    
    def find_value_bets(self, upcoming_games: list) -> pd.DataFrame:
        """
        Find value betting opportunities
        
        Args:
            upcoming_games: List of games with odds information
        
        Returns:
            DataFrame with value bet opportunities
        """
        return self.value_detector.find_value_bets(upcoming_games)
    
    def get_team_rankings(self) -> pd.DataFrame:
        """Get current team ELO rankings"""
        return self.elo.get_ratings_df()
    
    def analyze_game_with_odds(self, home_team: str, away_team: str,
                              home_odds: float, away_odds: float) -> dict:
        """Analyze a game with betting odds"""
        return self.value_detector.analyze_single_game(
            home_team, away_team, home_odds, away_odds
        )


def create_sample_data():
    """Create sample game data for testing"""
    # Sample NBA teams
    teams = [
        'Los Angeles Lakers', 'Golden State Warriors', 'Boston Celtics',
        'Miami Heat', 'Denver Nuggets', 'Phoenix Suns', 'Milwaukee Bucks',
        'Philadelphia 76ers', 'Dallas Mavericks', 'Brooklyn Nets'
    ]
    
    # Generate sample games
    np.random.seed(42)
    games = []
    
    for i in range(50):
        home = np.random.choice(teams)
        away = np.random.choice([t for t in teams if t != home])
        
        # Simulate scores based on team strength
        home_score = int(np.random.normal(110, 10))
        away_score = int(np.random.normal(108, 10))
        
        games.append({
            'home_team': home,
            'away_team': away,
            'home_score': max(80, home_score),
            'away_score': max(80, away_score),
            'date': datetime.now().strftime('%Y-%m-%d')
        })
    
    return pd.DataFrame(games)


def main():
    parser = argparse.ArgumentParser(description='NBA Prediction System')
    parser.add_argument('--predict', nargs=2, metavar=('HOME', 'AWAY'),
                       help='Predict a game (home_team away_team)')
    parser.add_argument('--analyze', nargs=4, metavar=('HOME', 'AWAY', 'HOME_ODDS', 'AWAY_ODDS'),
                       help='Analyze a game with odds')
    parser.add_argument('--rankings', action='store_true',
                       help='Show team rankings')
    parser.add_argument('--update', action='store_true',
                       help='Update models with sample data')
    parser.add_argument('--sample-data', action='store_true',
                       help='Use sample data for testing')
    
    args = parser.parse_args()
    
    # Initialize system
    system = NBAPredictionSystem()
    
    # Update with sample data if requested
    if args.update or args.sample_data:
        print("Creating sample data...")
        sample_games = create_sample_data()
        system.update_with_historical_data(sample_games)
        print("Models updated with sample data")
    
    # Show rankings
    if args.rankings:
        rankings = system.get_team_rankings()
        print("\nCurrent Team ELO Rankings:")
        print(rankings.to_string(index=False))
    
    # Predict a game
    if args.predict:
        home_team, away_team = args.predict
        print(f"\nPredicting: {home_team} (home) vs {away_team} (away)")
        prediction = system.predict_game(home_team, away_team)
        
        print(f"\nExpected Score: {home_team} {prediction['home_expected_score']:.1f} - "
              f"{away_team} {prediction['away_expected_score']:.1f}")
        print(f"{home_team} Win Probability: {prediction['home_win_probability']:.2%}")
        print(f"{away_team} Win Probability: {prediction['away_win_probability']:.2%}")
        print(f"Expected Total Points: {prediction['expected_total']:.1f}")
    
    # Analyze with odds
    if args.analyze:
        home_team, away_team, home_odds, away_odds = args.analyze
        home_odds = float(home_odds)
        away_odds = float(away_odds)
        
        print(f"\nAnalyzing: {home_team} (home) vs {away_team} (away)")
        print(f"Odds: {home_team} {home_odds}, {away_team} {away_odds}")
        
        analysis = system.analyze_game_with_odds(home_team, away_team, home_odds, away_odds)
        
        print(f"\n{'='*60}")
        print(f"Home Team ({home_team}):")
        print(f"  Model Probability: {analysis['home_model_prob']:.2%}")
        print(f"  Implied Probability: {analysis['home_implied_prob']:.2%}")
        print(f"  Edge: {analysis['home_edge']:.2%}")
        print(f"  Expected Value: {analysis['home_expected_value']:.2%}")
        print(f"  Value Bet: {'✓ YES' if analysis['home_value_bet'] else '✗ NO'}")
        
        print(f"\nAway Team ({away_team}):")
        print(f"  Model Probability: {analysis['away_model_prob']:.2%}")
        print(f"  Implied Probability: {analysis['away_implied_prob']:.2%}")
        print(f"  Edge: {analysis['away_edge']:.2%}")
        print(f"  Expected Value: {analysis['away_expected_value']:.2%}")
        print(f"  Value Bet: {'✓ YES' if analysis['away_value_bet'] else '✗ NO'}")
        print(f"{'='*60}")
    
    # If no arguments, show help
    if not any([args.predict, args.analyze, args.rankings, args.update]):
        parser.print_help()
        print("\nExample usage:")
        print("  python predict.py --update --rankings")
        print("  python predict.py --predict 'Los Angeles Lakers' 'Golden State Warriors'")
        print("  python predict.py --analyze 'Los Angeles Lakers' 'Golden State Warriors' -150 +130")


if __name__ == "__main__":
    main()

