import requests
from bs4 import BeautifulSoup
import pandas as pd

# Simplified version for better clarity
valid_positions = ['QB', 'RB', 'WR', 'TE']

def get_player_game_log(player: str, position: str, season: int) -> pd.DataFrame:
    if position not in valid_positions:
        print(f"Invalid position: {position}. Must be one of {valid_positions}")
        return None

    try:
        # Step 1: Construct the URL and make the request
        href = find_player_href(player, position, season)
        if not href:
            print(f"No href found for player {player} in season {season}")
            return None
        
        game_log_url = f'https://www.pro-football-reference.com{href}/gamelog/{season}/'
        print(f"Requesting game log from: {game_log_url}")
        
        response = requests.get(game_log_url)
        if response.status_code != 200:
            print(f"Failed to retrieve game log for {player} (status code: {response.status_code})")
            return None

        # Step 2: Parse the HTML
        soup = BeautifulSoup(response.text, 'html.parser')
        if not soup:
            print(f"No content found at {game_log_url}")
            return None

        # Step 3: Extract data based on position
        if position == 'QB':
            return qb_game_log(soup)
        # elif position in ['WR', 'TE']:
        #     return wr_game_log(soup)
        # elif position == 'RB':
        #     return rb_game_log(soup)
        # else:
        #     print(f"Unsupported position: {position}")
        #     return None
    except Exception as e:
        print(f"Error fetching game log for {player} in season {season}: {e}")
        return None

def find_player_href(player: str, position: str, season: int) -> str:
    try:
        last_initial = player.split(' ')[1][0]
        player_list_url = f'https://www.pro-football-reference.com/players/{last_initial}/'
        print(f"Requesting player list from: {player_list_url}")
        
        response = requests.get(player_list_url)
        if response.status_code != 200:
            print(f"Failed to retrieve player list for {player} (status code: {response.status_code})")
            return None

        soup = BeautifulSoup(response.text, 'html.parser')
        players = soup.find('div', id='div_players').find_all('p')

        for p in players:
            seasons = p.text.split(' ')[-1].split('-')
            if int(seasons[0]) <= season <= int(seasons[1]) and player in p.text and position in p.text:
                href = p.find('a').get('href')
                print(f"Found href for {player}: {href}")
                return href.replace('.htm', '')
        
        print(f"No matching href found for {player}")
        return None
    except Exception as e:
        print(f"Error finding href for {player}: {e}")
        return None

def qb_game_log(soup: BeautifulSoup) -> pd.DataFrame:
    data = {
        'date': [],
        'week': [],
        'team': [],
        'game_location': [],
        'opp': [],
        'result': [],
        'team_pts': [],
        'opp_pts': [],
        'cmp': [],
        'att': [],
        'pass_yds': [],
        'pass_td': [],
        'int': [],
        'rating': [],
        'sacked': [],
        'rush_att': [],
        'rush_yds': [],
        'rush_td': [],
    }

    table_rows = soup.find('tbody').find_all('tr')
    if not table_rows:
        print("No data found in game log")
        return pd.DataFrame(data)

    for row in table_rows:
        if row.find('td', {'data-stat': 'pass_cmp'}):
            data['date'].append(row.find('td', {'data-stat': 'game_date'}).text)
            data['week'].append(int(row.find('td', {'data-stat': 'week_num'}).text))
            data['team'].append(row.find('td', {'data-stat': 'team'}).text)
            data['game_location'].append(row.find('td', {'data-stat': 'game_location'}).text)
            data['opp'].append(row.find('td', {'data-stat': 'opp'}).text)
            data['result'].append(row.find('td', {'data-stat': 'game_result'}).text.split(' ')[0])
            data['team_pts'].append(int(row.find('td', {'data-stat': 'game_result'}).text.split(' ')[1].split('-')[0]))
            data['opp_pts'].append(int(row.find('td', {'data-stat': 'game_result'}).text.split(' ')[1].split('-')[1]))
            data['cmp'].append(int(row.find('td', {'data-stat': 'pass_cmp'}).text))
            data['att'].append(int(row.find('td', {'data-stat': 'pass_att'}).text))
            data['pass_yds'].append(int(row.find('td', {'data-stat': 'pass_yds'}).text))
            data['pass_td'].append(int(row.find('td', {'data-stat': 'pass_td'}).text))
            data['int'].append(int(row.find('td', {'data-stat': 'pass_int'}).text))
            data['rating'].append(float(row.find('td', {'data-stat': 'pass_rating'}).text))
            data['sacked'].append(int(row.find('td', {'data-stat': 'pass_sacked'}).text))
            data['rush_att'].append(int(row.find('td', {'data-stat': 'rush_att'}).text))
            data['rush_yds'].append(int(row.find('td', {'data-stat': 'rush_yds'}).text))
            data['rush_td'].append(int(row.find('td', {'data-stat': 'rush_td'}).text))

    return pd.DataFrame(data)

# Implement wr_game_log and rb_game_log similarly with proper error handling

def main():

    print(get_player_game_log('Josh Allen', 'QB', 2023))

main()