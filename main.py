# This is a sample Python script.

# Press ⌃R to execute it or replace it with your code.
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from nba_api.stats.endpoints import teamdashboardbylastngames
from nba_api.stats.endpoints import teamdashboardbyteamperformance
from nba_api.stats.endpoints import teamgamelogs
from nba_api.stats.endpoints import teamgamelog
from nba_api.stats.static import teams

from utils.dates import get_season_for_date, get_season_start_and_end_dates
from utils.dates import start_year_to_season


# get team performance of last 20 regular season games
def get_team_by_last_n_games(team_id, opponent_team_id=0, date_to=''):
    t = teamdashboardbylastngames.TeamDashboardByLastNGames(
        team_id=team_id,
        opponent_team_id=opponent_team_id,
        date_to_nullable=date_to,
        season=get_season_for_date(date_to)
    )
    return t.last20_team_dashboard.get_dict()


def get_team_perf(team_id):
    t = teamdashboardbyteamperformance.TeamDashboardByTeamPerformance(team_id=team_id)
    return t.overall_team_dashboard.get_dict()


def dict_from_resp(response_dict):
    return [dict(zip(response_dict['headers'], data)) for data in response_dict['data']]


def get_all_team_ids():
    return {t['nickname']: t['id'] for t in teams.get_teams()}


def get_team_gamelogs(team_id, season="", date_from="", date_to=""):
    t = teamgamelogs.TeamGameLogs(team_id_nullable=team_id,
                                  season_nullable=season,
                                  date_from_nullable=date_from,
                                  date_to_nullable=date_to)
    return t.team_game_logs.get_dict()


def get_team_gamelogs_for_season(team_id, season_start_year):
    start_date, end_date = get_season_start_and_end_dates(season_start_year)
    return get_team_gamelogs(team_id,
                             start_year_to_season(season_start_year),
                             start_date,
                             end_date)


if __name__ == '__main__':
    team_ids = get_all_team_ids()
    # print(team_ids, "\n")
    # print(dict_from_resp(get_team_by_last_n_games(team_ids['Raptors'], date_to='08/26/2000')))
    team_gamelogs = get_team_gamelogs_for_season(
            team_ids['Raptors'],
            2019
        )
    print(dict_from_resp(team_gamelogs))

