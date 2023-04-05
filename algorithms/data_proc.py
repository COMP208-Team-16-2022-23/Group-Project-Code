import io
from flask import g
import pandas as pd
import numpy as np
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.combine import SMOTEENN

from util import storage_control
from util import file_util


# pd_reader = pd.read_csv("../misc/temp/CountyGDP_ECON215.csv")
# print(pd_reader)

def process(file_path, parameters):
    """
    :param file_path: the path of the file to be processed
    :param parameters: a dictionary of parameters
    :return: the processed file path
    """

    # read file as pandas dataframe, file include column names
    df = pd.read_csv(storage_control.download_to_memory(file_path),
                     header=0)  # header=0 means the first row is column names

    # get processing method
    processing_method = parameters['function_name']

    # call corresponding function
    match processing_method:
        case 'outlier_handling':
            df = outlier_handling(df, parameters)
        case 'tail_shrinkage_or_truncation_processing':
            df = tail_shrinkage_or_truncation_processing(df, parameters)
        case 'normalisation':
            df = normalization(df, parameters)
        case 'sample_balancing':
            df = sample_balancing(df, parameters)
        case _:  # default
            pass

    file = df.to_csv(index=False)

    new_file_path = file_util.add_suffix(file_path=file_path, suffix=processing_method, username=g.user.username)
    processed_file_path = storage_control.upload_blob(file=file, blob_name=new_file_path)

    return processed_file_path


def outlier_handling(df, parameters):
    """
    :param df: the pandas dataframe to be processed
    :param parameters: a dictionary of parameters
    :return: the processed dataframe
    """

    # print(parameters)
    # get detection method
    detection_method = parameters['Detection method']

    # better to use a switch case here, but need python 3.10
    # call corresponding function
    if detection_method == '3-sigma':
        for column_name in parameters['column_selected']:
            df = three_sigma(df, column_name=column_name)

    return df


def three_sigma(df, column_name, parameters=None):
    """
    Use 3-sigma method to detect outliers
    :param df: the pandas dataframe to be processed
    :param parameters: a dictionary of parameters
    :return: the processed dataframe
    """

    # get column by name
    column = df[column_name]

    # get mean and standard deviation
    mean = column.mean()
    std = column.std()

    # get lower and upper bound
    lower_bound = mean - 3 * std
    upper_bound = mean + 3 * std

    # replace outliers with NaN
    df[column_name] = df[column_name].apply(lambda x: np.nan if x < lower_bound or x > upper_bound else x)

    return df


def tail_shrinkage_or_truncation_processing(df, parameters):
    """
    Use tail shrinkage or truncation method to Exclude extreme values
    :param df: the pandas dataframe to be processed
    :param parameters: a dictionary of parameters
    :return: the processed dataframe
    method is the method to be used, there are two methods: tail_shrinkage and tail_truncation
    column_name is the column to be processed(I don't know how to get the column name by this way)
    upper_percentile is the upper limit of the percentile, lower_percentile is the lower limit of the percentile
    processing_method is used when method is tail_truncation, there are two methods: delete_value and replace_value
    test failed
    """

    method = parameters['method_selection']
    column_name = parameters['column_selected']
    upper_percentile = int(parameters['upper_limit'])
    lower_percentile = int(parameters['upper_limit'])
    processing_method = parameters['processing_method']

    # Select the column to process
    col = df[column_name]

    # Calculate the upper and lower limits
    upper_limit = np.percentile(col, 100 - upper_percentile)
    lower_limit = np.percentile(col, lower_percentile)

    # Select the method
    if method == "tail_shrinkage":
        col_without_outliers = col.clip(lower_limit, upper_limit)
        df[column_name] = col_without_outliers

    elif method == "tail_truncation":
        if processing_method == "delete_value":
            col_without_outliers = col[(col >= lower_limit) & (col <= upper_limit)]
            df[column_name] = col_without_outliers

        elif processing_method == "delete_row":
            df_without_outliers = df[(col >= lower_limit) & (col <= upper_limit)]
            df.drop(df.index.difference(df_without_outliers.index).tolist())

    return df


def sample_balancing(df, parameters):
    """
    Use sample balancing method to balance the classes
    :param df: the pandas dataframe to be processed
    :param parameters: a dictionary of parameters
    :return: the processed dataframe
    column_name is the column to be processed
    balancing_method is the method to be used, there are three methods: undersample, oversample and combined
    """
    # Get the target column name and balancing method from parameters
    column_name = parameters['column_selected']
    balancing_method = parameters['balancing_method']

    # Separate the target column and features from the dataframe
    y = df[column_name]
    x = df.drop(column_name, axis=1)

    if balancing_method == 'undersample':
        # Create an instance of RandomUnderSampler and balance the classes
        sampler = RandomUnderSampler()
        x_resampled, y_resampled = sampler.fit_resample(x, y)

    elif balancing_method == 'oversample':
        # Create an instance of RandomOverSampler and balance the classes
        sampler = RandomOverSampler()
        x_resampled, y_resampled = sampler.fit_resample(x, y)

    elif balancing_method == 'combined':
        # Create an instance of SMOTEENN and balance the classes
        sampler = SMOTEENN(ratio='auto')
        x_resampled, y_resampled = sampler.fit_resample(x, y)

    else:
        # If balancing_method is invalid, return the original dataframe
        return df

    # Combine the resampled data and return as a new dataframe
    resampled_df = pd.concat([x_resampled, y_resampled], axis=1)

    return resampled_df


