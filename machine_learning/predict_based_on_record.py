import numpy as np

from constants import input_file, output_file, relevant_team_perf_metrics

if __name__ == '__main__':
    input_arr = np.load('../' + input_file)
    output_arr = np.load('../' + output_file)
    num_correct = 0
    for input, output in zip(input_arr, output_arr):
        home_team_win_pct = input[relevant_team_perf_metrics.index('W_PCT')]
        away_team_win_pct = input[len(input)//2 + relevant_team_perf_metrics.index('W_PCT')]
        if (home_team_win_pct > away_team_win_pct and output == 1) or \
            (home_team_win_pct <= away_team_win_pct and output == 0):
            num_correct += 1
    print(f'If we predict the game outcome solely on which team has a better winrate, ' +
          f'we would be correct {100*num_correct/len(input_arr)}% of the time.')
