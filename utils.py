import os
import requests
from bs4 import BeautifulSoup
from bs4 import Comment
from flask import Flask, json, jsonify, request

class LeagueStats:
    p3_league_attack_ratio = 0.24
    p2_league_attack_ratio = 0.6
    ft_league_attack_ratio = 0.16
    p3_league_ratio = 0.37
    p2_league_ratio = 0.5
    ft_league_ratio = 0.78


def sfloat(string):
    if string == '':
        return 0
    else:
        return float(string)

def get_player_year_stats(table, selected_year):
    found = False
    player_stats = {}

    for year in table:
        if year.find('th') and year.find('th').find('a'):
            if not found and selected_year in year.find('th').find('a').get_text():
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
                        
                    except (TypeError, AttributeError):
                        # no team info
                        player_stats['team_p3_ratio'] = LeagueStats.p3_league_ratio
                        player_stats['team_p2_ratio'] = LeagueStats.p2_league_ratio
                        player_stats['team_ft_ratio'] = LeagueStats.ft_league_ratio      

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
        minutes_of_play = player_stats['minutes_of_play']
        p3_team_ratio = player_stats['team_p3_ratio']
        p2_team_ratio = player_stats['team_p2_ratio']
        ft_team_ratio = player_stats['team_ft_ratio']

        p3_league_attack_ratio = LeagueStats.p3_league_attack_ratio
        p3_team_attack_ratio = LeagueStats.p3_league_attack_ratio
        p2_league_attack_ratio = LeagueStats.p2_league_attack_ratio
        p2_team_attack_ratio = LeagueStats.p2_league_attack_ratio
        ft_league_attack_ratio = LeagueStats.ft_league_attack_ratio
        p3_league_ratio = LeagueStats.p3_league_ratio
        p2_league_ratio = LeagueStats.p2_league_ratio
        ft_league_ratio = LeagueStats.ft_league_ratio

        assist_val = 3 * p3_league_attack_ratio * (1 - p3_team_ratio) + 2 * p2_league_attack_ratio * (1 - p2_team_ratio)
        d_rebound_val = 3 * p3_league_attack_ratio * p3_league_ratio + 2 * p2_league_attack_ratio * p2_league_ratio + 2 * ft_league_ratio * ft_league_attack_ratio
        off_rebound_val = d_rebound_val + 2 * p2_ratio * p2_league_attack_ratio + 2 * ft_ratio * ft_league_attack_ratio
        steal_val = d_rebound_val + 2 * p2_ratio * p2_league_attack_ratio + 2 * ft_ratio * ft_league_attack_ratio;
        block_val = 0.57 * d_rebound_val
        turnover_val = d_rebound_val + 2 * p2_league_ratio * p2_league_attack_ratio + 2 * ft_league_ratio * ft_league_attack_ratio
        total = 3 * p3_in * p3_ratio + 2 * p2_in * p2_ratio + 1 * ft_in * ft_ratio + assist_val * assists + d_rebound_val * d_rebounds + off_rebound_val * off_rebound + steal_val * steals + block_val * blocks - turnover_val * turnovers - (3 * p3_on_me * p3_ratio_on_me + 2 * p2_on_me * p2_ratio_on_me + 1 * ft_on_me * ft_ratio_on_me)
        try:
            total /= minutes_of_play
        except ZeroDivisionError:
            total = 0

        return total
    return 0
    