import numpy as np
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics.pairwise import euclidean_distances, manhattan_distances
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score
from sklearn.svm import SVR
from sklearn.utils import shuffle
import seaborn as sns
import pandas as pd
from scipy import stats
from scipy.stats import skew, kurtosis
import psython as psy
import pingouin as pg
import statsmodels.api as sm
import matplotlib.pyplot as plt
import matplotlib.font_manager as font_manager
from util import storage_control
from util import file_util
from flask import g
import json
import io
import base64


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
    with open('algorithms/data_anal_para_cfg.json', 'r', encoding='utf-8') as f:
        data_analysis_algorithms_config = json.load(f)

    # get the variable name of the selected function
    variable_name = ''
    for section in data_analysis_algorithms_config:
        for algorithm in section['algorithms']:
            if algorithm['code_name'] == parameters['function_name']:
                for variable in algorithm['variables']:
                    result_name += f'-{parameters[variable["name"]]}'

    result_dict = {"name": result_name}

    # Define dictionary mapping method names to functions
    method_dict = {
        'knn_classification': knn_classification,
        'normality_test': normality_test,
        'reliability_analysis': reliability_analysis,
        'svm_classification': svm_classification
    }

    # Call the corresponding function
    if processing_method in method_dict:
        result_dict['content'] = method_dict[processing_method](df, parameters)
    else:
        # Default behavior
        pass

    # convert the dictionary to json file
    result_json = json.dumps(result_dict)
    new_file_path = file_util.add_suffix(file_path=file_path, suffix=result_name, username=g.user.username,
                                         folder_name='analysis_result', ext='.json')
    processed_file_path = storage_control.upload_blob(file=result_json, blob_name=new_file_path)

    return processed_file_path


def reliability_analysis(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "There is currently no uniform standard for the analysis of Cronbach's α coefficient (or half coefficient), but according to the views of most scholars, generally if the Cronb's α coefficient (or half coefficient) is above 0.9, the reliability of the test or scale is very good , between 0.8-0.9 means the reliability is good, between 0.7-0.8 means the reliability is acceptable, between 0.6-0.7 means the reliability is average, between 0.5-0.6 means the reliability is not ideal, if it is below 0.5 Consider reorganizing the questionnaire.",
                                                  "Carry out further analysis on the item summary statistics table to see which items lead to the decline of the overall reliability. If the value of the 'correlation between the corrected item and the total' is lower than 0.3, or the value of α coefficient after deleting the item significantly higher than the α coefficient, you can consider removing this topic at this time."
                                              ]))

    result_content.append(make_result_section(section_name="Detailed conclusions",
                                              content_type="text",
                                              content=''))

    # here variable_names is the array of variables
    variable_names = parameters["variables"]
    # new_df  includes the columns need to conduct reliablity analysis
    new_df = df.loc[:, variable_names]
    cronbach_alpha_result = pg.cronbach_alpha(data=new_df)
    # the format of cronbach_alpha_result is   (0.7734375, array([0.336, 0.939]))

    Cronbach_alpha_coefficient = cronbach_alpha_result[0]
    column_size = len(variable_names)
    sample_size = len(df)

    evaluation_table = [Cronbach_alpha_coefficient, column_size, sample_size]

    result_content.append(make_result_section(section_name="Output 1: overall description of the results",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      ['%.3f' % (evaluation_table[0]),
                                                       evaluation_table[1],
                                                       evaluation_table[2],
                                                       ]
                                                  ],
                                                  "columns": ["Cronbach's alpha coefficient",
                                                              "number of items",
                                                              "sample size"
                                                              ],
                                                  "index": ["data"]
                                              }))



    result_content.append(make_result_section(section_name="Table description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table shows the results of the Cronbach's α coefficient of the model, including the Cronbach's α coefficient value, the number of items, and the number of samples, which are used to measure the reliability quality level of the data.",
                                                  "Cronbach's α coefficient value: Evaluate whether the collected data is true and reliable, and check out unreasonable or random answers based on this.",
                                                  "Number of items: The number of variables involved in the calculation of reliability analysis."
                                              ]))

    result_content.append(make_result_section(section_name="Low score suggestion:",
                                              content_type="ordered_list",
                                              content=[
                                                  "Check whether your questions are reasonable and whether they cause misunderstanding and confusion to the respondent.",
                                                  "Check each answer sheet, and you can eliminate answer sheets with poor quality answers.",
                                                  "Remove or add some scale items for re-analysis."
                                              ]))

    the_Cronbach, if_deleted_table = psy.cronbach_alpha_scale_if_deleted(df)

    table_data = []
    for index, row in if_deleted_table.iterrows():
        row_data = list(row)
        table_data.append(row_data)

    num_rows = if_deleted_table.shape[0]
    row_nums = list(range(1, num_rows + 1))

    result_content.append(make_result_section(section_name="Output 2: delete the statistical summary of the analysis item",
                                              content_type="table",
                                              content={
                                                  "data": table_data,
                                                  "columns": ["Item",
                                                              "Scale Mean if Item Deleted",
                                                              "Scale Variance if Item Deleted",
                                                              "Corrected Item-Total Correlation",
                                                              "Cronbach's Alpha if Item Deleted"
                                                              ],
                                                  "index": row_nums
                                              }))

    result_content.append(make_result_section(section_name="Table description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table shows the statistical results of the items of the model. Through the control variable method, the correlation and Cronbach's α coefficient and other indicators before and after deleting a certain item are compared to assist in judging whether the scale item should be corrected.",
                                                  "Generally, first judge whether the overall correlation after item deletion is less than 0.3, and if it is satisfied, then determine whether the α coefficient after item deletion is greater than the original coefficient. If all are not satisfied, it can be considered that the item is in good condition, otherwise it needs to be checked.",

                                              ]))

    return result_content



