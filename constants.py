data_directory = "data"
input_file = f'{data_directory}/input.npy'
output_file = f'{data_directory}/output.npy'

# list of team performance metrics that are relevant to determining the team's ability to win the next game
relevant_team_perf_metrics = [
    'W', 'L', 'W_PCT', 'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA',
    'FT_PCT', 'OREB', 'DREB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PLUS_MINUS'
]

# list of metrics to be averaged when accumulating stats for a team
stats_to_be_averaged = [
    'FGM', 'FGA', 'FG_PCT', 'FG3M', 'FG3A', 'FG3_PCT', 'FTM', 'FTA', 'FT_PCT', 'OREB',
    'DREB', 'AST', 'TOV', 'STL', 'BLK', 'BLKA', 'PF', 'PFD', 'PTS', 'PLUS_MINUS'
]