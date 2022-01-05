import os
from  helpers.constants import DOWNLOADED_FILES_FOLDER

from  helpers.connect_to_ftp import connect_to_ftp
from  helpers.collect_files import collect_files
from  helpers.download_file_from_ftp import download_file_from_ftp
from  helpers.unzip_files import unzip_files
from helpers.unzip_files_full import unzip_files_full as unzip_files_full_helper
from  helpers.download_from_s3 import download_file_from_s3
from  helpers.parse_files import crawler_parser
from  helpers.upload_to_s3 import upload_to_s3 as upload_to_s3_helper
from  helpers.constants import DOWNLOADED_FILES_FROM_S3, PARSED_JSONS
from  helpers.upload_to_s3_full import upload_to_s3_full as upload_to_s3_full_helper
from helpers.reset_task_status import resetTasksStatus

def start():
    return True


def complete():
    return True


def get_ftp_host_and_files_names_to_download():
    ftp_host = connect_to_ftp()
    file_names = collect_files(ftp_host)
    return({'ftp_host': ftp_host, 'file_names': file_names})

def download_file(file_path, ftp_host, task_id,  **context):
    downloaded_file_name = download_file_from_ftp(ftp_host, file_path)
    context['ti'].xcom_push(key=task_id, value=downloaded_file_name)

def unzip(s3_key):
    file_name = s3_key.split('/')[-1]
    files = unzip_files(file_name)
    return files

def unzip_full(task_id, s3_key):
    file_name = s3_key.split('/')[-1]
    files = unzip_files_full_helper(task_id, file_name)
    return files

def clean(file_path):
    os.remove(file_path)

def download_files_from_s3(s3_key, **kwargs):
    download_file_from_s3(s3_key)

def upload_to_s3(download_task_id, **kwargs):
    upload_to_s3_helper(download_task_id, **kwargs)

def upload_to_s3_full(task_id, download_task_id, **kwargs):
    upload_to_s3_full_helper(task_id, download_task_id, **kwargs)

def parse_files(file_path):
    path = os.path.join(os.getcwd(), PARSED_JSONS)
    os.environ['SCOAP_DEFAULT_LOCATION'] = path
    os.environ['HEPCRAWL_BASE_WORKING_DIR'] = path
    crawler_parser(file_path)

    return file_path

def reset_task_status(dag_name, task_ids, **kwargs):
    resetTasksStatus(dag_name, task_ids, kwargs['execution_date'])