# def process(df, para_received):
#     # identification_method should be an array
#     # and in format: ["empty value", "space", "None", "customize"]
#     identification_method = para_received["identification_method"]
#     # fill_type, filling_method, output_format are strings
#     fill_type = para_received["fill_type"]
#     filling_method = para_received["filling_method"]
#     output_format = para_received["output_format"]
#
#     return {
#         "mean": value_replace_mean(df, identification_method),
#         "median": value_replace_median(df, identification_method),
#         "mode": value_replace_mode(df, identification_method),
#         "3std": value_replace_3std(df, identification_method),
#         "tail": tail_shrinkage_or_truncation_processing(df, para_received),
#         "sample_balancing": sample_balancing(df, para_received),
#     }.get(filling_method, None)


def value_replace_mean(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "on":
            df[i].replace("", value=df[i].mean(), inplace=True)
        if identification_method[1] == "on":
            df.replace(" ", value=df[i].mean(), inplace=True)
        if identification_method[2] == "on":
            df.replace("None", value=df[i].mean(), inplace=True)
        if identification_method[3] != "":
            customize_value = identification_method[3]
            df.replace(customize_value, value=df[i].mean(), inplace=True)

    return df


def value_replace_median(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "on":
            df[i].replace("", value=df[i].median(), inplace=True)
        if identification_method[1] == "on":
            df.replace(" ", value=df[i].median(), inplace=True)
        if identification_method[2] == "on":
            df.replace("None", value=df[i].median(), inplace=True)
        if identification_method[3] != "":
            customize_value = identification_method[3]
            df.replace(customize_value, value=df[i].median(), inplace=True)

    return df


def value_replace_mode(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "y":
            df[i].replace("", value=(df.mode())[i][0], inplace=True)
        if identification_method[1] == "y":
            df.replace(" ", value=(df.mode())[i][0], inplace=True)
        if identification_method[2] == "y":
            df.replace("None", value=(df.mode())[i][0], inplace=True)
        if identification_method[3] != "":
            customize_value = identification_method[3]
            df.replace(customize_value, value=(df.mode())[i][0], inplace=True)
    return df


# convert messing value as three standard derivation
def value_replace_3std(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "y":
            df[i].replace("", value=3 * df[i].std(), inplace=True)
        if identification_method[1] == "y":
            df.replace(" ", value=3 * df[i].std(), inplace=True)
        if identification_method[2] == "y":
            df.replace("None", value=3 * df[i].std(), inplace=True)
        if identification_method[3] != "":
            customize_value = identification_method[3]
            df.replace(customize_value, value=3 * df[i].std(), inplace=True)

    return df


def normalization(df, parameters):

    method = parameters['Method']

    # call corresponding function
    if method == 'Min-Max':
        return Min_Max(df, parameters)
    if method == 'Z-Score':
        return Z_score(df, parameters)

    # Uncompleted method called
    return df


def Min_Max(df, parameters):
    """
    formula: (X-min) / (max-min)
    :param df: Input Dataframe
    :param parameters: Dict containing Method, column_selected and optionally Output option
    :return: normalised Dataframe with parameters above
    """
    method = parameters['Method']
    for column_name in parameters['column_selected']:
        column_min = df[column_name].min()
        data_range = df[column_name].max() - column_min
        new_column = (df[column_name] - column_min) / data_range
        if 'Output option' in parameters.keys() and parameters['Output option'] == 'on':
            df[column_name] = new_column
        else:
            df = df.join(new_column, rsuffix='_' + method)
    return df


def Z_score(df, parameters):
    """
    formula: (X-Mean)/ Std
    :param df: Input Dataframe
    :param parameters: Dict containing Method, column_selected and optionally Output option
    :return: normalised Dataframe with parameters above
    """

    method = parameters['Method']
    # Standardize each column
    for col in parameters['column_selected']:
        col_mean = df[col].mean()
        col_std = df[col].std()
        new_column = (df[col] - col_mean) / col_std
        if 'Output option' in parameters.keys() and parameters['Output option'] == 'on':
            df[col] = new_column
        else:
            # Merge the standardized numerical columns with the non-numerical columns
            df = df.join(new_column, rsuffix='_' + method)

    return df


paraset = {'identification_method': ['y', 'y', 'y', ''], 'fill_type': 'normal', }
# process(pd_reader, paraset)
