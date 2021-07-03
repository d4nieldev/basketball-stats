import os
import sys
import requests
from bs4 import BeautifulSoup
from flask import Flask, render_template, json, jsonify, request

app = Flask(__name__)

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

@app.route('/player/<playerselector>')
def player_stats(playerselector):
    url = "https://www.basketball-reference.com/players/" + playerselector[0] + "/" + playerselector + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    print(soup.prettify(), sys.stderr)