import numpy as np
from sklearn import svm
from sklearn.neighbors import KNeighborsClassifier
from sklearn.model_selection import train_test_split, KFold
from sklearn.metrics import confusion_matrix, accuracy_score, recall_score, precision_score, f1_score
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeClassifier
from sklearn.utils import shuffle
import seaborn as sns
import pandas as pd
from scipy import stats
from scipy.stats import t
from scipy.stats import skew
from scipy.stats import spearmanr
import psython
import pingouin as pg
import statsmodels.api as sm
from statsmodels.tsa.stattools import adfuller
from statsmodels.tsa.arima.model import ARIMA
import matplotlib.pyplot as plt
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
        'svm_classification': svm_classification,
        'adf_test': adf_test,
        'Bland-Altman_method': Bland_Altman_method,
        "decision_matrix": decision_matrix,
        'decision_tree': decision_tree_classification
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


def decision_matrix(df, parameters):
    result_content = []

    D = df[parameters['variable']].values

    # 计算指标变异性
    VC = np.var(D, axis=0, ddof=1)

    # 计算指标冲突性
    CC = np.zeros((D.shape[1], D.shape[1]))
    for j in range(D.shape[1]):
        for k in range(j + 1, D.shape[1]):
            CC[j][k] = np.sum((D[:, j] - np.mean(D[:, j])) * (D[:, k] - np.mean(D[:, k]))) / (D.shape[0] - 1) / np.std(
                D[:, j], ddof=1) / np.std(D[:, k], ddof=1)
            CC[k][j] = CC[j][k]

    # 计算信息量
    IC = VC / np.sum(CC, axis=1)

    # 计算权重百分比
    WP = IC / np.sum(IC) * 100

    result_df = pd.DataFrame({
        "Indicator variability": VC,
        'Information content': IC,
        'weight percentage': WP
    }, index=df.columns)

    table_data = []
    for index, row in result_df.iterrows():
        row_data = list(row)
        table_data.append(row_data)

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Firstly, the weight of each index is analyzed according to the weight calculation results.",
                                                  "The weight analysis matrix is obtained through the weight calculation results.",
                                                  "Summarize the analysis."
                                              ]))

    result_content.append(make_result_section(section_name="Detailed conclusions",
                                              content_type="text",
                                              content=''))

    result_content.append(make_result_section(section_name="Output 1: weight calculation result",
                                              content_type="table",
                                              content={
                                                  "data": table_data,
                                                  "columns": [
                                                      "Indicator variability",
                                                      'Information content',
                                                      'weight percentage'
                                                  ],
                                                  "index": parameters['variable']
                                              }))

    result_content.append(make_result_section(section_name="Table description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table shows the weight calculation results of the CRITIC method, and analyzes the weight of each indicator according to the results.",
                                                  "The index variability is the standard deviation, the greater the standard deviation, the greater the weight.",
                                                  "The amount of information is index variability * conflict index.",
                                                  "The weight is the normalization of the amount of information."
                                              ]))

    decision_pic = make_decision_pic(WP, parameters['variable'])

    result_content.append(make_result_section(section_name="Output 2: indicator importance histogram",
                                              content_type="img",
                                              content=decision_pic
                                              ))

    result_content.append(make_result_section(section_name="Chart descriptions",
                                              content_type="text",
                                              content="The figure above shows the importance of indicators in the form of a histogram."))

    return result_content


def make_decision_pic(WP, column):
    f = plt.figure()
    data = WP
    labels = column

    # 将数据转化为百分比
    data_perc = data / np.sum(data) * 100

    # 绘制横向直方图
    fig, ax = plt.subplots()
    # 设置横轴和纵轴标签
    ax.set_xlabel('Percentage')
    ax.set_ylabel('Category')
    bars = ax.barh(labels, data_perc)
    for bar, val in zip(bars, data):
        ax.text(bar.get_width(), bar.get_y() + bar.get_height() / 2, "{:.3f}".format(val), ha='left', va='center')

    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    f.clear()
    plt.close()

    return base64_pic