def normality_test(df, parameters):
    result_content = []
    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Perform the Shapiro-Wilk (small data sample, generally less than 5000 samples) or Kolmogorov–Smirnov (large data sample, generally more than 5000 samples) test on the data to check its significance.",
                                                  "If it does not show significance (P>0.05), it means that it conforms to the normal distribution, otherwise it means that it does not conform to the normal distribution (PS: Usually it is difficult to meet the test in real research situations, if the absolute value of the sample kurtosis is less than 10 and the skewness The absolute value is less than 3, combined with the normal distribution histogram, PP diagram or QQ diagram, it can be described as basically conforming to the normal distribution)."
                                              ]))

    df[parameters["variable"]] = df[parameters["variable"]].astype(float)
    variable_name = parameters["variable"]
    sample_size = len(df[parameters["variable"]])
    median = df[parameters["variable"]].median()
    mean = df[parameters["variable"]].mean()
    std = df[parameters["variable"]].std()
    skewness = skew(df[parameters["variable"]])
    kurtosis = df[parameters["variable"]].kurt()

    shapiro_test = stats.shapiro(df[parameters["variable"]])
    # shapiro_test is the format of ShapiroResult(statistic=0.9813305735588074, pvalue=0.16855233907699585)
    shapiro_statistic = shapiro_test.statistic
    shapiro_pvalue = shapiro_test.pvalue
    shapiro_result = '{}({})'.format(shapiro_statistic, shapiro_pvalue)

    ks_test = stats.kstest(df[parameters["variable"]], stats.norm.cdf)
    # ks_test is the format of KstestResult(statistic=0.17482387821055168, pvalue=0.001913921057766743)
    ks_statistic = ks_test.statistic
    ks_pvalue = ks_test.pvalue
    ks_result = '{}({})'.format(ks_statistic, ks_pvalue)

    result_content.append(make_result_section(section_name="Detailed conclusions",
                                              content_type="text",
                                              content=''))

    evaluation_table = [variable_name, sample_size, median, mean, std, skewness, kurtosis, shapiro_result, ks_result]
    result_content.append(make_result_section(section_name="Output 1: overall description of the results",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      [evaluation_table[0],
                                                       evaluation_table[1],
                                                       '%.3f' % (evaluation_table[2]),
                                                       '%.3f' % (evaluation_table[3]),
                                                       '%.3f' % (evaluation_table[4]),
                                                       '%.3f' % (evaluation_table[5]),
                                                       '%.3f' % (evaluation_table[6]),
                                                       evaluation_table[7],
                                                       evaluation_table[8],
                                                       ],
                                                  ],
                                                  "columns": ['variable name', 'sample size', 'median', 'mean', 'std',
                                                              'skewness', 'kurtosis', 'S-W test (statistics/pvalue)',
                                                              'K-S test (statistics/pvalue)'
                                                              ],
                                                  "index": ["data"]
                                              }))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table shows the results of Q1 descriptive statistics and normality test, including median, mean, etc., which are used to test the normality of the data.",
                                                  "Usually there are two normal distribution test methods, one is the Shapiro-Wilk test, which is suitable for small sample data (sample size ≤ 5000); the other is the Kolmogorov–Smirnov test, which is suitable for large sample data (sample size >5000).",
                                                  "If it is significant (P<0.05), it means that the null hypothesis is rejected (the data conforms to the normal distribution), and the data does not satisfy the normal distribution; otherwise, it means that the data conforms to the normal distribution."
                                              ]))

    # create histogram to visualize values in dataset
    histogram_pic = make_histogram_pic(df[parameters["variable"]], variable_name)

    result_content.append(make_result_section(section_name="Output 2: normality test histogram",
                                              content_type="img",
                                              content=histogram_pic
                                              ))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content="The figure above shows the normality test histogram of the Q1 data. If the normality chart is basically bell-shaped (high in the middle and low at both ends), it means that although the data is not absolutely normal, it is basically acceptable as a normal distribution."
                                              ))

    pp_pic = make_pp_plot(df[parameters["variable"]])
    result_content.append(make_result_section(section_name="Output 3: P-P Plot",
                                              content_type="img",
                                              content=pp_pic
                                              ))
    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content="The figure above shows the fitting situation between the cumulative probability (P) of Q1 calculation observation and the normal cumulative probability (P). The higher the degree of fitting, the more it obeys the normal distribution."
                                              ))

    qq_pic = make_qq_plot(df[parameters["variable"]])
    result_content.append(make_result_section(section_name="Output 4: Q-Q Plot",
                                              content_type="img",
                                              content=qq_pic
                                              ))
    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content="Q-Q diagram, the full name is 'Quantile Quantile Plot'. Compare the probability distributions of different quantiles of the observed value and the predicted value (assuming normal distribution) in a graphical way, so as to test whether it is consistent with the normal distribution law. And the actual data is used as the X-axis, and the quantile of the data when it is assumed to be normal is used as the Y-axis to make a scatter diagram. The higher the coincidence between the scatter point and the straight line, the more it obeys the normal distribution, and the larger the difference between the scatter points, the more it does not obey the normal state. The distribution depends on the actual situation."
                                              ))

    return result_content





