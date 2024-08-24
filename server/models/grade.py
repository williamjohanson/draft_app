import numpy as np
from sklearn.linear_model import LinearRegression

class CalcPlayerGrade:
    def __init__(self, player_name, player_position, team_roster):
        self.player_name = player_name
        self.player_position = player_position
        self.team_roster = team_roster

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
            position_counts[player['player_position']] += 1

        # Convert position needs into a feature vector
        X = np.array([position_counts[pos] for pos in position_weights.keys()]).reshape(1, -1)
        
        # The importance of having fewer players at a position
        y = np.array([10 - position_counts[self.player_position]])  # Simplified need-based score

        # Linear regression model to calculate grade
        model = LinearRegression()
        model.fit(X, y)
        grade = model.predict(X)[0]

        # Ensure the grade is within 0-10 and round to 2 decimal places
        grade = np.clip(grade, 0, 10)
        return round(grade, 2)
