import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
import json
from utils import calc_rating, get_player_year_stats
import sys
from tqdm import tqdm

def get_best_year(link, years):
    url = "https://www.basketball-reference.com/players/" + link[0] + "/" + link + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')
    
    player_years = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')

    rating = 0
    best_year = years[0]
    index = 0

    for year in years:
        if int(year.split('-')[0]) >= 1977:
            temp = calc_rating(get_player_year_stats(player_years, year))
            if temp > rating:
                rating = temp
                best_year = years[index]
        index += 1
    
    return best_year


def get_player_info(player_row):
    link_to_player = player_row.find("th")['data-append-csv']
    player_name = player_row.find("th").find("a").get_text()
    player_from = player_row.findAll('td')[0].get_text()
    player_to = player_row.findAll('td')[1].get_text()

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
        'years': sorted(years),
        'best_year': get_best_year(link_to_player, sorted(years))
    }

def get_players():
    players = []

    for c in tqdm(ascii_lowercase, desc="Total"):
        url = f'https://www.basketball-reference.com/players/{c}/'
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')

        player_rows = soup.find("table", {'id': 'players'}).find("tbody").findAll('tr')
        
        for player_row in tqdm(player_rows, desc=f"Letter {c}", leave=False):
                players.append(get_player_info(player_row))
    
    return players

def write_to_json(something):
    with open('players.json', 'w') as f:
        json.dump(something, f, indent=4, sort_keys=True)

write_to_json(something=get_players())
