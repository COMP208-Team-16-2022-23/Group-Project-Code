# -*- coding = utf-8 -*-
# @Time: 2023/3/9 14:48
# @File: file_manager.PY
from io import BytesIO

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


def download_to_memory(src_path, bucket_name=config.BUCKET_NAME) -> BytesIO:
    """Downloads a blob from the bucket and store in memory"""
    # todo verification
    file_data = BytesIO()
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(src_path)
        blob.download_to_file(file_data)
        file_data.seek(0)
        return file_data
    except Exception as e:
        return None


def download_for_embedding(src_path, dest_path='', bucket_name=config.BUCKET_NAME):
    """
    Download file from Cloud temporarily and respond file name and file data
    :return: file name and file data in memory
    """
    temp_path = download_to_memory(src_path, bucket_name)
    if dest_path:
        filename = dest_path
    return filename, temp_path


def download_with_response(src_path, dest_path='', bucket_name=config.BUCKET_NAME):
    """Download file from Cloud and respond"""
    filename, file_data = download_for_embedding(src_path, dest_path, bucket_name)
    return send_file(file_data, as_attachment=True, download_name=filename)


def list_blobs(bucket_name=config.BUCKET_NAME, prefix=''):
    """
    Lists all the blobs in the bucket.
    :param bucket_name: name of the bucket
    :param prefix: prefix of the blob name
    :return: list of blobs
    """
    try:
        processed_blob_list = []
        blob_list = storage_client.list_blobs(bucket_name, prefix=prefix)
        for blob in blob_list:
            processed_blob_list.append(
                {'file_path': blob.name,
                 'file_name': blob.name.split('/')[-1],
                 'date_modified': str(blob.updated).split('.')[0],
                 'id': str(blob.id).split('/')[-1]
                 })
        return processed_blob_list
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
        blobs_name_list = [blob['base_name'] for blob in blobs]
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

        blob.delete()

        print('Blob {} deleted.'.format(path))
    except:
        return False

# def check_folder_exists(folderPath, bucket):
#     """ check if path/file exists in bucket or not in google storage """
#     stats = storage.Blob(bucket=bucket, name=folderPath).exists(storage_client)
#     return stats
