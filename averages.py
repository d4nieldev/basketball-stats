import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
import os
from utils import sfloat
from tqdm import tqdm


def get_stats(link):
    url = f'https://www.basketball-reference.com/players/{link[0]}/{link}'
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    try:
        per_game = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr') 
    except AttributeError:
        # don't count this year
        return
    else:
        height_line = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')[3].get_text().strip()
        height = int(height_line.split('(')[1].split(', ')[0][:-2])
        weight = int(height_line.split('(')[1].split(', ')[1][:-2])
        
        bmi_years_count = 0
        p3_ratio_sum = 0 
        tovs = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }
        drbs = tovs
        orbs = tovs


        for row in tqdm(per_game.findAll('tr')):
            if row.find('th') and row.find('th').find('a'):
                if row.find('th') and row.find('th').find('a') and int(row.find('th').find('a').get_text().split('-')[0]) >= 1990:
                    pos = row.find('td', {'data-stat': 'pos'}).get_text()
                    tovs[pos].append(sfloat(row.find('td', {'data-stat': 'tov_per_g'}).get_text()))
                    drbs[pos].append(sfloat(row.find('td', {'data-stat': 'drb_per_g'}).get_text()))
                    orbs[pos].append(sfloat(row.find('td', {'data-stat': 'orb_per_g'}).get_text()))

                    if int(row.find('th').find('a').get_text().split('-')[0]) == 2021:
                        p3_ratio_sum += sfloat(row.find('td', {'data-stat': 'fg3_pct'}).get_text())
                        bmi_years_count += 1


        for key in tovs:
            tovs[key] = sum(tovs[key]) / len(tovs[key])
            tovs['total'] += tovs[key]

        for key in drbs:
            drbs[key] = sum(drbs[key]) / len(drbs[key])
            drbs['total'] += drbs[key]

        for key in orbs:
            orbs[key] = sum(orbs[key]) / len(orbs[key])
            orbs['total'] += orbs[key]

        return {
            'hgt': height,
            'wgt': weight,
            'bmi': weight / ((height / 100) ** 2),
            'p3': p3_ratio_sum / bmi_years_count,
            'tov': tovs,
            'drb': drbs,
            'orb': orbs
        }

SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
players_data = json.load(open(json_url))

links = []
for player in players_data:
    if player is not None:
        links.append(player['link'])

with concurrent.futures.ThreadPoolExecutor() as executor:
    players_stats = list(executor.map(get_stats, links))

p3s_bmi = {}
tovs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': []
}
drbs = tovs
orbs = tovs



for stat in players_stats:
    print(stat)
    for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
        tovs[pos].append(stat['tov'][pos])
        drbs[pos].append(stat['drb'][pos])
        orbs[pos].append(stat['orb'][pos])
    
    if stat['height'] in drbs.keys():
        drbs[stat['height']].append(stat['total'])
    else:
        drbs[stat['height']] = [stat['total']]

    if stat['height'] in orbs.keys():
        orbs[stat['height']].append(stat['total'])
    else:
        orbs[stat['height']] = [stat['total']]

    if stat['bmi'] in p3s_bmi.keys():
        p3s_bmi.append(stat['p3'])
    else:
        p3s_bmi = [stat['p3']]

# write to json file:
averages = {
    'turnovers': tovs,
    'defense rebounds': drbs,
    'offense rebounds': orbs,
    '3pt per BMI': p3s_bmi
}
with open('averages.json') as f:
    json.dump(averages, f, indent=4, sort_keys=True)
