import os

from nba_api.stats.endpoints import teamgamelogs, leaguegamelog
from nba_api.stats.static import teams
from time import sleep
import numpy as np

from constants import data_directory, output_file, input_file, relevant_team_perf_metrics, stats_to_be_averaged
from game_overview import GameOverview
from utils.dates import get_season_start_and_end_dates, start_year_to_season


# converts a list of headers and data into a map of header:data
def reformat_response(response_dict):
    return [dict(zip(response_dict['headers'], data)) for data in response_dict['data']]


def get_team_abbrev_to_id_map():
    return {t['abbreviation']: t['id'] for t in teams.get_teams()}


def get_team_gamelogs(team_id, season="", date_from="", date_to=""):
    t = teamgamelogs.TeamGameLogs(team_id_nullable=team_id,
                                  season_nullable=season,
                                  date_from_nullable=date_from,
                                  date_to_nullable=date_to)
    d = t.team_game_logs.get_dict()
    d['data'].reverse()  # the dates are given in reverse chrono. order, but we want them in chrono. order
    return reformat_response(d)


def get_team_gamelogs_for_season(team_id, season_start_year):
    start_date, end_date = get_season_start_and_end_dates(season_start_year)
    return get_team_gamelogs(team_id,
                             start_year_to_season(season_start_year),
                             start_date,
                             end_date)


# given a matchup string, which is of format either "TEAM1 vs. TEAM2" or "TEAM1 @ TEAM2",
# returns the names of the two teams, with the home team first and the away team second
def get_teams_by_matchup_str(matchup: str):
    s = matchup.split()
    assert len(s) == 3
    if s[1] == 'vs.':
        return s[0], s[2]
    assert(s[1] == '@')
    return s[2], s[0]


def get_league_gamelogs(season_start_year):
    team_ids_map = get_team_abbrev_to_id_map()
    start_date, end_date = get_season_start_and_end_dates(season_start_year)
    gamelogs = reformat_response(leaguegamelog.LeagueGameLog(
        season=start_year_to_season(season_start_year),
        date_from_nullable=start_date,
        date_to_nullable=end_date).league_game_log.get_dict())
    # remove duplicates and map to GameOverview objects
    seen_game_ids = set()
    new_gamelogs = []
    for game in gamelogs:
        if game['GAME_ID'] not in seen_game_ids:
            seen_game_ids.add(game['GAME_ID'])
            home_team, away_team = get_teams_by_matchup_str(game['MATCHUP'])
            home_team_won = (home_team == game['TEAM_ABBREVIATION']) == (game['WL'] == 'W')
            new_gamelogs.append(
                GameOverview(
                    game['GAME_ID'],
                    game['GAME_DATE'],
                    team_ids_map[home_team],
                    team_ids_map[away_team],
                    home_team_won
                )
            )
    return new_gamelogs


# given the teams data, returns a list that can be saved and later used as input data for the ML model
def encode_data(home_team_data, away_team_data):
    # extract relevant data from raw data dict
    return [home_team_data[metric] for metric in relevant_team_perf_metrics] + \
        [away_team_data[metric] for metric in relevant_team_perf_metrics]


# given a list of games for a team in chronological order, returns a dict which maps a game id to the accumulated stats
# of the team up to but not including the date of the game.
# gamelogs should be a list of gamelog dicts (ex. [{'SEASON_YEAR': '2019-20', 'TEAM_ID': 123, ... }, {...}, ...]
# returns a map of accumulated stats that looks like
#   { game_id: {'W': 6, 'L': 4, 'W_PCT': 0.6, 'FGM': 34.5, ... } }
def accumulate_team_gamelog_stats(gamelogs):
    wins = losses = 0

    for i in range(len(gamelogs)):
        if gamelogs[i]['WL'] == 'W':
            wins += 1
        else:
            losses += 1
        gamelogs[i]['W'] = wins
        gamelogs[i]['L'] = losses
        gamelogs[i]['W_PCT'] = wins/(wins + losses)
        if i >= 1:
            for metric in stats_to_be_averaged:
                gamelogs[i][metric] = (gamelogs[i-1][metric]*i + gamelogs[i][metric])/(i+1)

    game_id_to_accum_stats = {}
    for i in range(1, len(gamelogs)):
        game_id_to_accum_stats[gamelogs[i]['GAME_ID']] = \
            {key: gamelogs[i-1][key] for key in gamelogs[i-1] if key in relevant_team_perf_metrics}
    return game_id_to_accum_stats


def main():

    ml_input_data = []
    ml_output_data = []

    years = [2017, 2018] # years to get data for
    for year in years:
        # get all the games in the NBA league for the season
        games = get_league_gamelogs(year)

        # create a map of every team's performance before each one of their games
        team_performance_map = {}
        for team in teams.get_teams():
            print(f'Getting team stats for {team["abbreviation"]}...')
            sleep(1)  # delay before next request to prevent getting temporarily banned from nba api
            team_id = team['id']
            team_gamelogs = get_team_gamelogs_for_season(team_id, year)
            team_gamelogs_accum = accumulate_team_gamelog_stats(team_gamelogs)
            team_performance_map[team_id] = team_gamelogs_accum

        # now, for every game, create an input / output pair to use in the ML model
        # keep list of all seen teams so that we don't use stats for a team that has not played any games yet as input
        seen_teams = set()
        for game in games:
            if game.home_team_id in seen_teams and game.away_team_id in seen_teams:
                # get home team stats
                home_team_data = team_performance_map[game.home_team_id][str(game.game_id)]
                # get away team stats
                away_team_data = team_performance_map[game.away_team_id][str(game.game_id)]
                # save input and expected output
                ml_input_data.append(encode_data(home_team_data, away_team_data))
                ml_output_data.append(1 if game.home_team_won else 0)
            else:
                seen_teams.add(game.home_team_id)
                seen_teams.add(game.away_team_id)

    # now write the input and output to files
    # write input and output to files
    # create directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    # write input to file
    np.save(input_file, np.array(ml_input_data))
    # write output to file
    np.save(output_file, np.array(ml_output_data))


if __name__ == '__main__':
    main()
