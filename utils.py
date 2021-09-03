import os
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from flask import Flask, json, jsonify, request
import json
import re

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
    p2_league_ratio = 0.52 # L2P%
    ft_league_ratio = 0.78 # LFT%

    stl_p3 = 0.02
    stl_p2 = 0.06

    tov_p3 = 0.015
    tov_p2 = 0.05

    orb_p3 = 0.01
    orb_p2 = 0.03

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

    stl_turnovers = avg_steals / avg_turnovers # STOV%

    good_shooter_minimum_3p = 1.3
    good_shooter_minimum_ratio = 0.401
    good_shooter_3p_multiplier = 3.3

    ast_min_val = 0.5

    p3_league_attack_from_assist_ratio = 0.39
    p2_league_attack_from_assist_ratio = 0.61



def sfloat(string):
    if string == '':
        return 0
    else:
        return float(string)


def get_top_100(data):
    best_players_season = {}
    best_players_playoffs = {}

    for _ in range(100):
        best_rating_season = 0
        best_name_season = ''
        
        best_rating_playoffs = 0
        best_name_playoffs = ''
        
        for player in data:
            if player is not None:
                # player needs to be the best of the unchecked
                if player['rating_season_top100'] > best_rating_season and f"{player['name']} ({player['best_year_season_top100']})" not in best_players_season:
                    # on season, count only the best year that can be top100!
                    best_rating_season = player['rating_season_top100']
                    best_name_season = f"{player['name']} ({player['best_year_season_top100']})"
                if player['rating_playoffs'] > best_rating_playoffs and f"{player['name']} ({player['best_year_playoffs']})" not in best_players_playoffs:
                    best_rating_playoffs = player['rating_playoffs']
                    best_name_playoffs = f"{player['name']} ({player['best_year_playoffs']})"
        
        best_players_season[best_name_season] = round(best_rating_season, 5)
        best_players_playoffs[best_name_playoffs] = round(best_rating_playoffs, 5)
    
    return best_players_season, best_players_playoffs


