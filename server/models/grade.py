import numpy as np
from sklearn.linear_model import LinearRegression
from pro_football_reference_web_scraper.player_game_log import get_player_game_log

class CalcPlayerGrade:
    def __init__(self, player_name, player_position, team_roster):
        self.player_name = player_name
        self.player_position = player_position
        self.team_roster = team_roster
        self.player_stats = None  # Will hold game log data

    def fetch_player_game_log(self, season):
        # Fetch game log data
        try:
            self.player_stats = get_player_game_log(self.player_name, self.player_position, season)
            print(f"Fetched game log for {self.player_name}:")
            print(self.player_stats.head())  # Display first few rows for debugging
        except Exception as e:
            print(f"Error fetching game log for {self.player_name}: {e}")

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
            # Example: Add average passing yards or other relevant stats to the feature vector
            if 'pass_yds' in self.player_stats.columns:
                avg_pass_yds = self.player_stats['pass_yds'].mean()
                X = np.append(X, avg_pass_yds).reshape(1, -1)

        # Linear regression model to calculate grade
        model = LinearRegression()
        model.fit(X, y)
        grade = model.predict(X)[0]

        # Ensure the grade is within 0-10 and round to 2 decimal places
        grade = np.clip(grade, 0, 10)
        return round(grade, 2)

