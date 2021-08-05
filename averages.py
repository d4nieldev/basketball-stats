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
        # retreive the per_game table
        per_game = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr') 
    except AttributeError:
        # don't count this year
        return
    else:
        # retreive height and weight
        height_line = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')[3].get_text().strip()
        height = int(height_line.split('(')[1].split(', ')[0][:-2])
        weight = int(height_line.split('(')[1].split(', ')[1][:-2])
        
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
        p3s = tovs
        p3pcs = tovs

        for row in tqdm(per_game.findAll('tr')):
            if row.find('th') and row.find('th').find('a'):
                if row.find('th') and row.find('th').find('a') and int(row.find('th').find('a').get_text().split('-')[0]) >= 1990:
                    pos = row.find('td', {'data-stat': 'pos'}).get_text()
                    tovs[pos].append(sfloat(row.find('td', {'data-stat': 'tov_per_g'}).get_text()))
                    drbs[pos].append(sfloat(row.find('td', {'data-stat': 'drb_per_g'}).get_text()))
                    orbs[pos].append(sfloat(row.find('td', {'data-stat': 'orb_per_g'}).get_text()))
                    

                    if int(row.find('th').find('a').get_text().split('-')[0]) == 2020:
                        p3 = sfloat(row.find('td', {'data-stat': 'fg3_pct'}).get_text())
                        p3pc = sfloat(row.find('td', {'data-stat': 'fg3_per_g'}).get_text())

                        p3s[pos] += p3
                        p3pcs[pos] += p3pc


        for d in [tovs, drbs, orbs, p3s, p3pcs]:
            for key in d:
                d[key] = sum(d[key]) / d(tovs[key])
                d['total'] += d[key]
        
        data = {
            'hgt': height,
            'wgt': weight,
            'bmi': weight / ((height / 100) ** 2),
            'p3pc': p3pcs,
            'p3': p3s,
            'tov': tovs,
            'drb': drbs,
            'orb': orbs
        }
        print(data)

        return data


def avg_lst(lst):
    sum = 0

    for item in lst:
        sum += item

    return sum / len(lst)


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
players_data = json.load(open(json_url))

links = []
for player in players_data:
    if player is not None:
        links.append(player['link'])

with concurrent.futures.ThreadPoolExecutor() as executor:
    players_stats = list(executor.map(get_stats, links))

tovs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': []
}
drbs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': [],
    'heights': {}
}
orbs = drbs
p3pcs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': [],
    'bmis': {}
}
p3s = p3pcs

for stat in players_stats:
    # for each player
    for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
        # copy values from each player to the matching position in the total dict
        tovs[pos].append(stat['tov'][pos])
        drbs[pos].append(stat['drb'][pos])
        orbs[pos].append(stat['orb'][pos])
        p3pcs[pos].append(stat['p3pc'][pos])
        p3s[pos].append(stat['p3'][pos])
    
    # add player average to height key in heights in orbs 
    if stat['height'] in orbs['heights'].keys():
        orbs['heights'][stat['height']].append(stat['orb']['total'])
    else:
        orbs['heights'][stat['height']] = [stat['orb']['total']]

    # add player average to height key in heights in drbs
    if stat['height'] in drbs['heights'].keys():
        drbs['heights'][stat['height']].append(stat['drb']['total'])
    else:
        drbs['heights'][stat['height']] = [stat['drb']['total']]

    # add player average to bmi key in bmis in p3s
    if stat['bmi'] in p3s['bmis'].keys():
        p3s['bmis'][stat['bmi']].append(stat['p3']['total'])
    else:
        p3s['bmis'][stat['bmi']] = [stat['p3']['total']]

    # add player average to bmi key in bmis in p3pcs
    if stat['bmi'] in p3pcs['bmis'].keys():
        p3pcs['bmis'][stat['bmi']].append(stat['p3pc']['total'])
    else:
        p3pcs['bmis'][stat['bmi']] = [stat['p3pc']['total']]


for d in [tovs, drbs, orbs, p3s, p3pcs]:
        for idx, (key, val) in enumerate(d.items()):
            if idx < 5:
                # for positions
                d[key] = avg_lst(val)
            else:
                # for height or bmi
                for height, avgs in val.items():
                    # for each height, average the averages
                    val[height] = avg_lst(avgs)



# write to json file:
averages = {
    'turnovers': tovs,
    'defense rebounds': drbs,
    'offense rebounds': orbs,
    '3P per BMI or height': p3s,
    '3P% per BMI or height': p3pcs
}
with open('averages.json') as f:
    json.dump(averages, f, indent=4, sort_keys=True)
