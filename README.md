# NBA Prediction System

A comprehensive NBA prediction system that uses ELO ratings, Poisson scoring models, and value-bet detection to analyze games and identify betting opportunities.

## Features

- **Data Scraping**: Collects team statistics from ESPN and NBA.com (free sources)
- **ELO Rating System**: Calculates team strength ratings based on game results
- **Poisson Scoring Model**: Predicts game scores and outcomes using Poisson distribution
- **Value Bet Detector**: Compares model predictions to betting odds to find value bets
- **Combined Predictions**: Uses both ELO and Poisson models for more accurate predictions

## Installation

1. Clone or download this repository

2. Create a virtual environment (recommended):
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required dependencies:
```bash
pip install -r requirements.txt
```

**Note:** The virtual environment has already been created and dependencies installed. To activate it:
```bash
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

## Usage

### Basic Commands

**Update models with sample data and show rankings:**
```bash
python predict.py --update --rankings
```

**Predict a game:**
```bash
python predict.py --predict "Los Angeles Lakers" "Golden State Warriors"
```

**Analyze a game with betting odds:**
```bash
python predict.py --analyze "Los Angeles Lakers" "Golden State Warriors" -150 +130
```

The odds format is American odds:
- Negative numbers (e.g., -150) = favorites
- Positive numbers (e.g., +130) = underdogs

### Programmatic Usage

```python
from predict import NBAPredictionSystem
import pandas as pd

# Initialize system
system = NBAPredictionSystem()

# Update with historical game data
games_df = pd.DataFrame([
    {
        'home_team': 'Los Angeles Lakers',
        'away_team': 'Golden State Warriors',
        'home_score': 110,
        'away_score': 105
    },
    # ... more games
])

system.update_with_historical_data(games_df)

# Make a prediction
prediction = system.predict_game('Los Angeles Lakers', 'Golden State Warriors')
print(f"Lakers win probability: {prediction['home_win_probability']:.2%}")

# Analyze with betting odds
analysis = system.analyze_game_with_odds(
    'Los Angeles Lakers',
    'Golden State Warriors',
    home_odds=-150,  # Lakers favored
    away_odds=+130   # Warriors underdog
)

if analysis['home_value_bet']:
    print("Value bet detected on Lakers!")
```

## Components

### 1. Data Scraper (`data_scraper.py`)
- Scrapes team statistics from ESPN and NBA.com
- Handles different data formats and APIs
- Normalizes team names across sources

### 2. ELO Rating System (`elo_ratings.py`)
- Calculates team strength ratings using ELO algorithm
- Accounts for home court advantage
- Updates ratings based on game results
- Can save/load ratings for persistence

### 3. Poisson Scoring Model (`poisson_model.py`)
- Predicts game scores using Poisson distribution
- Calculates offensive and defensive ratings
- Combines with ELO for improved accuracy
- Provides win probabilities and score distributions

### 4. Value Bet Detector (`value_bet_detector.py`)
- Converts betting odds to implied probabilities
- Calculates expected value of bets
- Identifies value betting opportunities
- Uses Kelly Criterion for stake sizing

### 5. Main Prediction Script (`predict.py`)
- Combines all components
- Provides command-line interface
- Manages data persistence

## How It Works

1. **Data Collection**: The system scrapes team statistics and game results from free sources (ESPN, NBA.com)

2. **ELO Ratings**: Teams start with a default rating (1500). After each game:
   - Expected win probability is calculated based on rating difference
   - Ratings are updated based on actual outcome
   - Home teams get a +50 rating boost

3. **Poisson Model**: 
   - Calculates each team's average points scored (offensive rating)
   - Calculates each team's average points allowed (defensive rating)
   - Predicts expected scores using: `(team_offense / league_avg) * (opponent_defense / league_avg) * league_avg * home_factor`
   - Uses Poisson distribution to calculate win probabilities

4. **Combined Prediction**: 
   - ELO provides win probability based on team strength
   - Poisson provides win probability based on scoring
   - Combined using weighted average (60% Poisson, 40% ELO)

5. **Value Bet Detection**:
   - Converts betting odds to implied probabilities
   - Compares model probabilities to implied probabilities
   - Identifies bets where model probability > implied probability
   - Calculates expected value: `(model_prob * payout) - 1`

## Data Sources

The system uses free, publicly available data:
- **ESPN**: Team statistics and game results
- **NBA.com**: Official NBA statistics API

Note: Some data sources may require proper headers and may have rate limits. The scrapers include error handling and fallback methods.

## Configuration

You can adjust various parameters in the code:

- **ELO K-Factor**: Default 20 (in `elo_ratings.py`)
- **Home Advantage**: Default +50 rating points (in `elo_ratings.py`)
- **Value Bet Threshold**: Minimum 5% expected value (in `value_bet_detector.py`)
- **Model Weights**: Poisson 60%, ELO 40% (in `poisson_model.py`)

## Limitations

- Data scraping depends on website structure (may break if sites change)
- Models are trained on historical data - past performance doesn't guarantee future results
- Betting involves risk - use this system for informational purposes only
- The system uses sample data by default - you'll need to integrate real data sources

## Future Enhancements

- Real-time data integration
- Advanced features (player injuries, rest days, head-to-head records)
- Machine learning models
- Multiple sportsbook odds comparison
- Bet tracking and performance analysis

## Disclaimer

This system is for educational and informational purposes only. Sports betting involves risk, and past performance does not guarantee future results. Always gamble responsibly and within your means.

## License

This project is provided as-is for educational purposes.

