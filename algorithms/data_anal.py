import numpy as np
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score
from sklearn.utils import shuffle
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from util import storage_control
from util import file_util
from flask import g


def analysis(file_path, parameters):
    """
    :param file_path: string
    :param parameters: dict
    :return: the processed file path
    """

    # read file as pandas dataframe, file include column names
    df = pd.read_csv(storage_control.download_to_memory(file_path),
                     header=0)  # header=0 means the first row is column names

    processing_method = parameters['function_name']
    result_name = processing_method

    # read json file as dictionary
    import json
    with open('algorithms/data_anal_para_cfg.json', 'r') as f:
        data_analysis_algorithms_config = json.load(f)

    # get the variable name of the selected function
    variable_name = ''
    for section in data_analysis_algorithms_config:
        for algorithm in section['algorithms']:
            if algorithm['code_name'] == parameters['function_name']:
                for variable in algorithm['variables']:
                    result_name += f'-{parameters[variable["name"]]}'

    result_dict = {"result_name": result_name}

    match processing_method:
        case "knn_classification":
            result_dict["result"] = knn_classification(df, parameters)
        case _:
            pass

    # convert the dictionary to json file
    import json
    result_json = json.dumps(result_dict)
    new_file_path = file_util.add_suffix(file_path=file_path, suffix=result_name, username=g.user.username,
                                         folder_name='analysis_result', ext='.json')
    processed_file_path = storage_control.upload_blob(file=result_json, blob_name=new_file_path)

    return processed_file_path


# def analysis(df, para_received):
#     analytical_method = para_received["analytical_method"]
#     return {
#         "k_nearest_neighbor": k_nearest_neighbor(df, para_received),
#     }.get(analytical_method, None)

def shuffle_dataset(x, y):
    x, y = shuffle(x, y, random_state=0)
    return x, y


def dataset_split(x, y, testing_set_ratio):
    x_train, x_test, y_train, y_test = train_test_split(x, y, test_size=testing_set_ratio, random_state=0)

    return x_train, x_test, y_train, y_test


def get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred):
    # Calculate evaluation metrics
    accuracy_train = accuracy_score(y_train, y_train_pred)
    accuracy_test = accuracy_score(y_test, y_test_pred)

    recall_train = recall_score(y_train, y_train_pred, average='macro')
    recall_test = recall_score(y_test, y_test_pred, average='macro')

    precision_train = precision_score(y_train, y_train_pred, average='macro')
    precision_test = precision_score(y_test, y_test_pred, average='macro')

    f1_train = f1_score(y_train, y_train_pred, average='macro')
    f1_test = f1_score(y_test, y_test_pred, average='macro')

    return accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test


def make_result_dict(evaluation_table, confusion_matrix_table, accuracy):
    # make all the values in evaluation_table and confusion_matrix_table to one dictionary
    evaluation_table = {"accuracy_train": evaluation_table[0], "accuracy_test": evaluation_table[1],
                        "recall_train": evaluation_table[2], "recall_test": evaluation_table[3],
                        "precision_train": evaluation_table[4], "precision_test": evaluation_table[5],
                        "f1_train": evaluation_table[6], "f1_test": evaluation_table[7]}
    confusion_matrix_table = {"confusion_matrix_table": confusion_matrix_table.to_json(orient='split')}
    accuracy = {"accuracy": accuracy}

    # combine all the dictionaries into one dictionary
    result_dict = {**evaluation_table, **confusion_matrix_table, **accuracy}

    return result_dict


def cross_validation(x, y, model, k):
    # Initialize result table
    evaluation_table = []
    confusion_matrix_table = []
    accuracy = []
    kf = KFold(n_splits=k, shuffle=True, random_state=0)
    for train_index, test_index in kf.split(x):
        x_train, x_test = x.iloc[train_index], x.iloc[test_index]
        y_train, y_test = y.iloc[train_index], y.iloc[test_index]
        model.fit(x_train, y_train)
        y_train_pred = model.predict(x_train)
        y_test_pred = model.predict(x_test)
        # Calculate evaluation metrics
        accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test = \
            get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred)

        # Compute confusion matrix
        cnf_matrix = confusion_matrix(y_test, y_test_pred)

        # Append results to result table and confusion matrix table
        evaluation_table.append(
            [accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test,
             f1_train, f1_test])
        confusion_matrix_table.append(cnf_matrix)

        accuracy.append(model.score(x_test, y_test))

    # get the average of evaluation_table, confusion_matrix_table and accuracy
    evaluation_table = np.array(evaluation_table)
    evaluation_table = np.mean(evaluation_table, axis=0)
    confusion_matrix_table = np.array(confusion_matrix_table)
    confusion_matrix_table = pd.DataFrame(np.mean(confusion_matrix_table, axis=0))
    accuracy = np.array(accuracy)
    accuracy = np.mean(accuracy, axis=0)

    # make all the values in evaluation_table and confusion_matrix_table to one dictionary
    result_dict = make_result_dict(evaluation_table, confusion_matrix_table, accuracy)

    return result_dict


def knn_classification(df, parameters):
    result_dict = {}
    neigh = KNeighborsClassifier(n_neighbors=int(parameters["n_neighbors"]), weights=parameters["weights"],
                                 algorithm=parameters["algorithm"], leaf_size=int(parameters["leaf_size"]),
                                 p=int(parameters["p"]))

    # slice the dataframe according to the features selected by the user
    x_train = df[parameters["features"]]
    y_train = df[parameters["target"]]

    if parameters["shuffle"] == "True":
        x_train, y_train = shuffle_dataset(x_train, y_train)

    if parameters["cross_validation"] == "None":
        x_train, x_test, y_train, y_test = dataset_split(x_train, y_train, 1 - float(parameters["train_ratio"]))
        neigh.fit(x_train, y_train)

        y_train_pred = neigh.predict(x_train)
        y_test_pred = neigh.predict(x_test)

        # Calculate evaluation metrics
        accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test = \
            get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred)

        # Compute confusion matrix
        cnf_matrix = pd.DataFrame(confusion_matrix(y_test, y_test_pred))

        # get the accuracy
        accuracy = neigh.score(x_test, y_test)

        # make all the values in result_table and confusion_matrix_table to one dictionary
        evaluation_table = [accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test,
                            f1_train, f1_test]
        result_dict = make_result_dict(evaluation_table, cnf_matrix, accuracy)
    else:
        result_dict = cross_validation(x_train, y_train, neigh,
                                       int(parameters["cross_validation"].split("-", 1)[0]))  # k-fold

    return result_dict


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
