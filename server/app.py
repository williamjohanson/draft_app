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
# Simple in-memory cache
review_cache = {}

def fetch_and_store_players():
    """Fetch player data from Sleeper API and store it locally."""
    url = "https://api.sleeper.app/v1/players/nfl"
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
    users_url = f"https://api.sleeper.app/v1/league/{league_id}/users"
    response = requests.get(users_url)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({'error': 'Failed to fetch users'}), response.status_code

@app.route('/api/league/<league_id>/rosters', methods=['GET'])
def get_rosters(league_id):
    rosters_url = f"https://api.sleeper.app/v1/league/{league_id}/rosters"
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
    transactions_url = f"https://api.sleeper.app/v1/league/{league_id}/transactions/1"
    response = requests.get(transactions_url)
    if response.status_code == 200:
        return jsonify(response.json())
    return jsonify({'error': 'Failed to fetch transactions'}), response.status_code

@app.route('/api/league/<league_id>/draft_picks', methods=['GET'])
def get_draft_picks(league_id):    
    league_url = f"https://api.sleeper.app/v1/league/{league_id}"
    league_response = requests.get(league_url)
    if league_response.status_code == 200:
        draft_id = league_response.json().get('draft_id')
        if not draft_id:
            return jsonify({'error': 'No draft ID found for this league'}), 404

        draft_picks_url = f"https://api.sleeper.app/v1/draft/{draft_id}/picks"
        response = requests.get(draft_picks_url)
        if response.status_code == 200:
            return jsonify(response.json())
        return jsonify({'error': 'Failed to fetch draft picks'}), response.status_code
    return jsonify({'error': 'Failed to fetch league data'}), league_response.status_code

@app.route('/api/player-grade', methods=['POST'])
def get_player_grade():
    data = request.json
    player_name = data.get('player_name')
    player_position = data.get('player_position')
    team_roster = data.get('team_roster')
    season = data.get('season', 2023)  # Default to current season

    if not player_name or not player_position or not team_roster:
        return jsonify({'error': 'Player name, position, and team roster are required'}), 400

    # Initialize and calculate grade
    grade_calculator = CalcPlayerGrade(player_name, player_position, team_roster)
    grade_calculator.fetch_player_game_log(season)
    player_grade = grade_calculator.calculate_grade()

    return jsonify({'grade': player_grade})

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
