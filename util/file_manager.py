# -*- coding = utf-8 -*-
# @Time: 2023/3/9 14:48
# @File: file_manager.PY
import os.path

from google.cloud import storage

import config

storage_client = storage.Client.from_service_account_json(config.GOOGLE_APPLICATION_CREDENTIALS)
my_bucket = storage_client.get_bucket(config.BUCKET_NAME)


def upload_blob(file, blob_name, bucket, public=False, prefix=''):
    """Uploads a file to the bucket."""
    # todo limit size of files
    try:
        # md5_hash = hashlib.md5(filepath.read_bytes())  # nosec
        # blob.md5_hash = base64.b64encode(md5_hash.digest()).decode()
        if prefix:
            blob_name = os.path.join(prefix, blob_name)
        blob = bucket.blob(blob_name)
        blob.upload_from_file(file)
        if public:
            blob.make_public()
        return blob_name
    except Exception as e:
        return False


def delete_blob(blob_name, bucket):
    """Deletes a blob from the bucket."""
    try:
        blob = bucket.blob(blob_name)
        blob.delete()
    except:
        return False


def download_blob(source_blob_name, destination_filename, bucket_name):
    """Downloads a blob from the bucket."""
    try:
        bucket = storage_client.get_bucket(bucket_name)
        blob = bucket.blob(source_blob_name.replace('/', '\\'))
        blob.download_to_filename(destination_filename)
        return True
    except Exception as e:
        return False


def list_blobs(bucket_name, parent=''):
    """Lists all the blobs in the bucket."""
    try:
        blobs = storage_client.list_blobs(bucket_name, prefix=parent)
        listData = []
        for blob in blobs:
            listData.append(blob.name.replace(parent + '\\', ""))
        return listData
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
