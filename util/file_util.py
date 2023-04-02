### This is a utility file for file operations such as file transformation
import os
from io import BytesIO

from google.cloud import storage
from flask import send_file
import pandas as pd
from xhtml2pdf import pisa
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


def add_suffix(file_path, suffix, username, folder_name="", ext=""):
    """
    Add suffix to the filename.

    Args:
        file_path (str): Path of the file
        suffix (str): Suffix to be added
        username (str): Username of the user
        folder_name (str): Name of the folder
        ext (str): Extension of the file

    Returns:
        str: Filename with suffix
    """

    # file path: username/some_folder/file_name.csv
    # remove "username/"
    file_path = file_path.split('/', 1)[-1]  # ('/', 1) means split once

    # Split the filename into name and extension
    if not ext:
        name, ext = os.path.splitext(file_path)
    else:
        name, _ = os.path.splitext(file_path)

    # Add suffix to the filename
    if folder_name:
        file_path = username + "/" + folder_name + "/" + name + "-" + suffix + ext
    else:
        file_path = username + "/" + name + "-" + suffix + ext

    return file_path


def convert_to_pdf(html_file):
    bytes_io = BytesIO()
    pisa.CreatePDF(html_file, dest=bytes_io)
    return bytes_io
