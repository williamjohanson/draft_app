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

@app.route('/api/player-review', methods=['POST'])
def get_player_review():
    player_name = request.json.get('player_name')
    player_position = request.json.get('player_position')  # Assuming this is provided in the request
    team_roster = request.json.get('team_roster')  # Assuming the current roster is provided

    if not player_name or not player_position or not team_roster:
        return jsonify({'error': 'Player name, position, and team roster are required'}), 400

    try:
        # Initialize the generator and get parameters
        generator = CommentatorResponseGenerator()
        commentator, mood, structure = generator.generate_parameters()

        # Calculate player grade based on the team's needs
        grade_calculator = CalcPlayerGrade(player_name, player_position, team_roster)
        player_grade = grade_calculator.calculate_grade()
        grade_text = f"Grade: {player_grade:.2f}/10"

        # Call to OpenAI to generate a concise evaluation
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # More cost-effective model
            messages=[
                {"role": "system", "content": f"You are {commentator}, known for your {mood} analysis."},
                {"role": "user", "content": f"Using the following structure: '{structure}', evaluate the football player {player_name} who plays as a {player_position}. Provide a grade based on the team's needs, {grade_text}. Make sure the response is concise and non-humorous."}
            ],
            max_tokens=60
        )

        evaluation = response['choices'][0]['message']['content'].strip()

        # Combine the evaluation with the grade
        review = f"{evaluation}\n\n{grade_text}"
        return jsonify({'review': review})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    initialize()  # Ensure everything is set up before the server starts
    app.run(debug=True)