def get_player_year_stats(table, selected_year):
    player_stats = {}

    for year in table:
        if year.find('th') and year.find('th').find('a'):
            if selected_year in year.find('th').find('a').get_text():
                try:
                    player_stats['pos'] = str(year.find('td', {'data-stat': 'pos'}).get_text())

                    player_stats['p3_in'] = sfloat(year.find('td', {'data-stat': 'fg3_per_g'}).get_text())
                    player_stats['p3_attempts'] = sfloat(year.find('td', {'data-stat': 'fg3a_per_g'}).get_text())
                    if player_stats['p3_attempts'] != 0:
                        player_stats['p3_ratio'] = player_stats['p3_in'] / player_stats['p3_attempts']
                    else:
                        player_stats['p3_ratio'] = 0

                    player_stats['p2_in'] = sfloat(year.find('td', {'data-stat': 'fg2_per_g'}).get_text())
                    player_stats['p2_attempts'] = sfloat(year.find('td', {'data-stat': 'fg2a_per_g'}).get_text())
                    if player_stats['p2_attempts'] != 0:
                        player_stats['p2_ratio'] = player_stats['p2_in'] / player_stats['p2_attempts']
                    else:
                        player_stats['p2_ratio'] = 0

                    player_stats['ft_in'] = sfloat(year.find('td', {'data-stat': 'ft_per_g'}).get_text())
                    player_stats['ft_attempts'] = sfloat(year.find('td', {'data-stat': 'fta_per_g'}).get_text())
                    if player_stats['ft_attempts'] != 0:
                        player_stats['ft_ratio'] = player_stats['ft_in'] / player_stats['ft_attempts']
                    else:
                        player_stats['ft_ratio'] = 0

                    player_stats['p3_on_me'] = 0
                    player_stats['p3_attempts_on_me'] = 0
                    player_stats['p3_on_me_ratio'] = 0

                    player_stats['p2_on_me'] = 0
                    player_stats['p2_attempts_on_me'] = 0
                    player_stats['p2_on_me_ratio'] = 0

                    player_stats['ft_on_me'] = 0
                    player_stats['ft_attempts_on_me'] = 0
                    player_stats['ft_on_me_ratio'] = 0

                    player_stats['assists'] = sfloat(year.find('td', {'data-stat': 'ast_per_g'}).get_text())
                    player_stats['d_rebounds'] = sfloat(year.find('td', {'data-stat': 'drb_per_g'}).get_text())
                    player_stats['off_rebound'] = sfloat(year.find('td', {'data-stat': 'orb_per_g'}).get_text())
                    player_stats['steals'] = sfloat(year.find('td', {'data-stat': 'stl_per_g'}).get_text())
                    player_stats['blocks'] = sfloat(year.find('td', {'data-stat': 'blk_per_g'}).get_text())
                    player_stats['turnovers'] = sfloat(year.find('td', {'data-stat': 'tov_per_g'}).get_text())
                    player_stats['minutes_of_play'] = sfloat(year.find('td', {'data-stat': 'mp_per_g'}).get_text())

                    player_stats['games'] = sfloat(year.find('td', {'data-stat': 'g'}).get_text())

                    player_stats['p3_league_attack_ratio'] = round(LeagueStats.p3_league_attack_ratio, 3)
                    player_stats['p2_league_attack_ratio'] = round(LeagueStats.p2_league_attack_ratio, 3)
                    player_stats['ft_league_attack_ratio'] = round(LeagueStats.ft_league_attack_ratio, 3)
                    
                    try:
                        team_url = "https://www.basketball-reference.com" + year.find('td', {'data-stat': 'team_id'}).find('a')['href']
                        team_content = requests.get(team_url).content
                        team_soup = BeautifulSoup(team_content, 'html.parser')

                        team_winrate = 0
                        team_general_stats = team_soup.find("div", {"data-template": "Partials/Teams/Summary"}).findAll('p')
                        for stat in team_general_stats:
                            if stat.find("strong").get_text() == 'Record:':
                                record = re.findall("[0-9]+-[0-9]+", stat.get_text())[0]
                                team_winrate = int(record.split('-')[0]) / (int(record.split('-')[0]) + int(record.split('-')[1]))
                        player_stats['team_winrate'] = team_winrate

                        comments = team_soup.find_all(string=lambda text: isinstance(text, Comment))
                        team_stats_soup = BeautifulSoup(comments[34], 'html.parser')
                        team_stats = team_stats_soup.find('table').find('tbody').find('tr')

                        team_3p = sfloat(team_stats.find('td', {'data-stat': 'fg3'}).get_text())
                        team_3pa = sfloat(team_stats.find('td', {'data-stat': 'fg3a'}).get_text())
                        if team_3pa != 0:
                            player_stats['team_p3_ratio'] = round(team_3p / team_3pa, 3)
                        else:
                            player_stats['team_p3_ratio'] = 0

                        team_2p = sfloat(team_stats.find('td', {'data-stat': 'fg2'}).get_text())
                        team_2pa = sfloat(team_stats.find('td', {'data-stat': 'fg2a'}).get_text())
                        if team_2pa != 0:
                            player_stats['team_p2_ratio'] = round(team_2p / team_2pa, 3)
                        else:
                            player_stats['team_p2_ratio'] = 0

                    except (TypeError, AttributeError):
                        # no team info
                        player_stats['team_p3_ratio'] = LeagueStats.p3_league_ratio
                        player_stats['team_p2_ratio'] = LeagueStats.p2_league_ratio  
                except IndexError:
                    player_stats['error'] = "IndexError"

    return player_stats

