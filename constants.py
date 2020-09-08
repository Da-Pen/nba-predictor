data_directory = "data"
input_file = f'{data_directory}/input.npy'
output_file = f'{data_directory}/output.npy'

# relevant_team_perf_metrics_v2 = [
#     'GP', 'W', 'L', 'W_PCT', 'MIN', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE',
#     'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 'GP_RANK', 'W_RANK',
#     'L_RANK', 'W_PCT_RANK', 'MIN_RANK', 'OFF_RATING_RANK', 'DEF_RATING_RANK', 'NET_RATING_RANK',
#     'AST_RATIO_RANK', 'OREB_PCT_RANK', 'DREB_PCT_RANK', 'REB_PCT_RANK', 'TM_TOV_PCT_RANK', 'PACE_RANK'
# ]

relevant_team_perf_metrics_v2 = [
    'W_PCT', 'OFF_RATING', 'DEF_RATING', 'NET_RATING', 'PACE',
    'AST_RATIO', 'OREB_PCT', 'DREB_PCT', 'REB_PCT', 'TM_TOV_PCT', 'W_PCT_RANK', 'OFF_RATING_RANK',
    'DEF_RATING_RANK', 'NET_RATING_RANK', 'AST_RATIO_RANK', 'OREB_PCT_RANK', 'DREB_PCT_RANK', 'REB_PCT_RANK',
    'TM_TOV_PCT_RANK', 'PACE_RANK'
]


# list of items where we want to remove the 'W_' and 'E_' prefixes to normalise the data across both conferences
keys_to_remove_prefixes_from = [
    'E_OFF_RATING', 'E_DEF_RATING', 'E_NET_RATING', 'E_PACE', 'E_AST_RATIO', 'E_OREB_PCT', 'E_DREB_PCT',
    'E_REB_PCT', 'E_TM_TOV_PCT', 'E_OFF_RATING_RANK', 'E_DEF_RATING_RANK', 'E_NET_RATING_RANK',
    'E_AST_RATIO_RANK', 'E_OREB_PCT_RANK', 'E_DREB_PCT_RANK', 'E_REB_PCT_RANK', 'E_TM_TOV_PCT_RANK', 'E_PACE_RANK',
    'W_OFF_RATING', 'W_DEF_RATING', 'W_NET_RATING', 'W_PACE', 'W_AST_RATIO', 'W_OREB_PCT', 'W_DREB_PCT',
    'W_REB_PCT', 'W_TM_TOV_PCT', 'W_OFF_RATING_RANK', 'W_DEF_RATING_RANK', 'W_NET_RATING_RANK',
    'W_AST_RATIO_RANK', 'W_OREB_PCT_RANK', 'W_DREB_PCT_RANK', 'W_REB_PCT_RANK', 'W_TM_TOV_PCT_RANK', 'W_PACE_RANK'
]