import numpy as np

from constants import input_file, output_file


if __name__ == '__main__':
    input_arr = np.load('../' + input_file)
    output_arr = np.load('../' + output_file)
    # for input, output in zip(input_arr, output_arr):

        
