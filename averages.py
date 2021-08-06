import requests
from bs4 import BeautifulSoup
import json
import concurrent.futures
import os
from utils import sfloat
from tqdm import tqdm
import re
import pprint


def get_stats(link):
    url = f'https://www.basketball-reference.com/players/{link[0]}/{link}.html'
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
        desc = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')
        height = 0
        weight = 0
        for line in desc:
            txt = line.get_text().strip()
            try:
                hgt = int(re.findall("([0-9]+)cm", txt)[0])
                wgt = int(re.findall("([0-9]+)kg", txt)[1])

                # if height and weight were found than assign them and stop searching
                height = hgt
                weight = wgt
                break
            except IndexError:
                # didn't find height and weight for this line
                pass
                

        if height == 0 or weight == 0:
            # if no height or weight found, skip this year
            return
        

        
        tovs = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }
        drbs = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }
        orbs = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }
        p3s = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }
        p3pcs = {
            'PG': [],
            'SG': [],
            'SF': [],
            'PF': [],
            'C': [],
            'total': []
        }

        for row in tqdm(per_game, desc=link, leave=True):
            if row.find('th') and row.find('th').find('a'):
                if row.find('th') and row.find('th').find('a') and int(row.find('th').find('a').get_text().split('-')[0]) >= 1990:
                    pos = [item for item in row.find('td', {'data-stat': 'pos'}).get_text().split(',')]
                    for p in pos:
                        tovs[p].append(sfloat(row.find('td', {'data-stat': 'tov_per_g'}).get_text()))
                        drbs[p].append(sfloat(row.find('td', {'data-stat': 'drb_per_g'}).get_text()))
                        orbs[p].append(sfloat(row.find('td', {'data-stat': 'orb_per_g'}).get_text()))
                    
                    tovs['total'].append(sfloat(row.find('td', {'data-stat': 'tov_per_g'}).get_text()))
                    drbs['total'].append(sfloat(row.find('td', {'data-stat': 'drb_per_g'}).get_text()))
                    orbs['total'].append(sfloat(row.find('td', {'data-stat': 'orb_per_g'}).get_text()))

                    if int(row.find('th').find('a').get_text().split('-')[0]) == 2020:
                        p3 = sfloat(row.find('td', {'data-stat': 'fg3_pct'}).get_text())
                        p3pc = sfloat(row.find('td', {'data-stat': 'fg3_per_g'}).get_text())

                        for p in pos:
                            p3s[p].append(p3)
                            p3pcs[p].append(p3pc)

                        p3pcs['total'].append(p3pc)
                        p3s['total'].append(p3)

        data_list = [tovs, drbs, orbs, p3s, p3pcs]
        
        for i in range(len(data_list)):
            keys_to_pop = []
            for key, val in data_list[i].items():
                if val == []:
                    keys_to_pop.append(key)
            for k in keys_to_pop:
                if k == 'total':
                    data_list[i]['total'] = 0
                data_list[i].pop(k)

        for i in range(len(data_list)):
            for key, val in data_list[i].items():
                avg = avg_lst(val)
                data_list[i][key] = avg

        return {
            'hgt': height,
            'wgt': weight,
            'bmi': weight / ((height / 100) ** 2),
            'p3pc': p3pcs,
            'p3': p3s,
            'tov': tovs,
            'drb': drbs,
            'orb': orbs
        }


def avg_lst(lst):
    if len(lst) == 0:
        return None

    return sum(lst) / len(lst)


SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
players_data = json.load(open(json_url))

links = []
for player in players_data:
    if player is not None:
        links.append(player['link'])

# players_stats = []
# for player in links:
#     players_stats.append(get_stats(player))
#     break
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
orbs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': [],
    'heights': {}
}
p3pcs = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': [],
    'bmis': {}
}
p3s = {
    'PG': [],
    'SG': [],
    'SF': [],
    'PF': [],
    'C': [],
    'bmis': {}
}

for stat in players_stats:
    # for each player
    if stat:
        for pos in ['PG', 'SG', 'SF', 'PF', 'C']:
            # copy values from each player to the matching position in the total dict
            if pos in stat['tov']:
                tovs[pos].append(stat['tov'][pos])
            if pos in stat['drb']:
                drbs[pos].append(stat['drb'][pos])
            if pos in stat['orb']:
                orbs[pos].append(stat['orb'][pos])
            if pos in stat['p3pc']:
                p3pcs[pos].append(stat['p3pc'][pos])
            if pos in stat['p3']:
                p3s[pos].append(stat['p3'][pos])
    
    # add player average to height key in heights in orbs 
    if stat['hgt'] in orbs['heights'].keys():
        orbs['heights'][stat['hgt']].append(stat['orb']['total'])
    else:
        orbs['heights'][stat['hgt']] = [stat['orb']['total']]

    # add player average to height key in heights in drbs
    if stat['hgt'] in drbs['heights'].keys():
        drbs['heights'][stat['hgt']].append(stat['drb']['total'])
    else:
        drbs['heights'][stat['hgt']] = [stat['drb']['total']]

    # add player average to bmi key in bmis in p3s
    if stat['bmi'] in p3s['bmis']:
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
            avg = avg_lst(val)
            d[key] = None
            d[key] = avg
        else:
            # for height or bmi
            for height, avgs in val.items():
                # for each height, average the averages
                avg = avg_lst(avgs)
                val[height] = None
                val[height] = avg



# write to json file:
averages = {
    'turnovers': tovs,
    'defense rebounds': drbs,
    'offense rebounds': orbs,
    '3P per BMI or height': p3s,
    '3P% per BMI or height': p3pcs
}
with open('averages.json', 'w') as f:
    json.dump(averages, f, indent=4, sort_keys=True)