def Bland_Altman_method(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Analyze the results of the Bland-Altman method to obtain the mean value, P value (used to assist in judging the consistency) and the value of the limit of agreement (LoA).",
                                                  "Analyzing the Bland-Altman graph, the more points are within 95% LoA (dotted line in the graph), the better the consistency."
                                              ]))

    first_method = parameters['first method']
    second_method = parameters['second method']

    if parameters['testing_method'] == "difference":
        df['difference'] = df[first_method].sub(df[second_method])
    elif parameters['testing_method'] == "ratio":
        df['difference'] = df[first_method] / df[second_method]

    sample_size = df.shape[0]

    std = np.std(df['difference'], ddof=1)

    if parameters['testing_method'] == "difference":
        mean_value1 = df[first_method].mean()
        mean_value2 = df[second_method].mean()
        mean_value = abs(mean_value1 - mean_value2)
    elif parameters['testing_method'] == "ratio":
        mean_value1 = df[first_method].mean()
        mean_value2 = df[second_method].mean()
        mean_value = abs(mean_value1 / mean_value2)

    mean_value_95lower = mean_value - 1.96 * std
    mean_value_95upper = mean_value + 1.96 * std

    # p_value
    t_stat = mean_value / (std / np.sqrt(len(df['difference'])))
    p_val = t.sf(np.abs(t_stat), len(df['difference']) - 1) * 2

    CR = 1.96 * std * np.sqrt(2)

    result_content.append(make_result_section(section_name="Output 1: Bland-Altman method result",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      [sample_size],
                                                      ['%.3f' % mean_value],
                                                      ['%.3f' % std],
                                                      ['%.3f' % mean_value_95upper],
                                                      ['%.3f' % mean_value_95lower],
                                                      [p_val],
                                                      ['%.3f' % CR]
                                                  ],
                                                  "columns": [
                                                      "value"
                                                  ],
                                                  "index": [
                                                      "sample size", "arithmetic mean", "standard deviation",
                                                      "Upper limit of LoA", "Lower limit of LoA", "P value",
                                                      "coefficient of repeatability"
                                                  ]
                                              }))

    result_content.append(make_result_section(section_name="Chart descriptions",
                                              content_type="text",
                                              content='The above table shows the results of the Bland-Altman method, mainly the average value, P value (used to assist in judging the consistency) and the value of the limit of agreement (LoA).'))

    Bland_Altman_pic = make_Bland_Altman_plot(df, first_method, second_method)

    result_content.append(make_result_section(section_name="Output 2: Bland-Altman graph",
                                              content_type="img",
                                              content=Bland_Altman_pic
                                              ))

    result_content.append(make_result_section(section_name="Chart descriptions",
                                              content_type="text",
                                              content="The above table shows the Bland-Altman diagram, which is used to analyze the consistency. The more points that are within the 95% LoA (dotted line in the graph), the better the agreement."))

    return result_content


def make_Bland_Altman_plot(df, first_method, second_method):
    f, ax = plt.subplots(1, figsize=(8, 5))
    sm.graphics.mean_diff_plot(df[first_method], df[second_method], ax=ax)
    # plt.show()

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    f.clear()
    plt.close()

    return base64_pic


