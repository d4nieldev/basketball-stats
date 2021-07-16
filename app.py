import os
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from flask import Flask, render_template, json, jsonify, request
from utils import sfloat, get_player_year_stats, calc_rating, LeagueStats

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

@app.route('/player', methods=['GET', 'POST'])
def player_stats():
    playerSelector = request.form['selector']
    url = "https://www.basketball-reference.com/players/" + playerSelector[0] + "/" + playerSelector + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    return jsonify(get_player_year_stats(soup, request.form['year']))


@app.route('/get_player_years', methods=['POST', 'GET'])
def get_player_years():
    link = request.values['link']

    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")
    players_data = json.load(open(json_url))

    for player in players_data:
        if player["link"] == link:
            return jsonify(player['years'])
    
    return jsonify({"error": 'didnt find player'})

@app.route('/get_best_year', methods=['POST', 'GET'])
def get_best_year():
    link = request.values['link']
    years = request.values['years']
    years = years.split(' ')[1:]

    url = "https://www.basketball-reference.com/players/" + link[0] + "/" + link + ".html"
    content = requests.get(url).content
    soup = BeautifulSoup(content, 'html.parser')

    rating = 0
    best_year = 0
    index = 0

    for year in years:
        if int(year.split('-')[0]) >= 1977:
            print(int(year.split('-')[0]))
            temp = calc_rating(get_player_year_stats(soup, year))
            if temp > rating:
                rating = temp
                best_year = years[index]
        index += 1

    return jsonify({'best_year': best_year})



