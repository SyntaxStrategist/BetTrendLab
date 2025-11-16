# BetTrendLab REST API Endpoints

All endpoints return clean JSON responses. The API is accessible at both root level and `/api/v1` prefix.

## Base URLs
- Root level: `http://localhost:8000/`
- Prefixed: `http://localhost:8000/api/v1/`

## Endpoints

### 1. GET /teams
Get all teams with their ELO ratings.

**Response:**
```json
{
  "teams": [
    {
      "team": "Los Angeles Lakers",
      "eloRating": 1521.34
    },
    ...
  ],
  "count": 10
}
```

**Example:**
```bash
curl http://localhost:8000/teams
```

---

### 2. GET /rankings
Get full ELO rankings table sorted by rating.

**Response:**
```json
{
  "rankings": [
    {
      "rank": 1,
      "team": "Los Angeles Lakers",
      "eloRating": 1521.34
    },
    ...
  ],
  "updatedAt": "2024-01-15T10:30:00"
}
```

**Example:**
```bash
curl http://localhost:8000/rankings
```

---

### 3. GET /predict
Predict a game between two teams.

**Query Parameters:**
- `team1` (required): First team name
- `team2` (required): Second team name
- `home_team` (optional): Home team name (defaults to team1)

**Response:**
```json
{
  "homeTeam": "Los Angeles Lakers",
  "awayTeam": "Golden State Warriors",
  "predictedScore": "113.3-106.7",
  "homeExpectedScore": 113.3,
  "awayExpectedScore": 106.7,
  "homeWinProbability": 0.6394,
  "awayWinProbability": 0.3606,
  "eloPrediction": {
    "homeWinProbability": 0.6250,
    "awayWinProbability": 0.3750
  },
  "poissonPrediction": {
    "homeWinProbability": 0.6480,
    "awayWinProbability": 0.3520
  },
  "expectedTotal": 220.0
}
```

**Example:**
```bash
curl "http://localhost:8000/predict?team1=Los%20Angeles%20Lakers&team2=Golden%20State%20Warriors"
```

---

### 4. GET /value-bet
Analyze value bets by comparing predictions to betting odds.

**Query Parameters:**
- `team1` (required): First team name
- `team2` (required): Second team name
- `odds1` (required): Odds for team1 (American format, e.g., -150 or +130)
- `odds2` (required): Odds for team2 (American format)
- `home_team` (optional): Home team name (defaults to team1)

**Response:**
```json
{
  "homeTeam": "Los Angeles Lakers",
  "awayTeam": "Golden State Warriors",
  "homeAnalysis": {
    "team": "Los Angeles Lakers",
    "betType": "home_win",
    "modelProbability": 0.6394,
    "impliedProbability": 0.6000,
    "odds": -150,
    "expectedValue": 0.0657,
    "edge": 0.0394,
    "isValueBet": true
  },
  "awayAnalysis": {
    "team": "Golden State Warriors",
    "betType": "away_win",
    "modelProbability": 0.3606,
    "impliedProbability": 0.4348,
    "odds": 130,
    "expectedValue": -0.1706,
    "edge": -0.0742,
    "isValueBet": false
  },
  "expectedScore": "113.3-106.7"
}
```

**Key Fields:**
- `edge`: The difference between model probability and implied probability (as decimal, e.g., 0.0394 = 3.94%)
- `expectedValue`: Expected value of the bet (as decimal, e.g., 0.0657 = 6.57%)
- `isValueBet`: Boolean indicating if this is a value bet (EV >= 5%)

**Example:**
```bash
curl "http://localhost:8000/value-bet?team1=Los%20Angeles%20Lakers&team2=Golden%20State%20Warriors&odds1=-150&odds2=130"
```

---

### 5. POST /update
Force update of stats and ELO ratings by scraping latest data.

**Response:**
```json
{
  "status": "success",
  "message": "Updated with 5 recent games",
  "games_processed": 5,
  "teams_updated": 10
}
```

**Possible status values:**
- `"success"`: Update completed successfully
- `"partial"`: No recent games found, ratings unchanged
- `"error"`: Error occurred during update

**Example:**
```bash
curl -X POST http://localhost:8000/update
```

---

## Response Format

All endpoints return clean JSON with:
- **Scores**: Predicted final score (e.g., "113.3-106.7")
- **Win Probabilities**: Decimal format (0.0 to 1.0)
- **Edge %**: Difference between model and implied probability (as decimal)
- **Expected Value**: Expected value of bet (as decimal, positive = value bet)
- **ELO Prediction**: Win probabilities from ELO model only
- **Poisson Prediction**: Win probabilities from Poisson model only

## Error Responses

All endpoints return standard HTTP status codes:
- `200`: Success
- `404`: Team not found
- `500`: Internal server error

Error response format:
```json
{
  "error": "Team not found",
  "detail": "Team 'Invalid Team' not found in ratings",
  "timestamp": "2024-01-15T10:30:00"
}
```

## CORS

CORS is enabled for all origins, allowing frontend access from any domain.

## API Documentation

Interactive API documentation available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

