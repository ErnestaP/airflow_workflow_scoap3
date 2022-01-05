import airflow
from airflow.models import Variable
from airflow import DAG
from airflow.operators.python_operator import PythonOperator
from airflow.operators.dagrun_operator import TriggerDagRunOperator

import os
from datetime import date, timedelta

from helpers.create_dir import create_dir
from helpers.constants import UNZIPPED_FILES_FOLDER, DOWNLOADED_FILES_FOLDER, DUMMY_FILES_SUB_KEY, dags_names, DOWNLOADED_FILES_FROM_S3
from tasks.tasks import start, unzip
from helpers.collect_files_from_folders import collect_files_from_folders
from tasks.tasks import download_files_from_s3, complete, clean


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
# exampleee
dag_name = dags_names['unzip_files']
with DAG(dag_name,  # Dag id
         default_args=default_args,
         # Cron expression, here it is a preset of Airflow, @daily means once every day.
         schedule_interval='@daily',
         render_template_as_native_obj=True
         ) as dag:

    try:
        Variable.get("s3_keys")
    except Exception as e:
        Variable.set("s3_keys", '')
    # creating a folder, where unzipped files wil be stored
    create_dir(os.getcwd(), UNZIPPED_FILES_FOLDER)

    path_to_downloaded_files = os.path.join(
        os.getcwd(), DOWNLOADED_FILES_FOLDER)
    # starting point
    start_t = PythonOperator(
        task_id=f'start',
        python_callable=start)

    s3_keys_string = Variable.get("s3_keys")
    s3_keys = s3_keys_string.split(',')  # need to remove empty string

    # the dag will be trigggered when at least one task from parent dag will be succeeded
    complete_task = PythonOperator(
        task_id=f'complete',
        python_callable=complete,
        trigger_rule="one_success",
        provide_context=True)

    my_trigger_task = TriggerDagRunOperator(
        task_id='my_trigger_task',
        trigger_dag_id=dags_names['parse'])

    for index, s3_key in enumerate(s3_keys):
        grouping_folder = DUMMY_FILES_SUB_KEY
        file_name = s3_key.split('/')[-1]
        full_path = os.path.join(
            os.getcwd(), DOWNLOADED_FILES_FROM_S3, file_name)

        t3 = PythonOperator(
            task_id=f'download_file_from_s3_{index}',
            python_callable=download_files_from_s3,
            op_kwargs={'s3_key': s3_key},
            provide_context=True)

        t4 = PythonOperator(
            task_id=f'unzip_files{index}',
            python_callable=unzip,
            op_kwargs={'s3_key': s3_key},
            provide_context=True)

        t5 = PythonOperator(
            task_id=f'delete_from_downloads{index}',
            python_callable=clean,
            op_kwargs={'file_path': full_path},
            provide_context=True)

        start_t >> t3 >> t4 >> t5 >> complete_task >> my_trigger_task
