from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder


# app = Flask(__name__)
#
#
# @app.route('/')
# def home():
#     return render_template('index.html')
#
# @app.route('/upload', methods=['POST'])
# def upload():
#     file = request.files['file'] #dataset to be processed
#     df = pd.read_csv(file, header=1) #convert .csv to dataframe
#     para_received = request.form.get("para"); #parameter dictionary received from html
#     df = process(df, para_received)
#     return 0

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

paraset = {'identification_method': ['y', 'y', 'y', ''], 'fill_type' : 'normal', }
process(pd_reader, paraset);

