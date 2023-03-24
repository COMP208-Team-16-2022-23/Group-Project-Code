from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder

pd_reader = pd.read_csv("./CountyGDP_ECON215.csv")
print(pd_reader)


def process(df, para_received):
    # identification_method should be an array
    # and in format: ["empty value", "space", "None", "customize"]
    identification_method = para_received["identification_method"]
    # fill_type, filling_method, output_format are strings
    fill_type = para_received["fill_type"]
    filling_method = para_received["filling_method"]
    output_format = para_received["output_format"]

    return {
        "mean": value_replace_mean(df, identification_method),
        "median": value_replace_median(df, identification_method),
        "mode": value_replace_mode(df, identification_method),
        "3std": value_replace_3std(df, identification_method),
        "tail": tail_shrinkage_or_truncation_processing(df, para_received),
    }.get(filling_method, None)


def value_replace_mean(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "y":
            df[i].replace("", value=df[i].mean(), inplace=True)
        if identification_method[1] == "y":
            df.replace(" ", value=df[i].mean(), inplace=True)
        if identification_method[2] == "y":
            df.replace("None", value=df[i].mean(), inplace=True)
        if identification_method[3] != "":
            customize_value = identification_method[3]
            df.replace(customize_value, value=df[i].mean(), inplace=True)

    return df


def value_replace_median(df, identification_method):
    i = 0
    while i <= df.shape[1]:
        if identification_method[0] == "y":
            df[i].replace("", value=df[i].median(), inplace=True)
        if identification_method[1] == "y":
            df.replace(" ", value=df[i].median(), inplace=True)
        if identification_method[2] == "y":
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


def tail_shrinkage_or_truncation_processing(df, para_received):
    method = para_received["method_selection"]
    column_name = para_received["variable_to_be_processed"]
    upper_percentile = para_received["upper_limit"]
    lower_percentile = para_received["lower_limit"]
    processing_method = para_received["processing_method"]

    # Select the column to process
    col = df.loc[:, column_name]

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
            df.iloc[:, column_name] = col_without_outliers

        elif processing_method == "delete_row":
            df_without_outliers = df[(col >= lower_limit) & (col <= upper_limit)]
            df = df.drop(df.index.difference(df_without_outliers.index))

    return df


paraset = {'identification_method': ['y', 'y', 'y', ''], 'fill_type': 'normal', }
process(pd_reader, paraset);
