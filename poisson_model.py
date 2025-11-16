"""
Poisson Scoring Model for NBA Games
Predicts game scores and outcomes using Poisson distribution
"""

import pandas as pd
import numpy as np
from scipy.stats import poisson
from typing import Dict, Tuple, Optional
from elo_ratings import ELORatingSystem


class PoissonScoringModel:
    """
    Poisson model for predicting NBA game scores
    
    Assumes that points scored follow a Poisson distribution
    with mean lambda based on team offensive/defensive ratings
    """
    
    def __init__(self, elo_system: Optional[ELORatingSystem] = None):
        """
        Initialize Poisson model
        
        Args:
            elo_system: Optional ELO rating system for team strength
        """
        self.elo = elo_system
        self.team_offensive_ratings = {}  # Average points scored per game
        self.team_defensive_ratings = {}  # Average points allowed per game
        self.league_avg_offense = 110.0  # League average points per game
        self.league_avg_defense = 110.0
    
    def calculate_team_ratings(self, game_data: pd.DataFrame):
        """
        Calculate offensive and defensive ratings from game data
        
        Expected columns:
        - home_team, away_team: Team names
        - home_score, away_score: Points scored
        """
        team_stats = {}
        
        for _, game in game_data.iterrows():
            home_team = game.get('home_team', game.get('HOME_TEAM'))
            away_team = game.get('away_team', game.get('AWAY_TEAM'))
            home_score = game.get('home_score', game.get('HOME_SCORE', 0))
            away_score = game.get('away_score', game.get('AWAY_SCORE', 0))
            
            if pd.isna(home_team) or pd.isna(away_team):
                continue
            
            # Initialize team stats
            if home_team not in team_stats:
                team_stats[home_team] = {'points_for': [], 'points_against': []}
            if away_team not in team_stats:
                team_stats[away_team] = {'points_for': [], 'points_against': []}
            
            # Record points
            team_stats[home_team]['points_for'].append(home_score)
            team_stats[home_team]['points_against'].append(away_score)
            team_stats[away_team]['points_for'].append(away_score)
            team_stats[away_team]['points_against'].append(home_score)
        
        # Calculate averages
        for team, stats in team_stats.items():
            if stats['points_for']:
                self.team_offensive_ratings[team] = np.mean(stats['points_for'])
            if stats['points_against']:
                self.team_defensive_ratings[team] = np.mean(stats['points_against'])
        
        # Update league averages
        if self.team_offensive_ratings:
            self.league_avg_offense = np.mean(list(self.team_offensive_ratings.values()))
        if self.team_defensive_ratings:
            self.league_avg_defense = np.mean(list(self.team_defensive_ratings.values()))
    
    def get_offensive_rating(self, team: str) -> float:
        """Get offensive rating (points scored per game)"""
        return self.team_offensive_ratings.get(team, self.league_avg_offense)
    
    def get_defensive_rating(self, team: str) -> float:
        """Get defensive rating (points allowed per game)"""
        return self.team_defensive_ratings.get(team, self.league_avg_defense)
    
    def predict_score(self, team: str, opponent: str, is_home: bool = True) -> float:
        """
        Predict expected score for a team
        
        Formula: lambda = (team_offense / league_avg_offense) * 
                         (opponent_defense / league_avg_defense) * 
                         league_avg_offense * home_factor
        
        Args:
            team: Name of team
            opponent: Name of opponent
            is_home: Whether team is playing at home
        
        Returns:
            Expected points scored
        """
        team_offense = self.get_offensive_rating(team)
        opponent_defense = self.get_defensive_rating(opponent)
        
        # Home advantage factor (typically ~3 points)
        home_factor = 1.03 if is_home else 0.97
        
        # Calculate expected score
        expected_score = (team_offense / self.league_avg_offense) * \
                        (opponent_defense / self.league_avg_defense) * \
                        self.league_avg_offense * home_factor
        
        return max(expected_score, 80.0)  # Minimum reasonable score
    
    def predict_game(self, home_team: str, away_team: str) -> Dict:
        """
        Predict a game using Poisson model
        
        Returns:
            Dictionary with predictions including:
            - home_score: Expected home team score
            - away_score: Expected away team score
            - home_win_prob: Probability home team wins
            - away_win_prob: Probability away team wins
            - total_points: Expected total points
            - score_distributions: Probability distributions
        """
        # Predict expected scores
        home_lambda = self.predict_score(home_team, away_team, is_home=True)
        away_lambda = self.predict_score(away_team, home_team, is_home=False)
        
        # Create score distributions (using Poisson for each possible score)
        max_score = int(max(home_lambda, away_lambda) * 1.5) + 20
        home_scores = np.arange(0, max_score)
        away_scores = np.arange(0, max_score)
        
        # Calculate probability distributions
        home_probs = poisson.pmf(home_scores, home_lambda)
        away_probs = poisson.pmf(away_scores, away_lambda)
        
        # Calculate win probabilities
        home_win_prob = 0.0
        away_win_prob = 0.0
        tie_prob = 0.0
        
        for h_score in home_scores:
            for a_score in away_scores:
                prob = home_probs[h_score] * away_probs[a_score]
                if h_score > a_score:
                    home_win_prob += prob
                elif a_score > h_score:
                    away_win_prob += prob
                else:
                    tie_prob += prob
        
        # Normalize (handle ties by splitting probability)
        total_prob = home_win_prob + away_win_prob + tie_prob
        if total_prob > 0:
            home_win_prob /= total_prob
            away_win_prob /= total_prob
            # Split tie probability between teams
            home_win_prob += tie_prob / (2 * total_prob)
            away_win_prob += tie_prob / (2 * total_prob)
        
        # Calculate expected total points
        total_points = home_lambda + away_lambda
        
        return {
            'home_team': home_team,
            'away_team': away_team,
            'home_expected_score': home_lambda,
            'away_expected_score': away_lambda,
            'home_win_probability': home_win_prob,
            'away_win_probability': away_win_prob,
            'expected_total': total_points,
            'home_score_distribution': dict(zip(home_scores, home_probs)),
            'away_score_distribution': dict(zip(away_scores, away_probs))
        }
    
    def predict_with_elo(self, home_team: str, away_team: str) -> Dict:
        """
        Predict game using both Poisson and ELO, combining results
        
        Returns:
            Combined prediction dictionary
        """
        poisson_pred = self.predict_game(home_team, away_team)
        
        if self.elo:
            # Get ELO-based win probability
            elo_home_prob = self.elo.predict_win_probability(
                home_team, away_team, home_team=home_team
            )
            
            # Combine probabilities (weighted average)
            # You can adjust weights based on which model performs better
            poisson_weight = 0.6
            elo_weight = 0.4
            
            combined_home_prob = (poisson_weight * poisson_pred['home_win_probability'] + 
                                 elo_weight * elo_home_prob)
            combined_away_prob = 1.0 - combined_home_prob
            
            poisson_pred['home_win_probability'] = combined_home_prob
            poisson_pred['away_win_probability'] = combined_away_prob
            poisson_pred['elo_home_probability'] = elo_home_prob
            poisson_pred['elo_away_probability'] = 1.0 - elo_home_prob
        
        return poisson_pred
    
    def get_most_likely_score(self, prediction: Dict) -> Tuple[int, int]:
        """
        Get the most likely final score from prediction
        
        Returns:
            Tuple of (home_score, away_score)
        """
        home_dist = prediction['home_score_distribution']
        away_dist = prediction['away_score_distribution']
        
        most_likely_home = max(home_dist.items(), key=lambda x: x[1])[0]
        most_likely_away = max(away_dist.items(), key=lambda x: x[1])[0]
        
        return (int(most_likely_home), int(most_likely_away))


if __name__ == "__main__":
    # Example usage
    from elo_ratings import ELORatingSystem
    
    elo = ELORatingSystem()
    model = PoissonScoringModel(elo_system=elo)
    
    # Example game data
    example_games = pd.DataFrame([
        {'home_team': 'Lakers', 'away_team': 'Warriors', 'home_score': 110, 'away_score': 105},
        {'home_team': 'Celtics', 'away_team': 'Lakers', 'home_score': 98, 'away_score': 102},
        {'home_team': 'Warriors', 'away_team': 'Celtics', 'home_score': 115, 'away_score': 108},
    ])
    
    # Calculate team ratings
    model.calculate_team_ratings(example_games)
    
    # Make prediction
    prediction = model.predict_with_elo('Lakers', 'Warriors')
    
    print("Game Prediction: Lakers (home) vs Warriors (away)")
    print(f"Expected Score: Lakers {prediction['home_expected_score']:.1f} - Warriors {prediction['away_expected_score']:.1f}")
    print(f"Lakers Win Probability: {prediction['home_win_probability']:.2%}")
    print(f"Warriors Win Probability: {prediction['away_win_probability']:.2%}")
    print(f"Expected Total Points: {prediction['expected_total']:.1f}")

