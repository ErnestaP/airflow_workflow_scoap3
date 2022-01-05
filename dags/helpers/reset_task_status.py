from airflow.models import  DagBag, TaskInstance
from airflow import  settings, configuration as conf

import os
import logging


def resetTasksStatus(dag_name, task_ids, execution_date):
    '''
    I need reset status of the task, which is branches out of zip func.
    It doesn't start because it marked as removed
    https://www.linkedin.com/pulse/dynamic-workflows-airflow-kyle-bridenstine/
    '''
    dag_folder = conf.get('core', 'DAGS_FOLDER')
    dagbag = DagBag(dag_folder)
    check_dag = dagbag.dags[dag_name]
    session = settings.Session()
    for task_id in task_ids[1:len(task_ids)]:
        my_task = check_dag.get_task(task_id)
        ti = TaskInstance(my_task, execution_date)
        state = ti.current_state()
        if state is not 'success':
            logging.info("Current state of " + task_id + " is " + str(state))
            ti.set_state(None, session)
            state = ti.current_state()
            logging.info("Updated state of " + task_id + " is " + str(state))
        return True