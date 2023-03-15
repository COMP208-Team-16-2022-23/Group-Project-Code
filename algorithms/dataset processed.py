from flask import Flask, request, render_template
import pandas as pd
import numpy as np
from scipy import stats
from sklearn.preprocessing import StandardScaler, LabelEncoder

app = Flask(__name__)


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/upload', methods=['POST'])
def upload():
    file = request.files['file'] #dataset to be processed
    df = pd.read_csv(file, header=1) #convert .csv to dataframe
    para_received = request.form.get("para"); #parameter dictionary received from html
    df = process(df, para_received)
    return 0

def process(df, para_received):
    #identification_method should be an array
    #and in format: ["empty value", "space", "None", "customize"]
    identification_method = para_received["identification_method"]
    #fill_type, filling_method, output_format are strings
    fill_type = para_received["fill_type"]
    filling_method = para_received["filling_method"]
    output_format = para_received["output_format"]

    if(filling_method == "mean"):
        return value_repalce_mean(df, identification_method)
    elif(filling_method == "median"):
        return value_repalce_median(df, identification_method)
    elif (filling_method == "mode"):
        return value_repalce_mode(df, identification_method)
    elif(filling_method == "3std"):
        return value_repalce_3std(df, identification_method)


def value_repalce_mean(df, identification_method):
    i = 0
    while(i <= df.shape[1]):
        if(identification_method[0] == "y"):
            df[i].replace("", value=df[i].mean(), inplace=True)
        if(identification_method[1] == "y"):
            df.replace(" ", value=df[i].mean(), inplace=True)
        if(identification_method[2] == "y"):
            df.replace("None", value=df[i].mean(), inplace=True)
        if(identification_method[3] != ""):
            customize_value = identification_method[3]
            df.replace(customize_value, value=df[i].mean(), inplace=True)

    return df

def value_repalce_median(df, identification_method):
    i = 0
    while (i <= df.shape[1]):
        if (identification_method[0] == "y"):
            df[i].replace("", value=df[i].median(), inplace=True)
        if (identification_method[1] == "y"):
            df.replace(" ", value=df[i].median(), inplace=True)
        if (identification_method[2] == "y"):
            df.replace("None", value=df[i].median(), inplace=True)
        if (identification_method[3] != ""):
            customize_value = identification_method[3]
            df.replace(customize_value, value=df[i].median(), inplace=True)

    return df

def value_repalce_mode(df, identification_method):
    i = 0
    while (i <= df.shape[1]):
        if (identification_method[0] == "y"):
            df[i].replace("", value=(df.mode())[i][0], inplace=True)
        if (identification_method[1] == "y"):
            df.replace(" ", value=(df.mode())[i][0], inplace=True)
        if (identification_method[2] == "y"):
            df.replace("None", value=(df.mode())[i][0], inplace=True)
        if (identification_method[3] != ""):
            customize_value = identification_method[3]
            df.replace(customize_value, value=(df.mode())[i][0], inplace=True)
    return df

#convert messing value as three standard derivation
def value_repalce_3std(df, identification_method):
    i = 0
    while (i <= df.shape[1]):
        if (identification_method[0] == "y"):
            df[i].replace("", value= 3 * df[i].std(), inplace=True)
        if (identification_method[1] == "y"):
            df.replace(" ", value= 3 * df[i].std(), inplace=True)
        if (identification_method[2] == "y"):
            df.replace("None", value= 3 * df[i].std(), inplace=True)
        if (identification_method[3] != ""):
            customize_value = identification_method[3]
            df.replace(customize_value, value= 3 * df[i].std(), inplace=True)

    return df




    return df



'''
    # Finding missing values
    df.isnull().sum()
    # Dropping missing values
    df.dropna(inplace=True)
    # Filling missing values with a specific value
    df.fillna(value=0, inplace=True)


    # Detecting outliers using Z-Score method
    z_scores = stats.zscore(df)
    abs_z_scores = np.abs(z_scores)
    filtered_entries = (abs_z_scores < 3).all(axis=1)
    df = df[filtered_entries]


    # Finding duplicate values
    df.duplicated().sum()
    # Dropping duplicate values
    df.drop_duplicates(inplace=True)


    # Converting data types
    df['col_name'] = df['col_name'].astype('int')
    # Standardizing data
    scaler = StandardScaler()
    df[['col1', 'col2', 'col3']] = scaler.fit_transform(df[['col1', 'col2', 'col3']])
    # Encoding categorical data
    encoder = LabelEncoder()
    df['category_col'] = encoder.fit_transform(df['category_col'])



    return 'Dataset processed successfully.'

if __name__ == '__main__':
    app.run(debug=True)
'''