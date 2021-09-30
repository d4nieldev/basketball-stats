import os
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from flask import Flask, render_template, json, jsonify, request
from utils import sfloat, get_player_year_stats, calc_rating, LeagueStats, get_top_100

app = Flask(__name__)

@app.route('/')
def index():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    players = []

    for player in players_data:
        if player is not None:
            player_string = f'{player["name"]} ({player["from"]}-{player["to"]})'
            player_data = [player_string, player['link']]
            players.append(player_data)

    top100 = get_top_100()
    return render_template(
        'basketball_stats.html', 
        players=players, 
        top100season_keys=list(top100[0].keys()),
        top100season_items=list(top100[0].values()), 
        top100playoffs_keys=list(top100[1].keys()),
        top100playoffs_items=list(top100[1].values()),
        top100avg_keys=list(top100[2].keys()),
        top100avg_items=list(top100[2].values())
)

@app.route('/player', methods=['GET', 'POST'])
def player_stats():
    playerSelector = request.form['selector']
    url = "https://www.basketball-reference.com/players/" + playerSelector[0] + "/" + playerSelector + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    is_playoff = bool(request.form['playoffs'] == 'Playoffs')
    if is_playoff:
        player_years = soup.find("table", {'id': 'playoffs_per_game'}).find("tbody").findAll('tr')
    else:
        player_years = soup.find("table", {'id': 'per_game'}).find("tbody").findAll('tr')

    player_stats = get_player_year_stats(player_years, request.form['year'])
    height_line = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')[3].get_text().strip()
    try:
        height_line = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')[3].get_text().strip()
        player_stats['height'] = int(height_line.split('(')[1].split(',')[0][:-2])
    except IndexError:
        height_line = soup.find('div', {"itemtype": "https://schema.org/Person"}).findAll('p')[4].get_text().strip()
        player_stats['height'] = int(height_line.split('(')[1].split(',')[0][:-2])

    return jsonify(player_stats)


@app.route('/get_player_years', methods=['POST', 'GET'])
def get_player_years():
    link = request.values['link']
    is_playoff = bool(request.values['playoffs'] == 'Playoffs')

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    for player in players_data:
        if player is not None:
            if player["link"] == link:
                if is_playoff:
                    return jsonify(player['years_playoffs'])
                else:
                    return jsonify(player['years_season'])
    
    return jsonify({"error": 'didnt find player'})

@app.route('/get_best_year', methods=['POST', 'GET'])
def get_best_year():
    link = request.values['link']
    is_playoff = bool(request.values['playoffs'] == 'Playoffs')

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    best_year = -1

    for d in players_data:
        if d is not None:
            if d['link'] == link:
                best_year = d['best_year_playoffs'] if is_playoff else d['best_year_season']
                break
    

    return jsonify({'best_year': best_year})


@app.route('/apply_formula', methods=['POST', 'GET'])
def apply_formula():
    values = request.form.to_dict()

    for key, val in values.items():
        values[key] = 0 if val == 'NaN' else float(val)
    
    rating = calc_rating(values)
    return jsonify({'rating': rating})


@app.route('/get_link_from_name', methods=['POST', 'GET'])
def get_link_from_name():
    player_name = request.form.to_dict()['player_name']

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    for player in players_data:
        if player is not None and player['name'] == player_name:
            return jsonify(player['link'])
    return jsonify("ERR")