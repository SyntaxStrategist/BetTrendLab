"""
Data scraper for NBA statistics from ESPN and NBA.com
Uses free, publicly available data sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime
import time
from typing import Dict, List, Optional


class ESPNScraper:
    """Scraper for ESPN NBA data"""
    
    BASE_URL = "https://www.espn.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_team_stats(self, season: Optional[str] = None) -> pd.DataFrame:
        """
        Get team statistics from ESPN
        Returns DataFrame with team stats
        """
        if season is None:
            season = datetime.now().year
        
        url = f"{self.BASE_URL}/nba/stats/team/_/season/{season}/seasontype/2"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Find the stats table
            tables = soup.find_all('table')
            if not tables:
                # Try alternative approach - ESPN uses React, so we might need API
                return self._get_team_stats_api(season)
            
            # Parse table if found
            df = pd.read_html(str(tables[0]))[0]
            return df
            
        except Exception as e:
            print(f"Error scraping ESPN team stats: {e}")
            return self._get_team_stats_api(season)
    
    def _get_team_stats_api(self, season: int) -> pd.DataFrame:
        """Fallback: Use ESPN API endpoint"""
        url = f"https://site.web.api.espn.com/apis/v2/sports/basketball/nba/statistics/team"
        params = {
            'region': 'us',
            'lang': 'en',
            'contentorigin': 'espn',
            'season': season,
            'seasontype': 2
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            # Parse ESPN API response
            teams = []
            if 'teams' in data:
                for team in data['teams']:
                    teams.append({
                        'Team': team.get('name', ''),
                        'GP': team.get('gamesPlayed', 0),
                        'W': team.get('wins', 0),
                        'L': team.get('losses', 0),
                        'PTS': team.get('pointsPerGame', 0),
                        'FGA': team.get('fieldGoalsAttempted', 0),
                        'FGM': team.get('fieldGoalsMade', 0),
                        '3PA': team.get('threePointersAttempted', 0),
                        '3PM': team.get('threePointersMade', 0),
                        'FTA': team.get('freeThrowsAttempted', 0),
                        'FTM': team.get('freeThrowsMade', 0),
                        'REB': team.get('reboundsPerGame', 0),
                        'AST': team.get('assistsPerGame', 0),
                        'TO': team.get('turnoversPerGame', 0),
                    })
            
            return pd.DataFrame(teams)
            
        except Exception as e:
            print(f"Error with ESPN API: {e}")
            return pd.DataFrame()
    
    def get_schedule(self, season: Optional[str] = None) -> pd.DataFrame:
        """Get NBA schedule from ESPN"""
        if season is None:
            season = datetime.now().year
        
        url = f"{self.BASE_URL}/nba/schedule"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # ESPN schedule parsing
            games = []
            # This is a simplified version - actual implementation would parse the schedule
            return pd.DataFrame(games)
            
        except Exception as e:
            print(f"Error scraping schedule: {e}")
            return pd.DataFrame()
    
    def get_game_results(self, days_back: int = 30) -> List[Dict]:
        """Get recent game results"""
        url = f"{self.BASE_URL}/nba/scoreboard"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            games = []
            # Parse game results from scoreboard
            # This would need to be implemented based on ESPN's current HTML structure
            
            return games
            
        except Exception as e:
            print(f"Error scraping game results: {e}")
            return []


class NBAScraper:
    """Scraper for NBA.com data"""
    
    BASE_URL = "https://stats.nba.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'Referer': 'https://www.nba.com/',
            'Accept': 'application/json'
        })
    
    def get_team_stats(self, season: Optional[str] = None) -> pd.DataFrame:
        """Get team statistics from NBA.com stats API"""
        if season is None:
            season = datetime.now().year
        
        # NBA.com uses a different season format (e.g., 2023-24)
        season_id = f"{season-1}-{str(season)[2:]}"
        
        url = f"{self.BASE_URL}/stats/teamdashboardbygeneralsplits"
        params = {
            'Season': season_id,
            'SeasonType': 'Regular Season',
            'MeasureType': 'Base',
            'PerMode': 'PerGame'
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                rows = data['resultSets'][0]['rowSet']
                headers = data['resultSets'][0]['headers']
                df = pd.DataFrame(rows, columns=headers)
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error with NBA.com API: {e}")
            return pd.DataFrame()
    
    def get_game_log(self, team_id: Optional[int] = None) -> pd.DataFrame:
        """Get game log for a team or all teams"""
        url = f"{self.BASE_URL}/stats/teamgamelog"
        
        params = {
            'Season': '2023-24',  # Update dynamically
            'SeasonType': 'Regular Season',
            'TeamID': team_id if team_id else 0
        }
        
        try:
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'resultSets' in data and len(data['resultSets']) > 0:
                rows = data['resultSets'][0]['rowSet']
                headers = data['resultSets'][0]['headers']
                df = pd.DataFrame(rows, columns=headers)
                return df
            
            return pd.DataFrame()
            
        except Exception as e:
            print(f"Error getting game log: {e}")
            return pd.DataFrame()


class DataManager:
    """Manages data collection and storage"""
    
    def __init__(self):
        self.espn = ESPNScraper()
        self.nba = NBAScraper()
        self.cache = {}
    
    def get_team_stats(self, source: str = 'nba') -> pd.DataFrame:
        """Get team stats from specified source"""
        if source == 'espn':
            return self.espn.get_team_stats()
        else:
            return self.nba.get_team_stats()
    
    def get_recent_games(self) -> List[Dict]:
        """Get recent game results"""
        return self.espn.get_game_results()
    
    def normalize_team_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize team names across different sources"""
        # Common team name mappings
        name_mapping = {
            'LA Lakers': 'Los Angeles Lakers',
            'LA Clippers': 'Los Angeles Clippers',
            'GSW': 'Golden State Warriors',
            'PHX': 'Phoenix Suns',
            'BOS': 'Boston Celtics',
            # Add more mappings as needed
        }
        
        if 'TEAM_NAME' in df.columns:
            df['TEAM_NAME'] = df['TEAM_NAME'].replace(name_mapping)
        elif 'Team' in df.columns:
            df['Team'] = df['Team'].replace(name_mapping)
        
        return df


if __name__ == "__main__":
    # Test the scrapers
    manager = DataManager()
    print("Fetching team stats from NBA.com...")
    stats = manager.get_team_stats('nba')
    print(f"Retrieved {len(stats)} teams")
    print(stats.head() if not stats.empty else "No data retrieved")