def make_histogram_pic(column, variable):
    """
    Make the picture of histogram
    :param column: column to make the histogram
    :return: A string represents histogram picture in form of base64
    """

    # plot histogram and density curve
    f = plt.figure()
    fig, ax = plt.subplots()
    ax.hist(column, edgecolor='black', bins=20, density=True)
    ax.set_xlabel(variable)
    ax.set_ylabel("Density")
    ax.set_title("Histogram")

    kde = np.linspace(column.min(), column.max(), 100)
    kde_smooth = stats.gaussian_kde(column)(kde)
    ax.plot(kde, kde_smooth)

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    f.clear()
    plt.close()

    return base64_pic


def make_pp_plot(column):
    """
    Make the picture of P-P plot
    :param column: column to make the P-P plot
    :return: A string represents P-P plot in form of base64
    """

    # plot P-P plot
    fig, ax = plt.subplots()
    stats.probplot(column, dist="norm", plot=ax)
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")
    ax.set_title("P-P Plot")

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    plt.close()

    return base64_pic


def make_qq_plot(column):
    """
    Make the picture of Q-Q plot
    :param column: column to make the Q-Q plot
    :return: A string represents Q-Q plot in form of base64
    """

    # plot Q-Q plot
    fig, ax = plt.subplots()
    sm.ProbPlot(column).qqplot(line='s', ax=ax)
    ax.set_xlabel("Theoretical quantiles")
    ax.set_ylabel("Sample quantiles")
    ax.set_title("Q-Q Plot")

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.flush()
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    plt.close()

    return base64_pic


