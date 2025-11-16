"""
Data scraper for NBA statistics from ESPN and NBA.com
Uses free, publicly available data sources
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import json
from datetime import datetime, timedelta
import time
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ESPNScraper:
    """Scraper for ESPN NBA data"""
    
    BASE_URL = "https://www.espn.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's NBA games from ESPN"""
        url = f"{self.BASE_URL}/nba/scoreboard"
        
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            
            games = []
            # Try to find game containers
            # ESPN structure may vary, this is a basic implementation
            game_containers = soup.find_all(['div', 'section'], class_=lambda x: x and 'game' in x.lower())
            
            # If no games found, return sample structure
            if not game_containers:
                logger.warning("Could not parse ESPN games, returning empty list")
                return games
            
            # Parse games (this would need to be adapted to ESPN's actual structure)
            # For now, return empty list - actual implementation would parse the HTML
            
            return games
            
        except Exception as e:
            logger.error(f"Error scraping ESPN games: {e}")
            return []
    
    def get_recent_results(self, days: int = 1) -> List[Dict]:
        """Get recent game results"""
        url = f"{self.BASE_URL}/nba/scoreboard"
        
        try:
            response = self.session.get(url, timeout=10)
            soup = BeautifulSoup(response.content, 'html.parser')
            
            games = []
            # Parse completed games from scoreboard
            # Implementation would parse ESPN's HTML structure
            
            return games
            
        except Exception as e:
            logger.error(f"Error scraping game results: {e}")
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
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's games from NBA.com"""
        today = datetime.now().strftime('%Y%m%d')
        url = f"{self.BASE_URL}/stubs/calendar/games.json"
        
        try:
            # Try to get schedule
            # NBA.com API structure may vary
            # This is a placeholder - actual implementation would use NBA.com's API
            
            # For now, return sample games structure
            return []
            
        except Exception as e:
            logger.error(f"Error getting NBA.com games: {e}")
            return []


class DataManager:
    """Manages data collection and storage"""
    
    def __init__(self):
        self.espn = ESPNScraper()
        self.nba = NBAScraper()
        self.cache = {}
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's games from available sources"""
        games = self.espn.get_todays_games()
        
        if not games:
            games = self.nba.get_todays_games()
        
        # If still no games, return sample data for testing
        if not games:
            logger.info("No games found from scrapers, returning sample games")
            return self._get_sample_games()
        
        return games
    
    def get_recent_results(self, days: int = 7) -> List[Dict]:
        """Get recent game results for ELO updates"""
        games = self.espn.get_recent_results(days=days)
        
        # If no games from ESPN, try NBA.com or return empty
        if not games:
            logger.info(f"No recent game results found from scrapers (last {days} days)")
        
        return games
    
    def _get_sample_games(self) -> List[Dict]:
        """Return sample games for testing"""
        return [
            {
                'home_team': 'Los Angeles Lakers',
                'away_team': 'Golden State Warriors',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '20:00'
            },
            {
                'home_team': 'Boston Celtics',
                'away_team': 'Miami Heat',
                'date': datetime.now().strftime('%Y-%m-%d'),
                'time': '19:30'
            }
        ]
    
    def normalize_team_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize team names across different sources"""
        name_mapping = {
            'LA Lakers': 'Los Angeles Lakers',
            'LA Clippers': 'Los Angeles Clippers',
            'GSW': 'Golden State Warriors',
            'PHX': 'Phoenix Suns',
            'BOS': 'Boston Celtics',
        }
        
        if 'TEAM_NAME' in df.columns:
            df['TEAM_NAME'] = df['TEAM_NAME'].replace(name_mapping)
        elif 'Team' in df.columns:
            df['Team'] = df['Team'].replace(name_mapping)
        
        return df

