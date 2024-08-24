from flask import Flask, jsonify, request
from flask_cors import CORS
from models.database import db, League, Team
import requests
import os
import json
import openai
from models.grade import CalcPlayerGrade
from models.review import CommentatorResponseGenerator

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fantasy_league.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Set up OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Path to store player data locally
PLAYER_DATA_PATH = './data/players.json'
SLEEPER_API_BASE_URL = "https://api.sleeper.app/v1"
# Simple in-memory cache
review_cache = {}

SLEEPER_API_BASE_URL = "https://api.sleeper.app/v1"
LEAGUE_ID = league_id = "1048178119665889280"

def fetch_and_store_players():
    """Fetch player data from Sleeper API and store it locally."""
    url = f"{SLEEPER_API_BASE_URL}/players/nfl"
    response = requests.get(url)
    if response.status_code == 200:
        players_data = response.json()
        os.makedirs(os.path.dirname(PLAYER_DATA_PATH), exist_ok=True)  # Ensure directory exists
        with open(PLAYER_DATA_PATH, 'w') as file:
            json.dump(players_data, file)
        print("Player data saved locally.")
    else:
        print("Failed to fetch player data.")

def initialize():
    """Initialize the database and player data before the app starts."""
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
        if not os.path.exists(PLAYER_DATA_PATH):
            fetch_and_store_players()  # Load player data only if it's not already stored

@app.route('/api/league/<league_id>/users', methods=['GET'])
def get_league_users(league_id):
    users_url = f"{SLEEPER_API_BASE_URL}/league/{league_id}/users"
    response = requests.get(users_url)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({'error': 'Failed to fetch users'}), response.status_code

@app.route('/api/league/<league_id>/rosters', methods=['GET'])
def get_rosters(league_id):
    rosters_url = f"{SLEEPER_API_BASE_URL}/league/{league_id}/rosters"
    response = requests.get(rosters_url)
    if response.status_code == 200:
        rosters = response.json()
        with open(PLAYER_DATA_PATH, 'r') as file:
            players_data = json.load(file)
        
        # Attach player details to each roster
        for roster in rosters:
            roster['player_details'] = [players_data.get(player_id, {}) for player_id in roster['players']]
        
        return jsonify(rosters)
    return jsonify({'error': 'Failed to fetch rosters'}), response.status_code

@app.route('/api/league/<league_id>/transactions', methods=['GET'])
def get_transactions(league_id):
    transactions_url = f"{SLEEPER_API_BASE_URL}/league/{league_id}/transactions/1"
    response = requests.get(transactions_url)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({'error': 'Failed to fetch transactions'}), response.status_code

# Fetch all drafts for the league
@app.route('/api/league/<league_id>/drafts', methods=['GET'])
def get_league_drafts(league_id):
    try:
        url = f"https://api.sleeper.app/v1/league/{league_id}/drafts"
        response = requests.get(url)
        drafts = response.json()
        return jsonify(drafts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Fetch picks for a specific draft
@app.route('/api/draft/<draft_id>/picks', methods=['GET'])
def get_draft_picks(draft_id):
    try:
        url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
        response = requests.get(url)
        picks = response.json()
        return jsonify(picks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Fetch rookies
@app.route('/api/rookies', methods=['GET'])
def get_rookies():
    try:
        with open(PLAYER_DATA_PATH, 'r') as file:
            players_data = json.load(file)
        
        rookies = []
        for player_id, player_info in players_data.items():
            if player_info.get('years_exp', 1) == 0:  # Identify rookies
                rookie = {
                    "player_id": player_id,
                    "name": f"{player_info['first_name']} {player_info['last_name']}",
                    "position": player_info['position'],
                    "team": player_info.get('team', 'N/A'),
                    "grade": 8.5  # Placeholder for actual grade calculation
                }
                rookies.append(rookie)

        rookies = sorted(rookies, key=lambda x: x['grade'], reverse=True)
        return jsonify(rookies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(port=5001, debug=True)

@app.route('/api/draft/<draft_id>', methods=['GET'])
def get_draft_details(draft_id):
    try:
        response = requests.get(f"{SLEEPER_API_BASE_URL}/draft/{draft_id}")
        response.raise_for_status()
        draft_details = response.json()
        return jsonify(draft_details)
    except Exception as e:
        print(f"Error fetching draft details for draft {draft_id}: {e}")
        return jsonify({'error': 'Failed to fetch draft details'}), 500

@app.route('/api/draft/<draft_id>/traded_picks', methods=['GET'])
def get_traded_picks(draft_id):
    try:
        response = requests.get(f"{SLEEPER_API_BASE_URL}/draft/{draft_id}/traded_picks")
        response.raise_for_status()
        traded_picks = response.json()
        return jsonify(traded_picks)
    except Exception as e:
        print(f"Error fetching traded picks for draft {draft_id}: {e}")
        return jsonify({'error': 'Failed to fetch traded picks'}), 500

@app.route('/api/player-grades', methods=['POST'])
def get_player_grades():
    data = request.json
    team_roster = data.get('team_roster')

    if not team_roster:
        return jsonify({'error': 'Team roster is required'}), 400

    current_year = 2024  # Update to the current year
    player_grades = []

    for player in team_roster:
        player_name = player.get('first_name') + ' ' + player.get('last_name')
        player_position = player.get('position')
        years_exp = player.get('years_exp')

        if not player_name or not player_position or years_exp is None:
            continue

        # Calculate rookie season
        rookie_season = current_year - years_exp

        # Initialize grade calculator
        grade_calculator = CalcPlayerGrade(player_name, player_position, team_roster)

        # Handle players who are rookies this year
        if years_exp == 0:
            print(f"{player_name} is a rookie this year. No historical data available.")
            player_grade = grade_calculator.calculate_grade()  # Calculate based on team needs without player stats
        else:
            grade_calculator.fetch_player_game_log(rookie_season, current_year - 1)  # Fetch from rookie season to last year
            player_grade = grade_calculator.calculate_grade()

        player_grades.append({
            'player_id': player.get('player_id'),
            'grade': player_grade
        })

    return jsonify({'grades': player_grades})

@app.route('/api/player-review', methods=['POST'])
def get_player_review():
    player_name = request.json.get('player_name')
    player_position = request.json.get('player_position')
    team_roster = request.json.get('team_roster')
    player_grade = request.json.get('player_grade')  # Assuming grade is passed to this endpoint

    if not player_name or not player_position or not team_roster or not player_grade:
        return jsonify({'error': 'Player name, position, team roster, and grade are required'}), 400

    generator = CommentatorResponseGenerator()
    review = generator.generate_fantasy_review(player_name, player_position, player_grade, team_roster)

    return jsonify({'review': review, 'grade': f"Grade: {player_grade:.2f}/10"})

if __name__ == '__main__':
    initialize()  # Ensure everything is set up before the server starts
    app.run(port=5001, debug=True)