# def analysis(df, para_received):
#     analytical_method = para_received["analytical_method"]
#     return {
#         "k_nearest_neighbor": k_nearest_neighbor(df, para_received),
#     }.get(analytical_method, None)

def shuffle_dataset(x, y):
    x, y = shuffle(x, y, random_state=0)
    return x, y


# test_size is the proportion of the test set in the data set
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


def make_heatmap_pic(cnf_matrix, labels=None):
    """
    Make the picture of heatmap
    :param cnf_matrix: Confusion matrix
    :param labels: Specified labels shown in heatmap. Values of classification labels by default
    :return: A string represents heatmap picture in form of base64
    """
    # Confusion matrix and label process
    confusion_matrix_norm = cnf_matrix.astype('float') / cnf_matrix.sum(axis=1)[:, np.newaxis]
    if not labels:
        labels = list(cnf_matrix.columns.values)

    # plot heatmap
    f = plt.figure()
    sns.heatmap(confusion_matrix_norm, cmap="YlGnBu", annot=True, fmt=".2f", xticklabels=labels, yticklabels=labels)
    plt.xlabel("Predicted Label")
    plt.ylabel("Actual Label")
    plt.title("Heatmap")

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    f.clear()
    plt.close()

    return base64_pic


def make_result_section(section_name, content_type, content):
    result_section_dict = {
        "section_name": section_name,
        "type": content_type,
        "content": content
    }

    return result_section_dict


def make_result_dict(evaluation_table=None, confusion_matrix_table=None, accuracy=None):
    result_dict = {}
    # make all the values in evaluation_table and confusion_matrix_table to one dictionary
    if evaluation_table:
        result_dict["evaluation_table"] = {"accuracy_train": evaluation_table[0], "accuracy_test": evaluation_table[1],
                                           "recall_train": evaluation_table[2], "recall_test": evaluation_table[3],
                                           "precision_train": evaluation_table[4],
                                           "precision_test": evaluation_table[5],
                                           "f1_train": evaluation_table[6], "f1_test": evaluation_table[7]}

    if confusion_matrix_table:
        result_dict["confusion_matrix"] = confusion_matrix_table.to_json(orient='split')

    if accuracy:
        result_dict["accuracy"] = accuracy

    # add more if needed

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
            [accuracy_train, recall_train, precision_train, f1_train, accuracy_test, recall_test, precision_test,
             f1_test])
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
    result_content = []
    result_content.append(make_result_section(section_name="Evaluation Results",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      ['%.3f' % (evaluation_table[0]), '%.3f' % (evaluation_table[1]),
                                                       '%.3f' % (evaluation_table[2]),
                                                       '%.3f' % (evaluation_table[3])],
                                                      # '%.3f' % means 3 decimal places
                                                      ['%.3f' % (evaluation_table[4]), '%.3f' % (evaluation_table[5]),
                                                       '%.3f' % (evaluation_table[6]),
                                                       '%.3f' % (evaluation_table[7])]],
                                                  "columns": ["Accuracy", "Recall", "Precision", "F1"],
                                                  "index": ["Training Set", "Test Set"]
                                              }))

    result_content.append(make_result_section(section_name="Confusion Matrix",
                                              content_type="table",
                                              content=confusion_matrix_table.to_dict(orient='split')))

    result_content.append(make_result_section(section_name="Accuracy",
                                              content_type="text",
                                              content=accuracy))

    return result_content


