import os
import json
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from models.database import db, League, Team
from models.grade import CalcPlayerGrade
from models.review import CommentatorResponseGenerator
import openai

app = Flask(__name__)
CORS(app)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fantasy_league.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

# Set your OpenAI API key
openai.api_key = os.getenv("OPENAI_API_KEY")

# Constants and paths
SLEEPER_API_BASE_URL = "https://api.sleeper.app/v1"
LEAGUE_ID = "1048178119665889280"
PLAYER_DATA_PATH = './data/players.json'

# Initialize the database and player data before the app starts
def initialize():
    with app.app_context():
        db.create_all()  # Create database tables if they don't exist
        if not os.path.exists(PLAYER_DATA_PATH):
            fetch_and_store_players()  # Load player data only if it's not already stored

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

def fetch_rookies():
    """Fetch rookies from the local JSON file."""
    try:
        with open(PLAYER_DATA_PATH, 'r') as file:
            players_data = json.load(file)
        
        rookies = []
        for player_id, player in players_data.items():
            if player.get('years_exp', 1) == 0 and player['position'] in ['QB', 'RB', 'WR', 'TE', 'K']:
                rookies.append(player)

        return rookies
    except Exception as e:
        return str(e)

def determine_next_pick(team_roster, available_rookies):
    """Generate a prompt and get the top 5 rookie picks using OpenAI."""
    roster_text = "\n".join([f"{p['first_name']} {p['last_name']} - {p['position']}" for p in team_roster])
    rookies_text = "\n".join([f"{r['first_name']} {r['last_name']} - {r['position']}" for r in available_rookies])

    prompt = (
        f"Based on the following team roster:\n{roster_text}\n\n"
        f"And considering it's a 2024 Dynasty league Rookie draft in a 2 QB League."
        f"Given your knowledge isolated to players selected in the 2024 NFL Draft, principally its key players, "
        f"suggest the top 5 rookie picks (and grade /10.0) for my situation from the following available rookies:\n{rookies_text}\n"
        f"Please provide the output in the following JSON format: and limit the entire response to the following:\n"
        f'[\n'
        f'  {{"name": "Rookie Name 1", "position": "Position", "grade": "Grade"}},\n'
        f'  {{"name": "Rookie Name 2", "position": "Position", "grade": "Grade"}},\n'
        f'  ...\n'
        f']'
    )

    print(prompt)

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": "You are an expert fantasy football analyst."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=200,
            n=1,
            stop=None,
            temperature=0.7,
        )
        print (response)

        # Extract the assistant's message content
        message_content = response['choices'][0]['message']['content'].strip()

        # Clean up the response to remove the code block markers
        if message_content.startswith("```json"):
            message_content = message_content[7:-3].strip()

        # Parse the JSON content from the message
        parsed_suggestions = json.loads(message_content)

        # Now you can work with the parsed_suggestions as a list of dictionaries
        for suggestion in parsed_suggestions:
            print(f"Rookie Name: {suggestion['name']}, Position: {suggestion['position']}, Grade: {suggestion['grade']}")

        # Return or further process the parsed_suggestions
        return parsed_suggestions

    except Exception as e:
        print(f"Error generating suggestions: {e}")
        return []

def fetch_all_rosters():
    try:
        response = requests.get(f"{SLEEPER_API_BASE_URL}/league/{LEAGUE_ID}/rosters")
        response.raise_for_status()  # Raise an error for bad status codes
        rosters = response.json()

        all_rosters = []
        for roster in rosters:
            # print(roster)
            # print("\n")
            team_roster = {
                'owner_id': roster['owner_id'],
                'players': roster['players']  # Assuming 'player_details' holds player info
            }
            all_rosters.append(team_roster)

        # print(all_rosters)
        return all_rosters

    except requests.exceptions.RequestException as e:
        print(f"Error fetching rosters: {e}")
        return []

@app.route('/api/next-pick', methods=['POST'])
def get_next_pick():
    try:
        data = request.json
        team_roster = data.get('team_roster', [])

        # Fetch all available rookies
        available_rookies = fetch_rookies()

        if not team_roster or not available_rookies:
            return jsonify({'error': 'Invalid team roster or no available rookies found'}), 400

        # Fetch all teams' rosters to check for rookies already drafted
        all_rosters = fetch_all_rosters()

        # Flatten the list of player IDs from all rosters
        drafted_player_ids = {player_id for roster in all_rosters for player_id in roster['players']}

        # Filter out rookies who are already on another team's roster by comparing player IDs
        available_rookies = [
            rookie for rookie in available_rookies
            if rookie['player_id'] not in drafted_player_ids
        ]

        # Determine the next pick
        suggestions = determine_next_pick(team_roster, available_rookies)

        return jsonify({'suggestions': suggestions})

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/api/rookies', methods=['GET'])
def get_rookies():
    try:
        rookies = fetch_rookies()
        return jsonify(rookies)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/league/<league_id>/drafts', methods=['GET'])
def get_league_drafts(league_id):
    try:
        url = f"{SLEEPER_API_BASE_URL}/league/{league_id}/drafts"
        response = requests.get(url)
        drafts = response.json()
        return jsonify(drafts)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/draft/<draft_id>/picks', methods=['GET'])
def get_draft_picks(draft_id):
    try:
        url = f"{SLEEPER_API_BASE_URL}/draft/{draft_id}/picks"
        response = requests.get(url)
        picks = response.json()
        return jsonify(picks)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

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

@app.route('/api/player-review', methods=['POST'])
def get_player_review():
    player_name = request.json.get('player_name')
    player_position = request.json.get('player_position')
    team_roster = request.json.get('team_roster')
    player_grade = request.json.get('player_grade')

    if not player_name or not player_position or not team_roster or not player_grade:
        return jsonify({'error': 'Player name, position, team roster, and grade are required'}), 400

    generator = CommentatorResponseGenerator()
    review = generator.generate_fantasy_review(player_name, player_position, player_grade, team_roster)

    return jsonify({'review': review, 'grade': f"Grade: {player_grade:.2f}/10"})

if __name__ == '__main__':
    initialize()  # Ensure everything is set up before the server starts
    app.run(port=5001, debug=True)