def adf_test(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "By analyzing the t value, analyze whether it can significantly reject the null hypothesis of sequence instability (P<0.05).",
                                                  "If it is significant, it indicates that the null hypothesis that the series is not stationary is rejected, and the series is a stationary time series.",
                                                  "If it is not significant, it indicates that the null hypothesis that the sequence is not stable cannot be rejected. The sequence is an unstable time series. Considering the difference of the data, generally no more than the second order difference."
                                              ]))

    result_content.append(make_result_section(section_name="Detailed conclusions",
                                              content_type="text",
                                              content=''))

    # difference order = 0
    time_series_data = df[parameters["time series data"]]
    time_item = df[parameters["time item"]]

    df_combined1 = pd.concat([time_series_data, time_item], axis=1)

    original_sequence_pic_1 = make_original_sequence_pic(df_combined1)

    adf_result1 = adfuller(time_series_data)
    t_value1 = adf_result1[0]
    p_value1 = adf_result1[1]
    critical_value1_1 = adf_result1[4]['1%']
    critical_value1_5 = adf_result1[4]['5%']
    critical_value1_10 = adf_result1[4]['10%']

    index1 = f'{parameters["time series data"]} difference order 0'

    model = ARIMA(time_series_data, order=(1, 1, 1))
    result1 = model.fit()
    aic1 = result1.aic

    # difference order = 1
    diff1_time_series_data = time_series_data.diff()
    diff1_time_series_data = diff1_time_series_data.drop(diff1_time_series_data.index[0])

    time_item = time_item.iloc[1:]
    df_combined2 = pd.concat([diff1_time_series_data, time_item], axis=1)
    df_combined2.dropna(inplace=True)
    original_sequence_pic_2 = make_original_sequence_pic(df_combined2)

    adf_result2 = adfuller(diff1_time_series_data)
    t_value2 = adf_result2[0]
    p_value2 = adf_result2[1]
    critical_value2_1 = adf_result2[4]['1%']
    critical_value2_5 = adf_result2[4]['5%']
    critical_value2_10 = adf_result2[4]['10%']

    index2 = f'{parameters["time series data"]} difference order 1'

    model = ARIMA(diff1_time_series_data, order=(1, 1, 1))
    result2 = model.fit()
    aic2 = result2.aic

    # difference order = 2
    diff2_time_series_data = diff1_time_series_data.diff()
    diff2_time_series_data = diff2_time_series_data.drop(diff2_time_series_data.index[0])
    time_item = time_item.iloc[2:]
    df_combined3 = pd.concat([diff2_time_series_data, time_item], axis=1)
    original_sequence_pic_3 = make_original_sequence_pic(df_combined3)

    adf_result3 = adfuller(diff2_time_series_data)
    t_value3 = adf_result3[0]
    p_value3 = adf_result3[1]
    critical_value3_1 = adf_result3[4]['1%']
    critical_value3_5 = adf_result3[4]['5%']
    critical_value3_10 = adf_result3[4]['10%']

    index3 = f'{parameters["time series data"]} difference order 2'

    model = ARIMA(diff2_time_series_data, order=(1, 1, 1))
    result3 = model.fit()
    aic3 = result3.aic

    result_content.append(make_result_section(section_name="Output 1: ADF inspection table",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      [
                                                          '%.3f' % t_value1,
                                                          '%.3f' % p_value1,
                                                          '%.3f' % aic1,
                                                          '%.3f' % critical_value1_1,
                                                          '%.3f' % critical_value1_5,
                                                          '%.3f' % critical_value1_10
                                                      ],
                                                      [
                                                          '%.3f' % t_value2,
                                                          '%.3f' % p_value2,
                                                          '%.3f' % aic2,
                                                          '%.3f' % critical_value2_1,
                                                          '%.3f' % critical_value2_5,
                                                          '%.3f' % critical_value2_10
                                                      ],
                                                      [
                                                          '%.3f' % t_value3,
                                                          '%.3f' % p_value3,
                                                          '%.3f' % aic3,
                                                          '%.3f' % critical_value3_1,
                                                          '%.3f' % critical_value3_5,
                                                          '%.3f' % critical_value3_10
                                                      ],
                                                  ],
                                                  "columns": [
                                                      "t",
                                                      "P",
                                                      "AIC",
                                                      "critical value(1%)",
                                                      "critical value(5%)",
                                                      "critical value(10%)"
                                                  ],
                                                  "index": [index1, index2, index3
                                                            ]
                                              }))

    result_content.append(make_result_section(section_name="Table description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table is the result of ADF test, including variables, difference order, T test results, AIC value, etc., which are used to test whether the time series is stable.",
                                                  "The model requires that the sequence must be a stationary time series data. By analyzing the t value, analyze whether it can significantly reject the null hypothesis of sequence instability.",
                                                  "If it is significant (P<0.05), it means that the null hypothesis is rejected, and the series is a stationary time series; otherwise, it means that the series is an unstationary time series.",
                                                  "The critical value of 1%, 5%, 10% compares the statistical value of rejecting the null hypothesis in different degrees and the ADF Test result, and the ADF Test result is less than 1%, 5%, and 10% at the same time, which means that the hypothesis is rejected very well.",
                                                  "Difference order: essentially the next value, minus the previous value, mainly to eliminate some fluctuations and make the data tend to be stable. Non-stationary sequences can be transformed into stationary sequences through differential transformation.",
                                                  "AIC value: A standard to measure the goodness of statistical model fitting, the smaller the value, the better.",
                                                  "Critical value: A critical value is a fixed value corresponding to a given significance level."
                                              ]))

    result_content.append(make_result_section(section_name="Output 2: original sequence diagram",
                                              content_type="img",
                                              content=original_sequence_pic_1
                                              ))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content=
                                              "The image above shows the original image without difference. The X-axis represents the time item, and the Y-axis represents the value."
                                              ))

    result_content.append(make_result_section(section_name="Output 3: first-order difference map",
                                              content_type="img",
                                              content=original_sequence_pic_2
                                              ))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content=
                                              "The figure above shows the resulting plot of taking a first-order difference. When the time intervals are equal, subtract the previous value from the next value to get the first difference."
                                              ))

    result_content.append(make_result_section(section_name="Output 4: second-order difference map",
                                              content_type="img",
                                              content=original_sequence_pic_3
                                              ))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="text",
                                              content=
                                              "The figure above shows the resulting plot of the second difference. Doing the same action twice, that is, subtracting a value from the last value on the basis of the first-order difference, is called 'second-order difference'."
                                              ))

    return result_content


