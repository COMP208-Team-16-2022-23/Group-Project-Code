import pandas as pd
import numpy as np
from imblearn.under_sampling import RandomUnderSampler
from imblearn.over_sampling import RandomOverSampler
from imblearn.combine import SMOTEENN


# pd_reader = pd.read_csv("../misc/temp/CountyGDP_ECON215.csv")
# print(pd_reader)


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
        "sample_balancing": sample_balancing(df, para_received),
    }.get(filling_method, None)


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


def sample_balancing(df, para_received):
    # Get the target column name and balancing method from parameters
    target_col = para_received['target_col']
    balancing_method = para_received['balancing_method']

    # Separate the target column and features from the dataframe
    y = df[target_col]
    x = df.drop(target_col, axis=1)

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


def standardization(df, para_received):  # Z-score standardization
    # Create a new dataframe with only numerical columns
    num_df = df.select_dtypes(include=[np.number])
    # Create a dictionary to store the standardization parameters

    # Standardize each column
    for col in num_df.columns:
        col_mean = num_df[col].mean()
        col_std = num_df[col].std()
        num_df[col] = (num_df[col] - col_mean) / col_std

    # Merge the standardized numerical columns with the non-numerical columns
    df_std = pd.concat([num_df, df.select_dtypes(exclude=[np.number])], axis=1)

    # Apply the standardization parameters to the received dataframe (if specified)
    if para_received is not None:
        for col, para in para_received.items():
            if col in num_df.columns:
                df_std[col] = (df_std[col] - para["mean"]) / para["std"]

    return df_std


paraset = {'identification_method': ['y', 'y', 'y', ''], 'fill_type': 'normal', }
# process(pd_reader, paraset)
