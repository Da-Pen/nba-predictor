from nba_api.stats.static import teams

'''
This file defines a GameOverview object which represents the basic info of an nba game
'''

def get_team_id_to_abbrev_map():
    return {t['id']: t['abbreviation'] for t in teams.get_teams()}


class GameOverview:
    def __init__(self, game_id: str, date, home_team_id: int, away_team_id: int, home_team_won: bool):
        self.game_id = game_id
        self.date = date
        self.home_team_id = home_team_id
        self.away_team_id = away_team_id
        self.home_team_won = home_team_won

    def __str__(self):
        m = get_team_id_to_abbrev_map()
        return m[self.away_team_id] + " @ " + m[self.away_team_id] + " on " + self.date