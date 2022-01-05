import airflow
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python_operator import PythonOperator

import os
from datetime import date, timedelta
from helpers.create_dir import create_dir
from helpers.collect_files_from_folders import collect_files_from_folders
from helpers.constants import UNZIPPED_FILES_FOLDER, PARSED_JSONS, DOWNLOADED_FILES_FROM_S3
from tasks.tasks import start,\
    complete,\
    parse_files, \
    complete, \
    clean


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

dag_name = "parse_dag"

with DAG("parse_dag",  # Dag id
         default_args=default_args,
         # Cron expression, here it is a preset of Airflow, @daily means once every day.
         schedule_interval='@daily',
         render_template_as_native_obj=True
         ) as dag:

    complete_task = PythonOperator(
        task_id=f'complete',
        python_callable=complete,
        trigger_rule="one_success",
        provide_context=True)

    # folder, where downloaded from s3 files will be stored
    create_dir(os.getcwd(), DOWNLOADED_FILES_FROM_S3)
    # folder, where parsed files will be stored
    create_dir(os.getcwd(), PARSED_JSONS)

    # path_to_unzipped_files_string = Variable.get("unzipped_files_paths")
    # path_to_unzipped_files= path_to_unzipped_files_string.split(',')
    path_to_unzipped_files = os.path.join(os.getcwd(), UNZIPPED_FILES_FOLDER)
    grouping_folders = os.listdir(path_to_unzipped_files)
    files_full_paths = []

    for grouping_folder_ in grouping_folders:
        path_to_files = os.path.join(path_to_unzipped_files, grouping_folder_)
        file_names = os.listdir(path_to_files)
        for name in file_names:
            files_full_paths.append(os.path.join(path_to_files, name))

    def start1():
        print(files_full_paths, grouping_folders, os.getcwd())
        return True

    start_t = PythonOperator(
        task_id=f'start',
        python_callable=start1)

    if len(files_full_paths) > 0:
        for index, file_path in enumerate(files_full_paths):
            grouping_folder = os.path.basename(os.path.dirname(file_path))
            file_name = os.path.basename(file_path)

            t6 = PythonOperator(
                task_id=f'parse_files{index}',
                python_callable=parse_files,
                op_kwargs={'file_path': file_path},
                provide_context=True)
            t7 = PythonOperator(
                task_id=f'delete_from_downloads{index}',
                python_callable=clean,
                op_kwargs={'file_path': file_path},
                provide_context=True)
            t8 = PythonOperator(
                task_id=f'complete_{index}',
                python_callable=complete,
                op_kwargs={
                    'dag_name': dag_name,
                    'task_id': f'complete_{index}'},
                provide_context=True)

            start_t >> t6 >> t7 >> t8 >> complete_task
