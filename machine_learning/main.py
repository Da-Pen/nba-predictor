import tensorflow as tf
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
from tensorflow.python.keras.wrappers.scikit_learn import KerasClassifier

from constants import input_file, output_file, relevant_team_perf_metrics


def baseline_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(
            units=len(relevant_team_perf_metrics)/4,
            input_dim=len(relevant_team_perf_metrics)*2,
            activation='relu'),
        tf.keras.layers.Dense(units=1, activation='sigmoid')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    return model


def main():
    batch_size = 32
    input_arr = np.load('../' + input_file)
    output_arr = np.load('../' + output_file)

    # shuffle the numpy arrays so that the validation set doesn't only include losing games
    # p = np.random.permutation(len(input_arr))
    # input_arr = input_arr[p]
    # output_arr = output_arr[p]

    # evaluate baseline model with standardized dataset
    estimators = [
        ('standardize', StandardScaler()),
        ('mlp', KerasClassifier(build_fn=baseline_model, epochs=10, batch_size=batch_size, verbose=0))
    ]
    pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(pipeline, input_arr, output_arr, cv=kfold)
    print("Standardized: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))


if __name__ == '__main__':
    main()
