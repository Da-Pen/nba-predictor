from nba_api.stats.static import teams


def get_team_id_to_abbrev_map():
    return {t['id']: t['abbreviation'] for t in teams.get_teams()}


class GameOverview:
    def __init__(self, game_id, date, winning_team_id, losing_team_id):
        self.game_id = game_id
        self.date = date
        self.winning_team_id = winning_team_id
        self.losing_team_id = losing_team_id

    def __str__(self):
        m = get_team_id_to_abbrev_map()
        return m[self.winning_team_id] + " beat " + m[self.losing_team_id] + " on " + self.date

'''
class TeamStats:
    def __init__(self, stats):
        self.gp = stats['GP']
        self.wins = stats['W']
        self.losses = stats['L']
        self.win_pct = stats['W_PCT']
        self.fgm = stats['FGM']      # field goals made
        self.fga = stats['FGA']      # field goals attempted
        self.fg_pct = stats['FG_PCT']
        self.fg3m = stats['FG3M']    # 3pt made
        self.fg3a = stats['FG3A']
        self.ftm = stats['FTM']
        self.fta = stats['FTA']
        self.oreb = stats['OREB']
        self.dreb = stats['DREB']
        self.ast = stats['AST']
        self.tov = stats['TOV']
        self.stl = stats['STL']
        self.blk = stats['BLK']
        self.blka = stats['BLKA']
        self.pf = stats['PF']  # personal fouls
        self.pfd = stats['PFD']  # personal fouls drawn
        self.pts = stats['PTS']
        self.pm = stats['PLUS_MINUS']
'''
