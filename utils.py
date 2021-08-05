import os
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from flask import Flask, json, jsonify, request
import json

class LeagueStats:
    """
    average tov per game = 15
    average blocks per game = 5
    average stl per game = 8 (of tov)
    average p3 attempts = 34
    average p2 attempts = 54
    average ft attempts = 11
    """
    p3_league_attack_ratio = 34 / 119 # OL3P%
    p2_league_attack_ratio = 54 / 119 # OL2P%
    ft_league_attack_ratio = 11 / 119 # OLFT%
    p3_league_ratio = 0.37 # L3P%
    p2_league_ratio = 0.5 # L2P%
    ft_league_ratio = 0.78 # LFT%

    avg_blocks = 5
    avg_turnovers = 15
    avg_steals = 7.8
    avg_p3a = 34
    avg_p2a = 54
    avg_fta = 11
    total = avg_blocks + avg_turnovers + avg_p3a + avg_p2a + avg_fta

    block_chance = avg_blocks / total # BLKC%
    tov_chance = avg_turnovers / total # TOVC%
    stl_chance = avg_steals / total # STLC%

PROBLEMATIC_PLAYERS = {
    'westbru01': {'drb': -3.5}
}

def sfloat(string):
    if string == '':
        return 0
    else:
        return float(string)

def get_player_year_stats(table, selected_year):
    player_stats = {}

    for year in table:
        if year.find('th') and year.find('th').find('a'):
            if selected_year in year.find('th').find('a').get_text():
                try:
                    player_stats['pos'] = str(year.find('td', {'data-stat': 'pos'}).get_text())

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

                    player_stats['p3_league_attack_ratio'] = round(LeagueStats.p3_league_attack_ratio, 3)
                    player_stats['p2_league_attack_ratio'] = round(LeagueStats.p2_league_attack_ratio, 3)
                    player_stats['ft_league_attack_ratio'] = round(LeagueStats.ft_league_attack_ratio, 3)
                    
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
                            player_stats['team_p3_ratio'] = LeagueStats.p3_league_ratio

                        team_2p = sfloat(team_stats.findAll('td')[8].get_text())
                        team_2pa = sfloat(team_stats.findAll('td')[9].get_text())
                        try:
                            player_stats['team_p2_ratio'] = round(team_2p / team_2pa, 3)
                        except ZeroDivisionError:
                            player_stats['team_p2_ratio'] = LeagueStats.p2_league_ratio

                        team_ft = sfloat(team_stats.findAll('td')[11].get_text())
                        team_fta = sfloat(team_stats.findAll('td')[12].get_text())
                        try:
                            player_stats['team_ft_ratio'] = round(team_ft / team_fta, 3)
                        except ZeroDivisionError:
                            player_stats['team_ft_ratio'] = LeagueStats.ft_league_ratio

                        player_stats['p3_team_attack_ratio'] = round(team_3pa / (team_3pa + team_2pa), 3)
                        player_stats['p2_team_attack_ratio'] = round(team_2pa / (team_3pa + team_2pa), 3)
                        
                    except (TypeError, AttributeError):
                        # no team info
                        player_stats['team_p3_ratio'] = LeagueStats.p3_league_ratio
                        player_stats['team_p2_ratio'] = LeagueStats.p2_league_ratio
                        player_stats['team_ft_ratio'] = LeagueStats.ft_league_ratio    
                        player_stats['p3_team_attack_ratio'] = LeagueStats.p3_league_attack_ratio
                        player_stats['p2_team_attack_ratio'] = LeagueStats.p2_league_attack_ratio

                except IndexError:
                    player_stats['error'] = "IndexError"

    return player_stats

