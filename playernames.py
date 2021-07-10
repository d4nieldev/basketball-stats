import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
import json

def get_player_info(player_row):
    link_to_player = player_row.find("th")['data-append-csv']
    player_name = player_row.find("th").find("a").get_text()
    player_from = player_row.findAll('td')[0].get_text()
    player_to = player_row.findAll('td')[1].get_text()

    print(player_name)

    # get exact years
    url = f'https://www.basketball-reference.com/players/{link_to_player[0]}/{link_to_player}.html'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    player_rows = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')
    years = set()

    for row in player_rows:
        if row.find('th') and row.find('th').find('a'):
            years.add(row.find('th').find('a').get_text())

    return {
        'link': link_to_player,
        'name': player_name,
        'from': player_from,
        'to': player_to,
        'years': sorted(years)
    }

def get_players():
    players = []
    for c in ascii_lowercase:
        url = f'https://www.basketball-reference.com/players/{c}/'
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')

        player_rows = soup.find("table", {'id': 'players'}).find("tbody").findAll('tr')

        for player_row in player_rows:
                players.append(get_player_info(player_row))
    
    return players

def write_to_json(something):
    with open('players.json', 'w') as f:
        json.dump(something, f, indent=4, sort_keys=True)

write_to_json(something=get_players())
    
    