def calc_rating(player_stats):
    if not 'error' in player_stats:
        p3_in = player_stats['p3_in']
        p2_in = player_stats['p2_in']
        ft_in = player_stats['ft_in']

        p3_on_me = player_stats['p3_on_me']
        p2_on_me = player_stats['p2_on_me']
        ft_on_me = player_stats['ft_on_me']

        p3_ratio = player_stats['p3_ratio']
        p2_ratio = player_stats['p2_ratio']
        ft_ratio = player_stats['ft_ratio']

        p3_on_me_ratio = player_stats['p3_on_me_ratio']
        p2_on_me_ratio = player_stats['p2_on_me_ratio']
        ft_on_me_ratio = player_stats['ft_on_me_ratio']

        assists = player_stats['assists']
        d_rebounds = player_stats['d_rebounds']
        off_rebound = player_stats['off_rebound']
        steals = player_stats['steals']
        blocks = player_stats['blocks']
        turnovers = player_stats['turnovers']

        if assists <= LeagueStats.ast_min_val:
            assists = LeagueStats.ast_min_val
        
        if p3_ratio >= LeagueStats.good_shooter_minimum_ratio and p3_in >= LeagueStats.good_shooter_minimum_3p:
            p3_multiplier = LeagueStats.good_shooter_3p_multiplier
        else:
            p3_multiplier = 3

        z1 = 3 * LeagueStats.p3_league_attack_ratio * ((LeagueStats.p3_league_ratio + LeagueStats.stl_p3) ** 2) + 2 * LeagueStats.p2_league_attack_ratio * ((LeagueStats.p2_league_ratio + LeagueStats.stl_p2) ** 2) + 2 * (LeagueStats.ft_league_ratio ** 2) * LeagueStats.ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * (LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (LeagueStats.p2_league_ratio ** 2))
        z2 = 3 * LeagueStats.p3_league_attack_ratio * ((LeagueStats.p3_league_ratio + LeagueStats.tov_p3) ** 2) + 2 * LeagueStats.p2_league_attack_ratio * ((LeagueStats.p2_league_ratio + LeagueStats.tov_p2) ** 2) + 2 * (LeagueStats.ft_league_ratio ** 2) * LeagueStats.ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * (LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (LeagueStats.p2_league_ratio ** 2))

        tov_value = (z2 - LeagueStats.stl_chance * z1) / (1 + LeagueStats.tov_chance * LeagueStats.stl_chance)
        stl_value = z1 - LeagueStats.tov_chance * tov_value
        assist_val = 0.48 * (3 * LeagueStats.p3_league_ratio * LeagueStats.p3_league_attack_from_assist_ratio + 2 * LeagueStats.p2_league_ratio * LeagueStats.p2_league_attack_from_assist_ratio)
        d_rebound_val = 3 * LeagueStats.p3_league_attack_ratio * (LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (LeagueStats.p2_league_ratio ** 2) + 2 * LeagueStats.ft_league_ratio * (LeagueStats.ft_league_attack_ratio ** 2) - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * (LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (LeagueStats.p2_league_ratio ** 2)) - LeagueStats.tov_chance * tov_value
        off_rebound_val = 3 * LeagueStats.p3_league_attack_ratio * ((LeagueStats.p3_league_ratio + LeagueStats.orb_p3) ** 2) + 2 * LeagueStats.p2_league_attack_ratio * ((LeagueStats.p2_league_ratio + LeagueStats.orb_p2) ** 2) + 2 * (LeagueStats.ft_league_ratio ** 2) * LeagueStats.ft_league_attack_ratio - LeagueStats.block_chance * (3 * LeagueStats.p3_league_attack_ratio * (LeagueStats.p3_league_ratio ** 2) + 2 * LeagueStats.p2_league_attack_ratio * (LeagueStats.p2_league_ratio ** 2)) - LeagueStats.tov_chance * tov_value
        block_val = 0.57 * d_rebound_val

        total = p3_multiplier * p3_in * p3_ratio + 2 * p2_in * p2_ratio + 1 * ft_in * ft_ratio + assist_val * assists + d_rebound_val * d_rebounds + off_rebound_val * off_rebound + stl_value * steals + block_val * blocks -  tov_value * (turnovers / (LeagueStats.stl_turnovers * assists)) - (3 * p3_on_me * p3_on_me_ratio + 2 * p2_on_me * p2_on_me_ratio + 1 * ft_on_me * ft_on_me_ratio)

        return total
    return 0