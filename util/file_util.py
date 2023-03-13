### This is a utility file for file operations such as file transformation
import os
import tempfile

from google.cloud import storage
from flask import send_file
import pandas as pd
import config


def csv_to_xlsx(filename, temp_path):
    csv = pd.read_csv(temp_path, encoding='utf-8')
    csv.to_excel(f'{temp_path}.xlsx', sheet_name=filename, index=False)
    return f'{temp_path}.xlsx'