def calc_rating(player_stats):
    if not 'error' in player_stats:
        p3_in = player_stats['p3_in']
        p3_attempts = player_stats['p3_attempts']
        try:
            p3_ratio = p3_in / p3_attempts
        except ZeroDivisionError:
            p3_ratio = 0
        
        p2_in = player_stats['p2_in']
        p2_attempts = player_stats['p2_attempts']
        try:
            p2_ratio = p2_in / p2_attempts
        except ZeroDivisionError:
            p2_ratio = 0

        ft_in = player_stats['ft_in']
        ft_attempts = player_stats['ft_attempts']
        try:
            ft_ratio = ft_in / ft_attempts
        except ZeroDivisionError:
            ft_ratio = 0
        
        p3_on_me = player_stats['p3_on_me']
        p3_attempts_on_me = player_stats['p3_attempts_on_me']
        try:
            p3_ratio_on_me = p3_on_me / p3_attempts_on_me
        except ZeroDivisionError:
            p3_ratio_on_me = 0
        
        p2_on_me = player_stats['p2_on_me']
        p2_attempts_on_me = player_stats['p2_attempts_on_me']
        try:
            p2_ratio_on_me = p2_on_me / p2_attempts_on_me
        except ZeroDivisionError:
            p2_ratio_on_me = 0

        ft_on_me = player_stats['ft_on_me']
        ft_attempts_on_me = player_stats['ft_attempts_on_me']
        try:
            ft_ratio_on_me = ft_on_me / ft_attempts_on_me
        except ZeroDivisionError:
            ft_ratio_on_me = 0

        assists = player_stats['assists']
        d_rebounds = player_stats['d_rebounds']
        off_rebound = player_stats['off_rebound']
        steals = player_stats['steals']
        blocks = player_stats['blocks']
        turnovers = player_stats['turnovers']

        p3_team_ratio = player_stats['team_p3_ratio']
        p2_team_ratio = player_stats['team_p2_ratio']
        ft_team_ratio = player_stats['team_ft_ratio']

        p3_league_attack_ratio = LeagueStats.p3_league_attack_ratio
        p2_league_attack_ratio = LeagueStats.p2_league_attack_ratio
        ft_league_attack_ratio = LeagueStats.ft_league_attack_ratio

        p3_league_ratio = LeagueStats.p3_league_ratio
        p2_league_ratio = LeagueStats.p2_league_ratio
        ft_league_ratio = LeagueStats.ft_league_ratio

        p3_team_attack_ratio = player_stats['p3_team_attack_ratio']
        p2_team_attack_ratio = player_stats['p2_team_attack_ratio']

        z1 = 3 * p3_league_attack_ratio * (p3_league_ratio + 0.02) + 2 * p2_league_attack_ratio * (p2_league_ratio + 0.06) + 2 * ft_league_ratio * ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * LeagueStats.p3_league_ratio + 2 * LeagueStats.p2_league_attack_ratio * p2_league_ratio)
        z2 = 3 * p3_league_attack_ratio * (p3_league_ratio + 0.018) + 2 * p2_league_attack_ratio * (p2_league_ratio + 0.056) + 2 * ft_league_ratio * ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * LeagueStats.p3_league_ratio + 2 * LeagueStats.p2_league_attack_ratio * p2_league_ratio)

        tov_value = (z2 - LeagueStats.stl_chance * z1) / (1 + LeagueStats.tov_chance * LeagueStats.stl_chance)
        stl_value = z1 - LeagueStats.tov_chance * tov_value
        assist_val = 3 * p3_team_attack_ratio * (1 - p3_team_ratio) + 2 * p2_team_attack_ratio * (1 - p2_team_ratio)
        d_rebound_val = 3 * p3_league_attack_ratio * p3_league_ratio + 2 * p2_league_attack_ratio * p2_league_ratio + 2 * ft_league_ratio * ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * LeagueStats.p3_league_ratio + 2 * LeagueStats.p2_league_attack_ratio * LeagueStats.p2_league_ratio) - LeagueStats.tov_chance * tov_value
        off_rebound_val = 3 * p3_league_attack_ratio * (p3_league_ratio + 0.01) + 2 * p2_league_attack_ratio * (p2_league_ratio + 0.03) + 2 * ft_league_ratio * ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * LeagueStats.p3_league_ratio + 2 * LeagueStats.p2_league_attack_ratio * LeagueStats.p2_league_ratio) - LeagueStats.tov_chance * tov_value
        block_val = 0.57 * d_rebound_val


        if assists <= 0.5:
            assists = 0.5

        total = 3 * p3_in * p3_ratio + 2 * p2_in * p2_ratio + 1 * ft_in * ft_ratio + assist_val * assists + d_rebound_val * d_rebounds + off_rebound_val * off_rebound + stl_value * steals + block_val * blocks - tov_value * (turnovers / assists) - (3 * p3_on_me * p3_ratio_on_me + 2 * p2_on_me * p2_ratio_on_me + 1 * ft_on_me * ft_ratio_on_me)

        print(f"""
        ----------------------------------------------
        {tov_value=}
        {stl_value=}
        {assist_val=}
        {d_rebound_val=}
        {off_rebound_val=}
        {block_val=}
        ----------------------------------------------
        """)

        return total
    return 0

def get_top_100():
    SITE_ROOT = os.path.realpath(os.path.dirname(__file__))
    json_url = os.path.join(SITE_ROOT, "static/data", "players.json")

    with open(json_url, 'r') as f:
        data = json.load(f)

        best_players_season = {}
        best_players_playoffs = {}

        for _ in range(100):
            best_rating_season = 0
            best_name_season = ''
            
            best_rating_playoffs = 0
            best_name_playoffs = ''
            
            for player in data:
                if player is not None:
                    if player['rating_season'] > best_rating_season and f"{player['name']}({player['best_year_season']})" not in best_players_season:
                        best_rating_season = player['rating_season']
                        best_name_season = f"{player['name']}({player['best_year_season']})"
                    if player['rating_playoffs'] > best_rating_playoffs and f"{player['name']}({player['best_year_playoffs']})" not in best_players_playoffs:
                        best_rating_playoffs = player['rating_playoffs']
                        best_name_playoffs = f"{player['name']}({player['best_year_playoffs']})"
            
            best_players_season[best_name_season] = round(best_rating_season, 5)
            best_players_playoffs[best_name_playoffs] = round(best_rating_playoffs, 5)
        
        return best_players_season, best_players_playoffs
            

            
            
            