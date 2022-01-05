import airflow
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator
from airflow.models import Variable

import os
from datetime import timedelta

from helpers.create_dir import create_dir
from helpers.constants import DOWNLOADED_FILES_FOLDER, dags_names
from tasks.tasks import get_ftp_host_and_files_names_to_download,\
    download_file, \
    complete, \
    upload_to_s3_full, \
    download_files_from_s3, \
    unzip_full, \
    parse_files, \
    reset_task_status
from helpers.constants import UNZIPPED_FILES_FOLDER, DOWNLOADED_FILES_FOLDER, DUMMY_FILES_SUB_KEY, dags_names, DOWNLOADED_FILES_FROM_S3


default_args = {
    'owner': 'airflow',
    'depends_on_past': False,
    'start_date': airflow.utils.dates.days_ago(0),
    'email': ['airflow@example.com'],
    'email_on_failure': False,
    'email_on_retry': False,
    'retries': 1,
    'retry_delay': timedelta(minutes=1),
}

dag_name = dags_names['full_pipeline']

with DAG(dag_name,  # Dag id
         default_args=default_args,
         # Cron expression, here it is a preset of Airflow, @daily means once every day.
         schedule_interval='@daily',
         render_template_as_native_obj=True
         ) as dag:

    groups = []
    create_dir(os.getcwd(), DOWNLOADED_FILES_FOLDER)
    ftp_and_names = get_ftp_host_and_files_names_to_download()

    def start():
        return True

    if len(ftp_and_names['file_names']) > 0:
        start_t = PythonOperator(
            task_id=f'start',
            python_callable=start)

        for index, file_path in enumerate(ftp_and_names['file_names']):
            t1 = PythonOperator(
                task_id=f'download_file{index}',
                python_callable=download_file,
                op_kwargs={
                    'dag_name': dag_name,
                    'file_path': file_path,
                    'ftp_host': ftp_and_names["ftp_host"],
                    'task_id': f'download_file{index}'},
                provide_context=True)

            file_name = os.path.basename(file_path)
            grouping_folder = os.path.basename(os.path.dirname(file_path))

            t2 = PythonOperator(
                task_id=f'upload_files{index}',
                python_callable=upload_to_s3_full,
                op_kwargs={
                    'task_id': f'upload_file{index}',
                    'download_task_id': f'download_file{index}'},
                provide_context=True)

            upload_task_id = f'upload_file{index}'
            try:
                Variable.get(f"{upload_task_id}_s3_key")
            except Exception as e:
                Variable.set(f"{upload_task_id}_s3_key", '')

            s3_key = Variable.get(f"{upload_task_id}_s3_key")
            t3 = PythonOperator(
                task_id=f'download_file_from_s3_{index}',
                python_callable=download_files_from_s3,
                op_kwargs={'s3_key': s3_key},
                provide_context=True)

            unzipped_task_id = f'unzip_files{index}'
            try:
                Variable.get(f"{unzipped_task_id}_unzipped_files_path")
            except Exception as e:
                Variable.set(f"{unzipped_task_id}_unzipped_files_path", '')

            t4 = PythonOperator(
                task_id=unzipped_task_id,
                python_callable=unzip_full,
                op_kwargs={
                    'task_id': unzipped_task_id,
                    's3_key': s3_key},
                provide_context=True)

            path_to_unzipped_files_string = Variable.get(
                f"{unzipped_task_id}_unzipped_files_path")
            start_t >> t1 >> t2 >> t3 >> t4

            path_to_unzipped_files = path_to_unzipped_files_string.split(',')

            task_ids = []
            for index_parse, unzipped_file_path in enumerate(path_to_unzipped_files):
                grouping_folder = os.path.basename(
                    os.path.dirname(file_path))
                file_name = os.path.basename(file_path)
                task_ids.append(f'parse_files_{index}_{index_parse}')
                t5 = PythonOperator(
                    task_id=f'parse_files_{index}_{index_parse}',
                    python_callable=parse_files,
                    op_kwargs={'file_path': unzipped_file_path},
                    provide_context=True)
                t4 >> t5 

                
            t6 = PythonOperator(
                    task_id=f'reset_{index}',
                    python_callable=reset_task_status,
                    op_kwargs={'dag_name':  dag_name,
                               'task_ids': task_ids},
                    provide_context=True)

            t5 >> t6
