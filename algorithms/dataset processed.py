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
    file = request.files['file']
    df = pd.read_csv(file)


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