"""
Example usage of the NBA Prediction System
This script demonstrates how to use the system programmatically
"""

import pandas as pd
from predict import NBAPredictionSystem

def main():
    # Initialize the prediction system
    print("Initializing NBA Prediction System...")
    system = NBAPredictionSystem()
    
    # Create sample historical game data
    print("\nCreating sample game data...")
    sample_games = pd.DataFrame([
        {
            'home_team': 'Los Angeles Lakers',
            'away_team': 'Golden State Warriors',
            'home_score': 110,
            'away_score': 105
        },
        {
            'home_team': 'Boston Celtics',
            'away_team': 'Los Angeles Lakers',
            'home_score': 98,
            'away_score': 102
        },
        {
            'home_team': 'Golden State Warriors',
            'away_team': 'Boston Celtics',
            'home_score': 115,
            'away_score': 108
        },
        {
            'home_team': 'Miami Heat',
            'away_team': 'Los Angeles Lakers',
            'home_score': 112,
            'away_score': 108
        },
        {
            'home_team': 'Denver Nuggets',
            'away_team': 'Golden State Warriors',
            'home_score': 120,
            'away_score': 115
        },
    ])
    
    # Update models with historical data
    print("Updating models with historical data...")
    system.update_with_historical_data(sample_games)
    
    # Show team rankings
    print("\n" + "="*60)
    print("Current Team ELO Rankings:")
    print("="*60)
    rankings = system.get_team_rankings()
    print(rankings.to_string(index=False))
    
    # Make a prediction
    print("\n" + "="*60)
    print("Game Prediction: Los Angeles Lakers (home) vs Golden State Warriors (away)")
    print("="*60)
    prediction = system.predict_game('Los Angeles Lakers', 'Golden State Warriors')
    
    print(f"\nExpected Score:")
    print(f"  Lakers: {prediction['home_expected_score']:.1f} points")
    print(f"  Warriors: {prediction['away_expected_score']:.1f} points")
    print(f"\nWin Probabilities:")
    print(f"  Lakers: {prediction['home_win_probability']:.2%}")
    print(f"  Warriors: {prediction['away_win_probability']:.2%}")
    print(f"\nExpected Total Points: {prediction['expected_total']:.1f}")
    
    # Analyze with betting odds
    print("\n" + "="*60)
    print("Value Bet Analysis:")
    print("Game: Los Angeles Lakers (home) vs Golden State Warriors (away)")
    print("Odds: Lakers -150, Warriors +130")
    print("="*60)
    
    analysis = system.analyze_game_with_odds(
        'Los Angeles Lakers',
        'Golden State Warriors',
        home_odds=-150,  # Lakers favored
        away_odds=+130   # Warriors underdog
    )
    
    print(f"\nHome Team (Lakers):")
    print(f"  Model Probability: {analysis['home_model_prob']:.2%}")
    print(f"  Implied Probability (from odds): {analysis['home_implied_prob']:.2%}")
    print(f"  Edge: {analysis['home_edge']:.2%}")
    print(f"  Expected Value: {analysis['home_expected_value']:.2%}")
    print(f"  Value Bet: {'✓ YES' if analysis['home_value_bet'] else '✗ NO'}")
    
    print(f"\nAway Team (Warriors):")
    print(f"  Model Probability: {analysis['away_model_prob']:.2%}")
    print(f"  Implied Probability (from odds): {analysis['away_implied_prob']:.2%}")
    print(f"  Edge: {analysis['away_edge']:.2%}")
    print(f"  Expected Value: {analysis['away_expected_value']:.2%}")
    print(f"  Value Bet: {'✓ YES' if analysis['away_value_bet'] else '✗ NO'}")
    
    print("\n" + "="*60)
    print("Analysis complete!")
    print("="*60)

if __name__ == "__main__":
    main()

