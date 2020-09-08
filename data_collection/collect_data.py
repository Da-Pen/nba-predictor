import os

from nba_api.stats.endpoints import teamgamelogs, leaguegamelog, teamestimatedmetrics
from nba_api.stats.static import teams
from time import sleep
import numpy as np

from constants import data_directory, output_file, input_file, keys_to_remove_prefixes_from, relevant_team_perf_metrics_v2
from game_overview import GameOverview
from utils.dates import get_season_start_and_end_dates, start_year_to_season


# converts a list of headers and data into a map of header:data
def reformat_response(response_dict):
    return [dict(zip(response_dict['headers'], data)) for data in response_dict['data']]


def get_team_abbrev_to_id_map():
    return {t['abbreviation']: t['id'] for t in teams.get_teams()}


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
    return [home_team_data[metric] for metric in relevant_team_perf_metrics_v2] + \
        [away_team_data[metric] for metric in relevant_team_perf_metrics_v2]



def remove_east_west_prefixes(d):
    d_copy = d.copy() # have to make a copy to prevent errors when modifying dict while looping over its keys
    for key in d_copy:
        if key in keys_to_remove_prefixes_from:
            d[key[2:]] = d.pop(key)


# gets the estimated metrics (offensive rating, defensive rating, etc.) for all teams for a given year
def get_team_estimated_metrics(season_start_year):
    t = teamestimatedmetrics.TeamEstimatedMetrics(season=start_year_to_season(season_start_year))
    all_teams_data = reformat_response(t.team_estimated_metrics.get_dict())
    all_teams_data_dict = {}
    for team_data in all_teams_data:
        all_teams_data_dict[team_data['TEAM_ID']] = {k: team_data[k] for k in team_data if k not in {'TEAM_ID', 'TEAM_NAME'}}
        remove_east_west_prefixes(all_teams_data_dict[team_data['TEAM_ID']])
    return all_teams_data_dict


def main():

    ml_input_data = []
    ml_output_data = []

    years = range(2017, 2020)  # years to get data for
    for year in years:
        print(f'Collecting data for season {start_year_to_season(year)}...')
        sleep(1)
        # get all the games in the NBA league for the season
        games = get_league_gamelogs(year)

        team_estimated_metrics = get_team_estimated_metrics(year)

        # now, for every game, create an input / output pair to use in the ML model
        # keep list of all seen teams so that we don't use stats for a team that has not played any games yet as input
        seen_teams = set()
        for game in games:
            if game.home_team_id in seen_teams and game.away_team_id in seen_teams:
                # get home team stats
                # home_team_data = team_performance_map[game.home_team_id][str(game.game_id)]
                # # get away team stats
                # away_team_data = team_performance_map[game.away_team_id][str(game.game_id)]
                # # save input and expected output
                home_team_data = team_estimated_metrics[game.home_team_id]
                away_team_data = team_estimated_metrics[game.away_team_id]
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