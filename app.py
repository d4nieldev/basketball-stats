import os
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, json, jsonify, request

app = Flask(__name__)

def sfloat(string):
    if string == '':
        return 0
    else:
        return float(string)

@app.route('/')
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    players = []

    for player in players_data:
        player_string = f'{player["name"]} ({player["from"]}-{player["to"]})'
        player_data = [player_string, player['link']]
        players.append(player_data)

    return render_template('basketball_stats.html', players=players)

@app.route('/player', methods=['GET', 'POST'])
def player_stats():
    playerSelector = request.form['selector']
    url = "https://www.basketball-reference.com/players/" + playerSelector[0] + "/" + playerSelector + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    returnme = ""

    player_years = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')
    found = False
    player_stats = {}

    for year in player_years:
        if not found and request.form['year'] in year.find('th').find('a').get_text():
            found = True

            player_stats['p3_in'] = sfloat(year.findAll('td')[10].get_text())
            player_stats['p3_attempts'] = sfloat(year.findAll('td')[11].get_text())

            player_stats['p2_in'] = sfloat(year.findAll('td')[13].get_text())
            player_stats['p2_attempts'] = sfloat(year.findAll('td')[14].get_text())

            player_stats['ft_in'] = sfloat(year.findAll('td')[17].get_text())
            player_stats['ft_attempts'] = sfloat(year.findAll('td')[18].get_text())

            player_stats['p3_on_me'] = 0
            player_stats['p3_attempts_on_me'] = 0

            player_stats['p2_on_me'] = 0
            player_stats['p2_attempts_on_me'] = 0

            player_stats['ft_on_me'] = 0
            player_stats['ft_attempts_on_me'] = 0

            player_stats['assists'] = sfloat(year.findAll('td')[23].get_text())
            player_stats['d_rebounds'] = sfloat(year.findAll('td')[21].get_text())
            player_stats['off_rebound'] = sfloat(year.findAll('td')[20].get_text())
            player_stats['steals'] = sfloat(year.findAll('td')[24].get_text())
            player_stats['blocks'] = sfloat(year.findAll('td')[25].get_text())
            player_stats['turnovers'] = sfloat(year.findAll('td')[26].get_text())
            player_stats['minutes_of_play'] = sfloat(year.findAll('td')[6].get_text())
        

    return jsonify(player_stats)