import numpy as np
from sklearn.linear_model import LinearRegression
import pandas as pd
import time
import os
import json
from pro_football_reference_web_scraper.player_game_log import get_player_game_log

class CalcPlayerGrade:
    def __init__(self, player_name, player_position, team_roster):
        self.player_name = player_name
        self.player_position = player_position
        self.team_roster = team_roster
        self.player_stats = None  # Will hold game log data
        self.cache_dir = "player_cache"  # Directory to store cached data

        # Create the cache directory if it doesn't exist
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, season):
        """Get the cache file path for a given player and season."""
        filename = f"{self.player_name.replace(' ', '_')}_{season}.json"
        return os.path.join(self.cache_dir, filename)

    def _load_from_cache(self, season):
        """Load player data from the cache if available."""
        cache_path = self._get_cache_path(season)
        if os.path.exists(cache_path):
            with open(cache_path, 'r') as file:
                data = pd.read_json(file.read(), orient='split')
                print(f"Loaded cached data for {self.player_name} for season {season}.")
                return data
        return None


    def _save_to_cache(self, data, season):
        """Save player data to the cache."""
        cache_path = self._get_cache_path(season)
        with open(cache_path, 'w') as file:
            data.to_json(file, orient='split')
            print(f"Saved data for {self.player_name} for season {season} to cache.")

    def fetch_player_game_log(self, rookie_season, end_season):
        # Handle case where the player is a rookie this year
        if rookie_season == end_season + 1:
            print(f"{self.player_name} is a rookie this year. No historical data available.")
            self.player_stats = None
            return

        all_stats = []
        for season in range(rookie_season, end_season + 1):
            # Try to load from cache first
            cached_data = self._load_from_cache(season)
            if cached_data is not None:
                all_stats.append(cached_data)
            else:
                try:
                    season_stats = get_player_game_log(self.player_name, self.player_position, season)
                    all_stats.append(season_stats)
                    print(f"Fetched game log for {self.player_name} for season {season}:")
                    print(season_stats.head())  # Display first few rows for debugging

                    # Save the fetched data to cache
                    self._save_to_cache(season_stats, season)

                    # Respect rate limits by sleeping for 2 seconds
                    time.sleep(5)
                except Exception as e:
                    print(f"Error fetching game log for {self.player_name} in season {season}: {e}")

        if all_stats:
            self.player_stats = pd.concat(all_stats)
        else:
            self.player_stats = None

    def calculate_grade(self):
        # Sample weights for positions; these could be tuned
        position_weights = {
            'QB': 0.2,
            'RB': 0.3,
            'WR': 0.3,
            'TE': 0.1,
            'K': 0.05,
            'DEF': 0.05
        }

        # Count the current players in each position
        position_counts = {pos: 0 for pos in position_weights.keys()}
        for player in self.team_roster:
            position_counts[player['position']] += 1

        # Convert position needs into a feature vector
        X = np.array([position_counts[pos] for pos in position_weights.keys()]).reshape(1, -1)
        
        # The importance of having fewer players at a position
        y = np.array([10 - position_counts[self.player_position]])  # Simplified need-based score

        # Incorporate player stats into the regression if available
        if self.player_stats is not None:
            print(self.player_stats.columns)
            
            # Summarize stats over all seasons
            total_stats = {
                'pass_yds': self.player_stats['pass_yds'].sum() if 'pass_yds' in self.player_stats.columns else 0,
                'pass_td': self.player_stats['pass_td'].sum() if 'pass_td' in self.player_stats.columns else 0,
                'rush_yds': self.player_stats['rush_yds'].sum() if 'rush_yds' in self.player_stats.columns else 0,
                'rush_td': self.player_stats['rush_td'].sum() if 'rush_td' in self.player_stats.columns else 0,
                'rec_yds': self.player_stats['rec_yds'].sum() if 'rec_yds' in self.player_stats.columns else 0,
                'rec_td': self.player_stats['rec_td'].sum() if 'rec_td' in self.player_stats.columns else 0,
                # 'snap_pct': self.player_stats['snap_pct'].mean() if 'snap_pct' in self.player_stats.columns else 0,
                'games_played': len(self.player_stats)
            }

            X = np.append(X, [total_stats['pass_yds'], total_stats['pass_td'], total_stats['rush_yds'], 
                              total_stats['rush_td'], total_stats['rec_yds'], total_stats['rec_td'], 
                            #   total_stats['snap_pct'],
                              total_stats['games_played']])

        X = X.reshape(1, -1)

        # Linear regression model to calculate grade
        model = LinearRegression()
        model.fit(X, y)
        grade = model.predict(X)[0]

        # Ensure the grade is within 0-10 and round to 2 decimal places
        grade = np.clip(grade, 0, 10)
        return round(grade, 2)

# Example usage:
# grade_calculator = CalcPlayerGrade("Josh Allen", "QB", team_roster)
# grade_calculator.fetch_player_game_log(2018, 2023)  # Fetch data from 2018 to 2023
# player_grade = grade_calculator.calculate_grade()
# print(f"Player Grade: {player_grade}")
