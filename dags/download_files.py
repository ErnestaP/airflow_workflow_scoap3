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
    upload_to_s3


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

dag_name = dags_names['download_files']

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
        try:
            Variable.delete("s3_keys")
        except Exception as e:
            Variable.set("s3_keys", '')
        return True

    if len(ftp_and_names['file_names']) > 0:
        start_t = PythonOperator(
            task_id=f'start',
            python_callable=start)

        complete_task = PythonOperator(
            task_id=f'complete',
            python_callable=complete,
            trigger_rule="one_success",
            provide_context=True)

        my_trigger_task = TriggerDagRunOperator(
            task_id='my_trigger_task',
            trigger_dag_id=dags_names['unzip_files'])

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
                python_callable=upload_to_s3,
                op_kwargs={
                    'download_task_id': f'download_file{index}'},
                provide_context=True)

            start_t >> t1 >> t2 >> complete_task >> my_trigger_task
