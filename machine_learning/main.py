import tensorflow as tf
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
import numpy as np
from tensorflow.python.keras.wrappers.scikit_learn import KerasClassifier

from constants import input_file, output_file, relevant_team_perf_metrics, relevant_team_perf_metrics_v2


def baseline_model():
    model = tf.keras.Sequential([
        tf.keras.layers.Dense(
            units=(len(relevant_team_perf_metrics) + len(relevant_team_perf_metrics_v2))*2,
            input_dim=(len(relevant_team_perf_metrics) + len(relevant_team_perf_metrics_v2))*2,
            activation='relu'),
        tf.keras.layers.Dense(units=1, activation='sigmoid')
    ])
    model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    return model


def main():
    # hyperparameters
    batch_size = 32
    epochs = 10
    # max number of training sets to train on. Used to check at which point more data doesn't result in a better model.
    # -1 for no cap.
    training_data_cap = -1

    input_arr = np.load('../' + input_file)
    output_arr = np.load('../' + output_file)
    if training_data_cap != -1:
        input_arr = input_arr[:training_data_cap]
        output_arr = output_arr[:training_data_cap]

    # evaluate baseline model with standardized dataset
    estimators = [
        ('standardize', StandardScaler()),
        ('mlp', KerasClassifier(build_fn=baseline_model, epochs=epochs, batch_size=batch_size, verbose=0))
    ]
    pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(pipeline, input_arr, output_arr, cv=kfold)
    print("Standardized: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))


if __name__ == '__main__':
    main()
