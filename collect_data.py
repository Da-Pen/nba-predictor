import os

from nba_api.stats.endpoints import teamgamelogs, teamdashboardbyteamperformance, leaguegamelog
from nba_api.stats.library.parameters import PerModeDetailed
from nba_api.stats.static import teams
from time import sleep
import numpy as np

from constants import data_directory, output_file, input_file, relevant_team_perf_metrics, stats_to_be_averaged
from team_stats import GameOverview
from utils.dates import get_season_start_and_end_dates, start_year_to_season, get_season_for_date

# # directories to write the data files to
# lost_directory = "lost"
# won_directory = "won"


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
# returns the names of the two teams
def get_teams_by_matchup_str(matchup: str):
    s = matchup.split()
    assert len(s) == 3 and s[1] in {'vs.', '@'}
    return s[0], s[2]


def get_league_gamelogs(season_start_year):
    team_ids_map = get_team_abbrev_to_id_map()
    start_date, end_date = get_season_start_and_end_dates(season_start_year)
    gamelogs = reformat_response(leaguegamelog.LeagueGameLog(
        season=start_year_to_season(season_start_year),
        date_from_nullable=start_date,
        date_to_nullable=end_date).league_game_log.get_dict())
    # remove duplicates
    seen_game_ids = set()
    new_gamelogs = []
    for game in gamelogs:
        if game['GAME_ID'] not in seen_game_ids:
            seen_game_ids.add(game['GAME_ID'])
            team1, team2 = get_teams_by_matchup_str(game['MATCHUP'])
            team1_won = (team1 == game['TEAM_ABBREVIATION']) == (game['WL'] == 'W')
            new_gamelogs.append(
                GameOverview(
                    game['GAME_ID'],
                    game['GAME_DATE'],
                    team_ids_map[team1 if team1_won else team2],
                    team_ids_map[team2 if team1_won else team1]))
    return new_gamelogs


'''
# writes the raw (not yet preprocessed) input data for a given team and season to files
def write_inputs_for_season(team_id, season_start_year):
    # get list of all the games and whether they won or lost
    gamelogs = reformat_response(get_team_gamelogs_for_season(team_id, season_start_year))
    for game in gamelogs:
        pass
        # get date of the game
        date = game['GAME_DATE']
        # get this team's stats at that point in time
        team_stats = get_team_perf(team_id, date_to=date)
        # get opponent's stats at that point in time
        # opp
        opp_stats = get_team_perf()



def get_team_perf(team_id, date_to):
    t = teamdashboardbyteamperformance.TeamDashboardByTeamPerformance(
        team_id=team_id,
        date_to_nullable=date_to,
        season=get_season_for_date(date_to),
        per_mode_detailed=PerModeDetailed.per_game)
    return reformat_response(t.overall_team_dashboard.get_dict())[0]
'''

# given a team's data (dict), returns a list that can be saved
def encode_data(team1_data, team2_data):
    # extract relevant data from raw data dict
    # return [team1_data[metric] - team2_data[metric] for metric in relevant_team_perf_metrics]
    return [team1_data[metric] for metric in relevant_team_perf_metrics] + \
        [team2_data[metric] for metric in relevant_team_perf_metrics]

'''
# writes team performance data to file and returns the file names
def write_team_perf_to_files(game_id, winning_team_stats, losing_team_stats):
    # create the directories if they don't exist
    if not os.path.exists(f"{data_directory}/{won_directory}"):
        os.makedirs(f"{data_directory}/{won_directory}")
    if not os.path.exists(f"{data_directory}/{lost_directory}"):
        os.makedirs(f"{data_directory}/{lost_directory}")

    # create winning teams file
    file_name_winning = f"{data_directory}/{won_directory}/{game_id}.npy"
    winning_arr = np.array(encode_data(winning_team_stats, losing_team_stats))
    np.save(file_name_winning, winning_arr)

    # create losing teams file
    file_name_losing = f"{data_directory}/{lost_directory}/{game_id}.npy"
    losing_arr = np.array(encode_data(losing_team_stats, winning_team_stats))
    np.save(file_name_losing, losing_arr)

    return file_name_winning, file_name_losing
'''

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
    team_performance_map = {}
    for team in teams.get_teams():
        print(f'Getting team stats for {team["abbreviation"]}...')
        sleep(1)
        team_id = team['id']
        team_gamelogs = get_team_gamelogs_for_season(team_id, 2018)
        team_gamelogs_accum = accumulate_team_gamelog_stats(team_gamelogs)
        team_performance_map[team_id] = team_gamelogs_accum

    games = get_league_gamelogs(2018)
    # keep list of all seen teams so that we don't use stats for a team that has not played any games yet as input
    seen_teams = set()
    # lists of winning and losing data to use as inputs for the ML model
    winning_input = []
    losing_input = []
    for game in games:
        if game.winning_team_id in seen_teams and game.losing_team_id in seen_teams:
            # get winning team stats
            winning_team_data = team_performance_map[game.winning_team_id][str(game.game_id)]
            # get losing team stats
            losing_team_data = team_performance_map[game.losing_team_id][str(game.game_id)]

            winning_input.append((winning_team_data, losing_team_data))
            losing_input.append((losing_team_data, winning_team_data))
            # winning_team_file, losing_team_file = write_team_perf_to_files(game.game_id, winning_team_stats, losing_team_stats)
            # print('wrote', game, 'to files', winning_team_file, "and", losing_team_file)

        else:
            seen_teams.add(game.winning_team_id)
            seen_teams.add(game.losing_team_id)

    # write input and output to files
    # create directory if it doesn't exist
    if not os.path.exists(data_directory):
        os.makedirs(data_directory)
    # write input to file
    np.save(input_file, np.array([encode_data(team1, team2) for team1, team2 in winning_input + losing_input]))
    # write output to file
    np.save(output_file, np.array([1]*len(winning_input) + [0]*len(losing_input)))


    # team_ids = get_team_abbrev_to_id_map()
    # print(get_team_perf(team_ids['ATL'], "03/10/2020"))
    # print(team_ids)
    # team_gamelogs = get_team_gamelogs_for_season(
    #     team_ids['TOR'],
    #     2019)
    # print(team_gamelogs)

    '''
    print(reformat_response(get_team_perf(team_ids['TOR'], '2020-05-14T00:00:00')))
    
    
    
    games = get_league_gamelogs(2019)
    # keep list of all seen teams so that we don't use stats for a team that has not played any games yet as input
    seen_teams = set()
    for game in games:
        if game.winning_team_id in seen_teams and game.losing_team_id in seen_teams:
            y = yesterday(game.date)
            sleep(0.5)
            # get winning team stats
            winning_team_stats = get_team_perf(game.winning_team_id, y)
            winning_team_file = write_team_perf_to_file(True, game.game_id, winning_team_stats)
            sleep(0.5)
            # get losing team stats
            losing_team_stats = get_team_perf(game.losing_team_id, y)
            losing_team_file = write_team_perf_to_file(False, game.game_id, losing_team_stats)
            print('wrote', game, 'to files', winning_team_file, "and", losing_team_file)
        else:
            seen_teams.add(game.winning_team_id)
            seen_teams.add(game.losing_team_id)
    '''


if __name__ == '__main__':
    main()
