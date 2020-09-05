import tensorflow as tf
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from tensorflow.keras.layers.experimental.preprocessing import Normalization
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
    p = np.random.permutation(len(input_arr))
    input_arr = input_arr[p]
    output_arr = output_arr[p]

    # normalizer = Normalization(axis=-1)
    # normalizer.adapt(input_arr)
    # input_arr = normalizer(input_arr)

    # evaluate model with standardized dataset
    # estimator = KerasClassifier(build_fn=baseline_model, epochs=10, batch_size=batch_size, verbose=0)
    # kfold = StratifiedKFold(n_splits=10, shuffle=True)
    # results = cross_val_score(estimator, input_arr, output_arr, cv=kfold)
    # print("Baseline: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))

    # evaluate baseline model with standardized dataset
    estimators = [
        ('standardize', StandardScaler()),
        ('mlp', KerasClassifier(build_fn=baseline_model, epochs=10, batch_size=batch_size, verbose=0))
    ]
    pipeline = Pipeline(estimators)
    kfold = StratifiedKFold(n_splits=10, shuffle=True)
    results = cross_val_score(pipeline, input_arr, output_arr, cv=kfold)
    print("Standardized: %.2f%% (%.2f%%)" % (results.mean() * 100, results.std() * 100))

    # for i in range(1500, 1510):
    #     print(input_arr[i], output_arr[i])

    # model.compile(optimizer=tf.keras.optimizers.Adam(), loss='binary_crossentropy', metrics=['accuracy'])
    # model.fit(x=input_arr, y=output_arr, validation_split=0.15, batch_size = batch_size, epochs=30, verbose=2, shuffle=False)
    #
    # predictions = model.predict(x=input_arr, batch_size=batch_size)
    # print(predictions)
    # rounded_predictions = np.argmin(predictions, axis=-1)
    # correct_predictions = 0
    # for i in range(len(predictions)):
    #     if rounded_predictions[i] == output_arr[i]:
    #         correct_predictions += 1
    # print(f'correct predictions percentage: {correct_predictions/len(predictions)}')




if __name__ == '__main__':
    main()
