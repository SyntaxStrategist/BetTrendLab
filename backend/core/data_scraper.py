"""
Data manager for NBA statistics using balldontlie.io API
Free API for NBA data - no authentication required
"""

import requests
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class BallDontLieAPI:
    """Client for balldontlie.io API"""
    
    BASE_URL = "https://www.balldontlie.io/api/v1"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'Accept': 'application/json',
            'User-Agent': 'BetTrendLab/1.0'
        })
    
    def _make_request(self, endpoint: str, params: Optional[Dict] = None) -> Optional[Dict]:
        """Make API request with error handling"""
        url = f"{self.BASE_URL}/{endpoint}"
        try:
            response = self.session.get(url, params=params, timeout=10)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            logger.error(f"Error making API request to {url}: {e}")
            return None
    
    def get_all_teams(self) -> List[Dict]:
        """Get all NBA teams"""
        data = self._make_request("teams")
        if data and 'data' in data:
            teams = []
            for team in data['data']:
                teams.append({
                    'id': team.get('id'),
                    'abbreviation': team.get('abbreviation'),
                    'city': team.get('city'),
                    'conference': team.get('conference'),
                    'division': team.get('division'),
                    'full_name': team.get('full_name'),
                    'name': team.get('name')
                })
            return teams
        return []
    
    def get_teams_by_ids(self, team_ids: List[int]) -> List[Dict]:
        """Get teams by their IDs"""
        teams = []
        for team_id in team_ids:
            data = self._make_request(f"teams/{team_id}")
            if data:
                teams.append(data)
        return teams
    
    def get_games(self, 
                  dates: Optional[List[str]] = None,
                  seasons: Optional[List[int]] = None,
                  team_ids: Optional[List[int]] = None,
                  per_page: int = 100) -> List[Dict]:
        """
        Get games with optional filters
        
        Args:
            dates: List of dates in YYYY-MM-DD format
            seasons: List of season years (e.g., [2023] for 2023-24 season)
            team_ids: List of team IDs to filter by
            per_page: Number of results per page (max 100)
        """
        params = {'per_page': min(per_page, 100)}
        
        if dates:
            params['dates[]'] = dates
        if seasons:
            params['seasons[]'] = seasons
        if team_ids:
            params['team_ids[]'] = team_ids
        
        all_games = []
        page = 1
        
        while True:
            params['page'] = page
            data = self._make_request("games", params=params)
            
            if not data or 'data' not in data:
                break
            
            games = data.get('data', [])
            if not games:
                break
            
            all_games.extend(games)
            
            # Check if there are more pages
            meta = data.get('meta', {})
            if page >= meta.get('total_pages', 1):
                break
            
            page += 1
        
        return all_games
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's scheduled games"""
        today = datetime.now().strftime('%Y-%m-%d')
        games = self.get_games(dates=[today])
        
        # Format games for our application
        formatted_games = []
        for game in games:
            home_team = game.get('home_team', {})
            visitor_team = game.get('visitor_team', {})
            
            formatted_games.append({
                'id': game.get('id'),
                'date': game.get('date', today),
                'home_team': home_team.get('full_name', ''),
                'home_team_id': home_team.get('id'),
                'away_team': visitor_team.get('full_name', ''),
                'away_team_id': visitor_team.get('id'),
                'home_score': game.get('home_team_score'),
                'visitor_score': game.get('visitor_team_score'),
                'status': game.get('status'),
                'time': game.get('time', ''),
                'season': game.get('season'),
                'period': game.get('period'),
                'postseason': game.get('postseason', False)
            })
        
        return formatted_games
    
    def get_recent_games(self, days: int = 7) -> List[Dict]:
        """Get recent completed games"""
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        dates = []
        current_date = start_date
        while current_date <= end_date:
            dates.append(current_date.strftime('%Y-%m-%d'))
            current_date += timedelta(days=1)
        
        games = self.get_games(dates=dates)
        
        # Filter for completed games and format
        formatted_games = []
        for game in games:
            # Only include completed games (status is 'Final' or has scores)
            status = game.get('status', '')
            home_score = game.get('home_team_score')
            visitor_score = game.get('visitor_team_score')
            
            if status == 'Final' or (home_score is not None and visitor_score is not None):
                home_team = game.get('home_team', {})
                visitor_team = game.get('visitor_team', {})
                
                formatted_games.append({
                    'id': game.get('id'),
                    'date': game.get('date'),
                    'home_team': home_team.get('full_name', ''),
                    'home_team_id': home_team.get('id'),
                    'away_team': visitor_team.get('full_name', ''),
                    'away_team_id': visitor_team.get('id'),
                    'home_score': int(home_score) if home_score is not None else 0,
                    'away_score': int(visitor_score) if visitor_score is not None else 0,
                    'status': status,
                    'season': game.get('season')
                })
        
        return formatted_games
    
    def get_season_stats(self, season: int, team_id: Optional[int] = None) -> pd.DataFrame:
        """
        Get season statistics for teams
        
        Args:
            season: Season year (e.g., 2023 for 2023-24 season)
            team_id: Optional team ID to filter by
        """
        params = {'seasons[]': [season], 'per_page': 100}
        if team_id:
            params['team_ids[]'] = [team_id]
        
        all_stats = []
        page = 1
        
        while True:
            params['page'] = page
            data = self._make_request("stats", params=params)
            
            if not data or 'data' not in data:
                break
            
            stats = data.get('data', [])
            if not stats:
                break
            
            all_stats.extend(stats)
            
            meta = data.get('meta', {})
            if page >= meta.get('total_pages', 1):
                break
            
            page += 1
        
        if not all_stats:
            return pd.DataFrame()
        
        # Convert to DataFrame and aggregate by team
        df = pd.DataFrame(all_stats)
        
        # Group by team and calculate averages
        if 'team' in df.columns:
            # Extract team name from nested dict
            df['team_name'] = df['team'].apply(lambda x: x.get('full_name', '') if isinstance(x, dict) else '')
        
        return df
    
    def get_team_averages(self, season: int) -> Dict[str, Dict]:
        """Get team averages for a season"""
        stats_df = self.get_season_stats(season)
        
        if stats_df.empty:
            return {}
        
        # Group by team and calculate averages
        team_stats = {}
        
        for _, row in stats_df.iterrows():
            team_info = row.get('team', {})
            if isinstance(team_info, dict):
                team_name = team_info.get('full_name', '')
            else:
                team_name = str(team_info)
            
            if team_name not in team_stats:
                team_stats[team_name] = {
                    'games': 0,
                    'points': 0,
                    'rebounds': 0,
                    'assists': 0,
                    'field_goal_percentage': 0,
                    'three_point_percentage': 0
                }
            
            team_stats[team_name]['games'] += 1
            team_stats[team_name]['points'] += row.get('pts', 0) or 0
            team_stats[team_name]['rebounds'] += row.get('reb', 0) or 0
            team_stats[team_name]['assists'] += row.get('ast', 0) or 0
        
        # Calculate averages
        for team_name, stats in team_stats.items():
            games = stats['games']
            if games > 0:
                stats['points_per_game'] = stats['points'] / games
                stats['rebounds_per_game'] = stats['rebounds'] / games
                stats['assists_per_game'] = stats['assists'] / games
        
        return team_stats