def make_original_sequence_pic(column):
    # plot histogram and density curve
    f = plt.figure()
    x = column.iloc[:, 0]
    y = column.iloc[:, 1]
    plt.plot(y, x)

    # Encode into a string in the form of base64
    pic_io = io.BytesIO()
    plt.savefig(pic_io, format='png')
    pic_io.seek(0)
    base64_pic = base64.b64encode(pic_io.read()).decode()

    # Clear plt buffer
    f.clear()
    plt.close()

    return base64_pic


def reliability_analysis(df, parameters):
    if parameters["Analytical_method"] == "Cronbach's α":
        result_content = cronbach(df, parameters)
    elif parameters["Analytical_method"] == "Split-half Reliability":
        result_content = splitHalf(df, parameters)

    return result_content


def cronbach(df, parameters):
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

    the_Cronbach, if_deleted_table = psython.cronbach_alpha_scale_if_deleted(df)

    table_data = []
    for index, row in if_deleted_table.iterrows():
        row_data = list(row)
        table_data.append(row_data)

    num_rows = if_deleted_table.shape[0]
    row_nums = list(range(1, num_rows + 1))

    result_content.append(
        make_result_section(section_name="Output 2: delete the statistical summary of the analysis item",
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


def splitHalf(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "There is currently no uniform standard for the analysis of Cronbach's α coefficient (or half coefficient), but according to the views of most scholars, generally if the Cronb's α coefficient (or half coefficient) is above 0.9, the reliability of the test or scale is very good , between 0.8-0.9 means the reliability is good, between 0.7-0.8 means the reliability is acceptable, between 0.6-0.7 means the reliability is average, between 0.5-0.6 means the reliability is not ideal, if it is below 0.5 Consider reorganizing the questionnaire.",
                                                  "Carry out further analysis on the item summary statistics table to see which items lead to the decline of the overall reliability. If the value of the reliability is lower than 0.3, or the value of 'α coefficient after deleting the item' Significantly higher than the α coefficient, you can consider removing this topic at this time."

                                              ]))

    result_content.append(make_result_section(section_name="Detailed conclusions",
                                              content_type="text",
                                              content=''))

    # here variable_names is the array of variables
    variable_names = parameters["variables"]
    # new_df  includes the columns need to conduct reliablity analysis
    new_df = df.loc[:, variable_names]

    n_cols = len(new_df.columns)
    half_cols = n_cols // 2

    df1 = new_df.iloc[:, :half_cols]
    df2 = new_df.iloc[:, half_cols:]

    number_of_items1 = df1.shape[1]
    number_of_items2 = df2.shape[1]

    result1 = pg.cronbach_alpha(data=df1)[0]
    result2 = pg.cronbach_alpha(data=df2)[0]

    # 计算两组数据的总分
    sum1 = df1.sum(axis=1)
    sum2 = df2.sum(axis=1)

    # 计算两组数据的斯皮尔曼相关系数
    corr = spearmanr(sum1, sum2).correlation

    # 计算 Spearman-Brown 系数
    sb = 2 * corr / (1 + corr)

    result_content.append(make_result_section(section_name="Output 1: Half-half reliability coefficient table",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      [result1,
                                                       number_of_items1
                                                       ],
                                                      [
                                                          result2,
                                                          number_of_items2
                                                      ]
                                                  ],
                                                  "columns": ["Cronbach's alpha coefficient",
                                                              "number of items"
                                                              ],
                                                  "index": ["first half", "second half"]
                                              }))

    result_content.append(make_result_section(section_name="Output 2: Spearman-Brown coefficient",
                                              content_type="table",
                                              content={
                                                  "data": [
                                                      [sb]
                                                  ],
                                                  "columns": ["Spearman-Brown coefficient"
                                                              ],
                                                  "index": ["total dataset"]
                                              }))

    result_content.append(make_result_section(section_name="Chart description:",
                                              content_type="ordered_list",
                                              content=[
                                                  "The above table shows the results of half-half reliability analysis of the model, including Cronbach's α coefficient value, correlation coefficient value, and half-half coefficient.",
                                                  "The split-half reliability method is to divide the survey item into two halves, calculate the correlation coefficient of the scores of the two halves, and then estimate the reliability of the entire scale;",
                                                  "The Cronbach α of the two parts before and after can be calculated to obtain the correlation coefficient value of the two parts of the data, and the correlation coefficient value participates in the calculation of the Spearman-Brown coefficient.",
                                                  "If the number of items is an odd number n, the number of items in the first part is (n+1)/2, and the number of items in the second half is (n-1)/2, which is 'unequal length'. If the number of items isEven n, the number of items in the first part is n/2, and the number of items in the second half is n/2, which are 'equal length'.",
                                                  "According to whether the number of items in the two parts is 'equal length' or 'unequal length', select the corresponding half coefficient (Spearman-Brown) to judge the reliability effect."
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


def get_unique_label_list(df):
    labels = list(df.unique())
    labels.sort()
    return labels


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

        pic = make_heatmap_pic(cnf_matrix, labels=get_unique_label_list(y_train))

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
                                                  "Due to the random nature of support vector machine (SVM) classification, the results of each operation are not the same",
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

        pic = make_heatmap_pic(cnf_matrix, get_unique_label_list(y_train))

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
                                                  "Due to the random nature of support vector machine (SVR) regression, the results of each operation are not the same",
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

        pic = make_heatmap_pic(cnf_matrix, get_unique_label_list(y_train))

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


def decision_tree_classification(df, parameters):
    result_content = []

    result_content.append(make_result_section(section_name="Analysis steps",
                                              content_type="ordered_list",
                                              content=[
                                                  "Establish a Decision Number Classification Model to obtain a decision tree structure. through the training set data.",
                                                  "Feature importance is calculated from the decision tree built.",
                                                  "Apply the established Decision Tree classification model to the training and test data to obtain the classification evaluation results of the model.",
                                                  "Due to the random nature of Decision Tree classification, the results of each operation are not the same.",
                                                  "Note: Decision trees do not yield definitive equations as traditional models do. At each decision node, the segmentation features chosen determine the final classification result, and the model is usually evaluated by testing the effectiveness of the data classification."
                                              ]))

    # Construct a Decision Tree classifier model
    clf = DecisionTreeClassifier(criterion=parameters["criterion"], splitter=parameters["splitter"],
                                 min_samples_split=int(parameters["min_samples_leaf"]),
                                 min_samples_leaf=int(parameters["min_samples_leaf"]),
                                 max_depth=int(parameters["max_depth"]),
                                 max_leaf_nodes=int(parameters["max_leaf_nodes"]))

    # Slice the dataframe according to the features selected by the user
    x_train = df[parameters["features"]]
    y_train = df[parameters["target"]]

    # If the data needs to be shuffled, perform the shuffle operation
    if parameters["shuffle"] == "True":
        x_train, y_train = shuffle_dataset(x_train, y_train)

    # Divide the dataset and return the divided training and test sets
    if parameters["cross_validation"] == "None":
        x_train, x_test, y_train, y_test = dataset_split(x_train, y_train, 1 - float(parameters["train_ratio"]))
        clf.fit(x_train, y_train)

        # Predict on training and test sets
        y_train_pred = clf.predict(x_train)
        y_test_pred = clf.predict(x_test)

        # Calculate evaluation metrics
        accuracy_train, accuracy_test, recall_train, recall_test, precision_train, precision_test, f1_train, f1_test = \
            get_evaluation_metrics(y_train, y_train_pred, y_test, y_test_pred)

        # Compute confusion matrix
        cnf_matrix = pd.DataFrame(confusion_matrix(y_test, y_test_pred))

        pic = make_heatmap_pic(cnf_matrix, get_unique_label_list(y_train))

        # Get the accuracy
        accuracy = clf.score(x_test, y_test)

        # Make all the values in result_table and confusion_matrix_table into one dictionary
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

        result_content.append(make_result_section(section_name="Heatmap", content_type="img", content=pic))
        result_content.append(make_result_section(section_name="Accuracy",
                                                  content_type="text",
                                                  content=accuracy))
    else:
        result_content += cross_validation(x_train, y_train, clf,
                                           int(parameters["cross_validation"].split("-", 1)[0]))  # k-fold

    return result_content
