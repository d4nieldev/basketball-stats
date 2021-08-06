import requests
from bs4 import BeautifulSoup
from string import ascii_lowercase
import json
from utils import calc_rating, get_player_year_stats, sfloat
from tqdm import tqdm
import concurrent.futures
from time import perf_counter

MINIMUM_GAMES_FOR_PLAYOFFS = 12


def get_best_year(soup, years_season, years_playoffs):
    name = soup.find('h1', {'itemprop': 'name'}).find('span').get_text()
    rating_season = 0
    rating_playoffs = 0
    index = 0

    try:
        best_year_season = years_season[0]
    except IndexError:
        best_year_season = -1
    else:
        player_years_season = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')
        for year in tqdm(years_season, desc=f"{name} - Season [{years_season[index]}]", leave=False):
            if int(year.split('-')[0]) >= 1979:
                temp_season = calc_rating(get_player_year_stats(player_years_season, year))

                if temp_season > rating_season:
                    rating_season = temp_season
                    best_year_season = years_season[index]
            index += 1
    
    index = 0
    
    try:
        best_year_playoffs = years_playoffs[0]
    except IndexError:
        best_year_playoffs = -1
    else:
        player_years_playoffs = soup.find("table", {'id': 'playoffs_per_game'}).find("tbody").findAll('tr')
        for year in tqdm(years_playoffs, desc=f"{name} - Playoffs [{years_playoffs[index]}]", leave=False):
            if int(year.split('-')[0]) >= 1979 and sfloat(soup.find("table", {'id': 'playoffs_per_game'}).find('a', string=year).find_parent('tr').findAll('td')[4].get_text()) >= MINIMUM_GAMES_FOR_PLAYOFFS:
                temp_playoffs = calc_rating(get_player_year_stats(player_years_playoffs, year))

                if temp_playoffs > rating_playoffs:
                    rating_playoffs = temp_playoffs
                    best_year_playoffs = years_playoffs[index]
            index += 1
    
    return best_year_season, best_year_playoffs, rating_season, rating_playoffs


def get_player_info(player_row):
    link_to_player = player_row.find("th")['data-append-csv']
    player_name = player_row.find("th").find("a").get_text()
    player_from = player_row.findAll('td')[0].get_text()
    player_to = player_row.findAll('td')[1].get_text()

    # get exact years
    url = f'https://www.basketball-reference.com/players/{link_to_player[0]}/{link_to_player}.html'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    try:
        player_rows_season = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')   
    except AttributeError:
        years_season = set()
    else:
        years_season = set()
        for row in player_rows_season:
            if row.find('th') and row.find('th').find('a') and int(row.find('th').find('a').get_text().split('-')[0]) >= 1979:
                years_season.add(row.find('th').find('a').get_text())
    
    try:
        player_rows_playoffs = soup.find("table", {'id': 'playoffs_per_game'}).find("tbody").findAll('tr')
        years_playoffs = set()
    except AttributeError:
        years_playoffs = set()
    else:
        for row in player_rows_playoffs:
            if row.find('th') and row.find('th').find('a'):
                if int(row.findAll('td')[4].get_text()) >= MINIMUM_GAMES_FOR_PLAYOFFS and row.find('th') and row.find('th').find('a') and int(row.find('th').find('a').get_text().split('-')[0]) >= 1979:
                    if str(row.find('td', {'data-stat': 'pos'}).get_text()) in ['PG', 'SG', 'SF']:
                        if sfloat(row.findAll('td')[10].get_text()) > 0:
                            years_playoffs.add(row.find('th').find('a').get_text())
                    else:
                        years_playoffs.add(row.find('th').find('a').get_text())
    
    if list(years_season) == [] and list(years_playoffs) == []:
        return

    best_years = get_best_year(soup, sorted(years_season), sorted(years_playoffs))

    return {
        'link': link_to_player,
        'name': player_name,
        'from': player_from,
        'to': player_to,
        'years_season': sorted(years_season),
        'years_playoffs': sorted(years_playoffs),
        'best_year_season': best_years[0],
        'best_year_playoffs': best_years[1],
        'rating_season': best_years[2],
        'rating_playoffs': best_years[3]
    }


def get_players():
    players = []

    for c in tqdm(ascii_lowercase, desc="Total"):
        url = f'https://www.basketball-reference.com/players/{c}/'
        content = requests.get(url).content
        soup = BeautifulSoup(content, 'html.parser')

        player_rows = soup.find("table", {'id': 'players'}).find("tbody").findAll('tr')
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            letter_list = list(executor.map(get_player_info, player_rows))
            
        for item in letter_list:
            players.append(item)
    
    return players

def write_to_json(something):
    print("Writing to file...")
    with open('players.json', 'w') as f:
        json.dump(something, f, indent=4, sort_keys=True)
    print("Operation complete!")

if __name__ == "__main__":
    write_to_json(get_players())