class DataManager:
    """Manages data collection using balldontlie.io API"""
    
    def __init__(self):
        self.api = BallDontLieAPI()
        self.cache = {}
        self.current_season = datetime.now().year
        # NBA season typically starts in October, so adjust if needed
        if datetime.now().month < 10:
            self.current_season -= 1
    
    def get_all_teams(self) -> List[Dict]:
        """Get all NBA teams"""
        cache_key = 'all_teams'
        if cache_key not in self.cache:
            teams = self.api.get_all_teams()
            self.cache[cache_key] = teams
            logger.info(f"Fetched {len(teams)} teams from balldontlie API")
        return self.cache[cache_key]
    
    def get_todays_games(self) -> List[Dict]:
        """Get today's games from balldontlie API"""
        today = datetime.now().strftime('%Y-%m-%d')
        cache_key = f'todays_games_{today}'
        
        if cache_key not in self.cache:
            games = self.api.get_todays_games()
            self.cache[cache_key] = games
            logger.info(f"Fetched {len(games)} games for {today} from balldontlie API")
        
        return self.cache[cache_key]
    
    def get_recent_results(self, days: int = 7) -> List[Dict]:
        """Get recent game results for ELO updates"""
        cache_key = f'recent_games_{days}'
        
        if cache_key not in self.cache:
            games = self.api.get_recent_games(days=days)
            self.cache[cache_key] = games
            logger.info(f"Fetched {len(games)} recent games (last {days} days) from balldontlie API")
        
        return self.cache[cache_key]
    
    def get_season_stats(self, season: Optional[int] = None) -> pd.DataFrame:
        """Get season statistics"""
        if season is None:
            season = self.current_season
        
        cache_key = f'season_stats_{season}'
        if cache_key not in self.cache:
            stats_df = self.api.get_season_stats(season)
            self.cache[cache_key] = stats_df
            logger.info(f"Fetched season stats for {season} from balldontlie API")
        
        return self.cache[cache_key]
    
    def get_team_averages(self, season: Optional[int] = None) -> Dict[str, Dict]:
        """Get team averages for a season"""
        if season is None:
            season = self.current_season
        
        cache_key = f'team_averages_{season}'
        if cache_key not in self.cache:
            averages = self.api.get_team_averages(season)
            self.cache[cache_key] = averages
            logger.info(f"Fetched team averages for {season} from balldontlie API")
        
        return self.cache[cache_key]
    
    def normalize_team_names(self, df: pd.DataFrame) -> pd.DataFrame:
        """Normalize team names - balldontlie uses full names, so minimal mapping needed"""
        name_mapping = {
            'LA Lakers': 'Los Angeles Lakers',
            'LA Clippers': 'Los Angeles Clippers',
        }
        
        if 'TEAM_NAME' in df.columns:
            df['TEAM_NAME'] = df['TEAM_NAME'].replace(name_mapping)
        elif 'Team' in df.columns:
            df['Team'] = df['Team'].replace(name_mapping)
        elif 'team_name' in df.columns:
            df['team_name'] = df['team_name'].replace(name_mapping)
        
        return df
    
    def clear_cache(self):
        """Clear the cache"""
        self.cache.clear()
        logger.info("DataManager cache cleared")
