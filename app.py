import os
import sys
import requests
import time
from bs4 import BeautifulSoup
from bs4 import Comment
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
        if year.find('th') and year.find('th').find('a'):
            if not found and request.form['year'] in year.find('th').find('a').get_text():
                found = True
                try:
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
                    
                    try:
                        team_url = "https://www.basketball-reference.com" + year.find('td', {'data-stat': 'team_id'}).find('a')['href']
                        team_content = requests.get(team_url).content
                        team_soup = BeautifulSoup(team_content, 'html.parser')

                        comments = team_soup.find_all(string=lambda text: isinstance(text, Comment))
                        team_stats_soup = BeautifulSoup(comments[34], 'html.parser')
                        team_stats = team_stats_soup.find('table').find('tbody').find('tr')

                        team_3p = sfloat(team_stats.findAll('td')[5].get_text())
                        team_3pa = sfloat(team_stats.findAll('td')[6].get_text())
                        try:
                            player_stats['team_p3_ratio'] = round(team_3p / team_3pa, 3)
                        except ZeroDivisionError:
                            player_stats['team_p3_ratio'] = 0.38

                        team_2p = sfloat(team_stats.findAll('td')[8].get_text())
                        team_2pa = sfloat(team_stats.findAll('td')[9].get_text())
                        try:
                            player_stats['team_p2_ratio'] = round(team_2p / team_2pa, 3)
                        except ZeroDivisionError:
                            player_stats['team_p2_ratio'] = 0.38

                        team_ft = sfloat(team_stats.findAll('td')[11].get_text())
                        team_fta = sfloat(team_stats.findAll('td')[12].get_text())
                        try:
                            player_stats['team_ft_ratio'] = round(team_ft / team_fta, 3)
                        except ZeroDivisionError:
                            player_stats['team_ft_ratio'] = 0.38
                        
                    except TypeError:
                        # no team info
                        player_stats['team_p3_ratio'] = 0.38
                        player_stats['team_p2_ratio'] = 0.48
                        player_stats['team_ft_ratio'] = 0.8      

                except IndexError:
                    player_stats['error'] = "IndexError"

    return jsonify(player_stats)


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