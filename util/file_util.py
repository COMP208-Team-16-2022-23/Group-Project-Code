### This is a utility file for file operations such as file transformation
import os
from io import BytesIO

from google.cloud import storage
from flask import send_file
import pandas as pd
import config


def csv_to_xlsx(filename, temp_path) -> BytesIO:
    # temporary data
    target_xlsx = BytesIO()
    csv = pd.read_csv(temp_path, encoding='utf-8')
    csv.to_excel(target_xlsx, sheet_name=filename, index=False)
    target_xlsx.seek(0)
    return target_xlsx

def xlsx_to_csv(filename, temp_path) -> BytesIO:
    # temporary data
    target_csv = BytesIO()
    xlsx = pd.read_excel(temp_path, encoding='utf-8')
    xlsx.to_csv(target_csv, index=False)
    target_csv.seek(0)
    return target_csv


def xlsx_to_csv_upload(file):
    """
    Convert Excel file (in .xlsx format) to CSV file (in .csv format) and return the transformed file.

    Args:
        file (FileStorage): Input file to be transformed

    Returns:
        file: Transformed file in .csv format
    """
    # Read the Excel file using pandas
    xlsx = pd.read_excel(file)

    # Convert the Excel file to CSV format
    csv = xlsx.to_csv(index=False).encode('utf-8')

    # Convert CSV data to a FileStorage object and return it
    return csv