def knn_classification(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Establish a K-Nearest Neighbor (KNN) classifier model through the training set data.",
                                                  "Apply the established K-Nearest Neighbor (KNN) classifier model to the training and test data to obtain the classification evaluation results of the model.",
                                                  "If the data shuffling function is selected for K-Nearest Neighbors (KNN), the result of each calculation is different. If you save this training model, you can directly upload the data and substitute it into this training model for calculation and classification.",
                                                  "Note: The K-Nearest Neighbor (KNN) classifier model cannot obtain a definite equation like the traditional model, and the model is usually evaluated by testing the classification effect of the data."
                                              ]))

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

        pic = make_heatmap_pic(cnf_matrix)

        # get the accuracy
        accuracy = neigh.score(x_test, y_test)

        # make all the values in result_table and confusion_matrix_table to one dictionary
        evaluation_table = [accuracy_train, recall_train, precision_train, f1_train, accuracy_test, recall_test,
                            precision_test, f1_test]
        result_content.append(make_result_section(section_name="Evaluation Results",
                                                  content_type="table",
                                                  content={
                                                      "data": [['%.3f' % (evaluation_table[0]),
                                                                '%.3f' % (evaluation_table[1]),
                                                                '%.3f' % (evaluation_table[2]),
                                                                '%.3f' % (evaluation_table[3])],
                                                               # '%.3f' % means 3 decimal places
                                                               ['%.3f' % (evaluation_table[4]),
                                                                '%.3f' % (evaluation_table[5]),
                                                                '%.3f' % (evaluation_table[6]),
                                                                '%.3f' % (evaluation_table[7])]],
                                                      "columns": ["Accuracy", "Recall", "Precision", "F1"],
                                                      "index": ["Training Set", "Test Set"]
                                                  }))
        # result_content.append(make_result_section(section_name="Confusion Matrix",
        #                                           content_type="table",
        #                                           content=cnf_matrix.to_dict(orient='split')))
        result_content.append(make_result_section(section_name="Heatmap", content_type="img", content=pic))
        result_content.append(make_result_section(section_name="Accuracy",
                                                  content_type="text",
                                                  content=accuracy))
    else:
        result_content += cross_validation(x_train, y_train, neigh,
                                           int(parameters["cross_validation"].split("-", 1)[0]))  # k-fold

    return result_content


def svm_classification(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Establish a Support vector machine (SVM) class classification model through the training set data.",
                                                  "Apply the established Support vector machine (SVM) classification model to the training and test data to obtain the classification evaluation results of the model.",
                                                  "Due to the random nature of support vector machine (SVM) classification, the results of each operation are not the same"
                                                  "Note: The Support vector machine (SVM) classification model cannot obtain a definite equation like the traditional model, and the model is usually evaluated by testing the classification effect of the data."
                                              ]))

    # Constructing a support vector machine (SVM) classifier model
    clf = svm.SVC(kernel=parameters["kernel"], C=float(parameters["C"]), tol=float(parameters["tol"]),
                  max_iter=int(parameters["max_iter"]))

    # slice the dataframe according to the features selected by the user
    x_train = df[parameters["features"]]
    y_train = df[parameters["target"]]

    # If the data needs to be shuffled, the shuffle operation is performed
    if parameters["shuffle"] == "True":
        x_train, y_train = shuffle_dataset(x_train, y_train)

    # Divide the dataset and return the divided training and test sets
    if parameters["cross_validation"] == "None":
        x_train, x_test, y_train, y_test = dataset_split(x_train, y_train, 1 - float(parameters["train_ratio"]))
        clf.fit(x_train, y_train)

        # Prediction on training and test sets
        y_train_pred = clf.predict(x_train)
        y_test_pred = clf.predict(x_test)

        # Calculate evaluation metrics
        accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test = \
            get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred)

        # Compute confusion matrix
        cnf_matrix = pd.DataFrame(confusion_matrix(y_test, y_test_pred))

        pic = make_heatmap_pic(cnf_matrix)

        # get the accuracy
        accuracy = clf.score(x_test, y_test)

        # make all the values in result_table and confusion_matrix_table to one dictionary
        evaluation_table = [accuracy_train, recall_train, precision_train, f1_train, accuracy_test, recall_test,
                            precision_test, f1_test]
        result_content.append(make_result_section(section_name="Evaluation Results",
                                                  content_type="table",
                                                  content={
                                                      "data": [['%.3f' % (evaluation_table[0]),
                                                                '%.3f' % (evaluation_table[1]),
                                                                '%.3f' % (evaluation_table[2]),
                                                                '%.3f' % (evaluation_table[3])],
                                                               # '%.3f' % means 3 decimal places
                                                               ['%.3f' % (evaluation_table[4]),
                                                                '%.3f' % (evaluation_table[5]),
                                                                '%.3f' % (evaluation_table[6]),
                                                                '%.3f' % (evaluation_table[7])]],
                                                      "columns": ["Accuracy", "Recall", "Precision", "F1"],
                                                      "index": ["Training Set", "Test Set"]
                                                  }))
        # result_content.append(make_result_section(section_name="Confusion Matrix",
        #                                           content_type="table",
        #                                           content=cnf_matrix.to_dict(orient='split')))
        result_content.append(make_result_section(section_name="Heatmap", content_type="img", content=pic))
        result_content.append(make_result_section(section_name="Accuracy",
                                                  content_type="text",
                                                  content=accuracy))
    else:
        result_content += cross_validation(x_train, y_train, clf,
                                           int(parameters["cross_validation"].split("-", 1)[0]))  # k-fold

    return result_content


