# -*- coding = utf-8 -*-
# @Time: 2023/3/9 14:48
# @File: file_manager.PY
import io
import os

from flask import send_file
from google.cloud import storage

import config

storage_client = storage.Client.from_service_account_json(config.GOOGLE_APPLICATION_CREDENTIALS)


def upload_blob(file, blob_name, bucket_name=config.BUCKET_NAME, public=False, prefix=''):
    """Uploads a file to the bucket."""
    # todo limit size of files
    try:
        # md5_hash = hashlib.md5(filepath.read_bytes())  # nosec
        # blob.md5_hash = base64.b64encode(md5_hash.digest()).decode()
        if prefix:
            # blob_name = os.path.join(prefix, blob_name)
            blob_name = prefix + '/' + blob_name
        blob = storage_client.bucket(bucket_name).blob(blob_name)
        blob.upload_from_file(file)
        if public:
            blob.make_public()
        return blob_name
    except Exception as e:
        return False


def delete_blob(blob_name, bucket_name=config.BUCKET_NAME):
    """Deletes a blob from the bucket."""
    try:
        blob = storage_client.bucket(bucket_name).blob(blob_name)
        blob.delete()
    except:
        return False


def download_as_temp(src_path, dest_path, bucket_name=config.BUCKET_NAME):
    """Downloads a blob from the bucket and store in disk temporary"""
    # todo verification
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(src_path)
        blob.download_to_filename(dest_path)
        return dest_path
    except Exception as e:
        return None


def download_for_embedding(src_path, dest_path='', bucket_name=config.BUCKET_NAME) -> [str | io.BytesIO]:
    """
    Download file from Cloud temporarily and respond file name and file data
    :return: file name and file data in memory
    """
    filename = src_path.split('/')[-1]
    temp_path = config.TEMP_PATH + '/' + filename
    download_as_temp(src_path, temp_path, bucket_name)
    #  fetch file data into memory
    file_data = io.BytesIO()
    with open(temp_path, 'rb') as f:
        file_data.write(f.read())
    file_data.seek(0)
    os.remove(temp_path)
    if dest_path:
        filename = dest_path
    return filename, file_data


def download_with_response(src_path, dest_path='', bucket_name=config.BUCKET_NAME):
    """Download file from Cloud and respond"""
    filename, file_data = download_for_embedding(src_path, dest_path, bucket_name)
    response = send_file(file_data, as_attachment=True, download_name=filename)
    return response


def list_blobs(bucket_name=config.BUCKET_NAME, prefix=''):
    """
    Lists all the blobs in the bucket.
    :param bucket_name: name of the bucket
    :param prefix: prefix of the blob name
    :return: list of blobs
    """
    try:
        return storage_client.list_blobs(bucket_name, prefix=prefix)
    except Exception as e:
        return False


def list_blobs_names(bucket_name=config.BUCKET_NAME, prefix=''):
    """
    Lists all the blobs name in the bucket.
    :param bucket_name: name of the bucket
    :param prefix: prefix of the blob name
    :return: list of blobs name
    """
    try:
        blobs = list_blobs(bucket_name=bucket_name, prefix=prefix)
        blobs_name_list = []
        for blob in blobs:
            if blob.name.replace(prefix + '/', ""):  # remove empty string
                blobs_name_list.append(blob.name.replace(prefix + '/', ""))
        return blobs_name_list
    except Exception as e:
        return False


# reference to https://github.com/faizan170/google-cloud-storage-flask.git
# not tested
def create_bucket(bucket_name="checkma"):
    """Creates a new bucket."""
    try:
        bucket = storage_client.create_bucket(bucket_name)
        print('Bucket {} created'.format(bucket.name))
        return True
    except:
        return False


def create_folder(path, bucket):
    """ Create a new folder """
    try:
        if path[-1] != "/":
            path += "/"
        blob = bucket.blob(path)

        blob.upload_from_string('', content_type='application/x-www-form-urlencoded;charset=UTF-8')
        return True
    except:
        return False


def delete_folder(path, bucket):
    """ Delete a folder """
    try:
        if path[-1] != "/":
            path += "/"
        blob = bucket.blob(path)

        blob = bucket.blob(path)

        blob.delete()

        print('Blob {} deleted.'.format(path))
    except:
        return False

# def check_folder_exists(folderPath, bucket):
#     """ check if path/file exists in bucket or not in google storage """
#     stats = storage.Blob(bucket=bucket, name=folderPath).exists(storage_client)
#     return stats
