import numpy as np
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
from sklearn.utils import shuffle
import seaborn as sns
import matplotlib.pyplot as plt


def analysis(df, para_received):
    analytical_method = para_received["analytical_method"]
    return {
        "k_nearest_neighbor": k_nearest_neighbor(df, para_received),
    }.get(analytical_method, None)


def chebyshev_distances(x, y):
    x = np.array(x)
    y = np.array(y)
    diff = np.abs(x - y)
    distance = np.max(diff)
    return distance


def k_nearest_neighbor(df, para_received):
    dependent_variable = para_received["dependent_variable_y"]
    independent_variables = para_received["independent_variable_x"]
    data_shuffling = para_received["data_shuffling"]
    testing_set_ratio = para_received["testing_set_ratio"]
    cross_validation = para_received["cross_validation"]
    k = para_received["number_of_neighbors"]
    vector_distance_algorithm = para_received["vector_distance_algorithm"]
    search_algorithm = para_received["search_algorithm"]
    weighting_function_of_nearest_neighbors = para_received["weighting_function_of_nearest_neighbors"]

    df = df.dropna()  # remove rows with missing values
    x = df[independent_variables].values  # extract independent variables
    y = df[dependent_variable].values  # extract dependent variable
    label_encoder = LabelEncoder()
    y = label_encoder.fit_transform(y)  # convert dependent variable to numerical label

    # shuffle the data
    if data_shuffling == "true":
        x, y = shuffle(x, y, random_state=42)

    # cross validation
    if cross_validation == "false":

        # split data into training and testing sets
        x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=testing_set_ratio)

        # calculate distances between test instances and training instances
        if vector_distance_algorithm == "euclidean":
            distances = euclidean_distances(x_test, x_train)
        elif vector_distance_algorithm == "manhattan":
            distances = manhattan_distances(x_test, x_train)
        elif vector_distance_algorithm == "chebyshev":
            distances = chebyshev_distances(x_test, x_train)

        # get k nearest neighbors for each test instance
        k_nearest_indices = np.argsort(distances, axis=1)[:, :k]

        # make predictions for test instances based on k nearest neighbors
        y_pred = []
        for indices in k_nearest_indices:
            labels = y_train[indices]
            counts = np.bincount(labels)
            y_pred.append(np.argmax(counts))

        # convert predicted labels back to original format
        y_pred = label_encoder.inverse_transform(y_pred)

    else:

        # perform k-fold cross-validation
        kf = KFold(n_splits=cross_validation)
        y_pred = []
        for train_index, test_index in kf.split(x):
            x_train, x_test = x[train_index], x[test_index]
            y_train, y_test = y[train_index], y[test_index]

            # calculate distances between test instances and training instances
            if vector_distance_algorithm == "euclidean":
                distances = euclidean_distances(x_test, x_train)
            elif vector_distance_algorithm == "manhattan":
                distances = manhattan_distances(x_test, x_train)
            elif vector_distance_algorithm == "chebyshev":
                distances = chebyshev_distances(x_test, x_train)

            # get k nearest neighbors for each test instance
            k_nearest_indices = np.argsort(distances, axis=1)[:, :k]

            # make predictions for test instances based on k nearest neighbors
            y_pred_fold = []
            for indices in k_nearest_indices:
                labels = y_train[indices]
                counts = np.bincount(labels)
                y_pred_fold.append(np.argmax(counts))

            # convert predicted labels back to original format
            y_pred_fold = label_encoder.inverse_transform(y_pred_fold)
            y_pred.extend(y_pred_fold)

    # create confusion matrix
    confusion_matrix = np.zeros((len(label_encoder.classes_), len(label_encoder.classes_)))
    for actual, predicted in zip(y_test, y_pred):
        confusion_matrix[actual][predicted] += 1

    # normalize confusion matrix
    confusion_matrix_norm = confusion_matrix.astype('float') / confusion_matrix.sum(axis=1)[:, np.newaxis]

    # plot heatmap
    sns.heatmap(confusion_matrix_norm, cmap="YlGnBu", annot=True, fmt=".2f", xticklabels=label_encoder.classes_,
                yticklabels=label_encoder.classes_)
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.title("Confusion Matrix")

    return y_pred