def svr_regression(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Establish a Support vector machine regression (SVR) model through the training set data.",
                                                  "Apply the established Support vector machine regression (SVR) model to the training and test data to obtain the classification evaluation results of the model.",
                                                  "Due to the random nature of support vector machine (SVR) regression, the results of each operation are not the same"
                                                  "Note: The Support vector machine regression (SVR) model cannot obtain a definite equation like the traditional model, and the model is usually evaluated by testing the classification effect of the data."
                                              ]))

    # Constructing SVM regression models
    svm = SVR(kernel=parameters["kernel"], C=float(parameters["C"]), tol=float(parameters["tol"]),
              max_iter=int(parameters["max_iter"]))

    # 从数据框中选取用户指定的特征和目标列
    x_train = df[parameters["features"]]
    y_train = df[parameters["target"]]

    # If the data needs to be shuffled, the shuffle operation is performed
    if parameters["shuffle"] == "True":
        x_train, y_train = shuffle_dataset(x_train, y_train)

    # Divide the dataset and return the divided training and test sets
    if parameters["cross_validation"] == "None":
        x_train, x_test, y_train, y_test = dataset_split(x_train, y_train, 1 - float(parameters["train_ratio"]))
        svm.fit(x_train, y_train)

        # Prediction on training and test sets
        y_train_pred = svm.predict(x_train)
        y_test_pred = svm.predict(x_test)

        # Calculate evaluation metrics
        accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test = \
            get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred)

        # Compute confusion matrix
        cnf_matrix = pd.DataFrame(confusion_matrix(y_test, y_test_pred))

        pic = make_heatmap_pic(cnf_matrix)

        # get the accuracy
        accuracy = svm.score(x_test, y_test)

        # make all the values in result_table and confusion_matrix_table to one dictionary
        evaluation_table = [accuracy_train, recall_train, precision_train, f1_train, accuracy_test, recall_test,
                            precision_test, f1_test]
        result_content.append(make_result_section(section_name="Evaluation Results",
                                                  content_type="table",
                                                  content={
                                                      "data": [['%.3f' % (evaluation_table[0]),
                                                                '%.3f' % (evaluation_table[1]),
                                                                '%.3f' % (evaluation_table[2]),
                                                                '%.3f' % (evaluation_table[3])],
                                                               # '%.3f' % means 3 decimal places
                                                               ['%.3f' % (evaluation_table[4]),
                                                                '%.3f' % (evaluation_table[5]),
                                                                '%.3f' % (evaluation_table[6]),
                                                                '%.3f' % (evaluation_table[7])]],
                                                      "columns": ["Accuracy", "Recall", "Precision", "F1"],
                                                      "index": ["Training Set", "Test Set"]
                                                  }))
        # result_content.append(make_result_section(section_name="Confusion Matrix",
        #                                           content_type="table",
        #                                           content=cnf_matrix.to_dict(orient='split')))
        result_content.append(make_result_section(section_name="Heatmap", content_type="img", content=pic))
        result_content.append(make_result_section(section_name="Accuracy",
                                                  content_type="text",
                                                  content=accuracy))
    else:
        result_content += cross_validation(x_train, y_train, svm,
                                           int(parameters["cross_validation"].split("-", 1)[0]))  # k-fold

    return result_content


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
