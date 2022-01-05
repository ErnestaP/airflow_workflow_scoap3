This code implements data harvesting from FTP server.
The are two possible implementations:
1. Workflow consists of 3 sparated DAGs, which trigger each other:
    * a. Connect to FTP, download files, upload to S3;
    * b. Download files from S3 and unzip them;
    * c. Parse unzipped XML files to JSON.

When the at least one task of the last tasks of the DAG is finished successfully, the other DAG is triggered to start a job.
For example: one of the last step tasks in DAG **a** finished successfully, it will tirgger the DAG **b**.

2. Workflow consist of one DAG.
The point number 2 it speaks for its own. All tasks are implemented in one DAG. However, because Airflow doesn't know how many files are in zip file initially, *unzip* tasks is not branched out in the beggining. This is causing an issue, which starts just one brach out of N. Other tasks will be marked as *removed*. For example: branch X splits in Y1 and Y2. Y1 will be ran, howerver Y2 will be marked as **removed** and will never start. In order to solve this problem the tasks is triggered by changing its state to None. This is the first state before scheduling it. More information can be found in [Airflow doc](https://airflow.apache.org/docs/apache-airflow/stable/concepts/tasks.html).


# How to run it?
## Locally
1. Create and activate a virual environment:
```
export PYTHON_VERSION=3.7.12
pyenv install $PYTHON_VERSION
pyenv virtualenv $PYTHON_VERSION workflows
pyenv activate workflows
```
2. Install rquired dependencies:
```
pip install -r requirements.txt
```
3. Set AIRFLOW_HOME variable to the path where this project is cloned:
```
export AIRFLOW_HOME=/full/path/of/the/project
```
4. Run the airflow:
```
airflow standalone
```
5. The airflow server will run on http://locahost:8080

All DAGs, should be placed in /dags folder and cannot be places inside the functions or classes. The visibility scope is at the top level. More information can be found in [Airflow doc](https://airflow.apache.org/docs/apache-airflow/stable/concepts/dags.html#loading-dags).Otherwise they won't be visible in Airflow UI. Also, exporting AIRFLOW_HOME with **the correct path** is extremely important! This variable indicates from where DAGs should be imported to UI.

## In Docker
The simpliest way to run an Airflow workflow just by using docker-compose:
```
docker-compose up
```

# How does it work?
To start a workflow, first need to activate it. Find the you desired DAG in the list of DAGs in the UI and click on slider, to activate it. In order to trigger it, click the *play* button on the right side of the DAG name.

To follow the process, select the activated dag, it will open a windown with where all tasks and their state are listed.

## How to rerun a task?
1. select a DAG, where is the desired task;
2. select a desired task;
3. clear its state;
4. now task is marked as "not ran yet". Click on it;
5. run a task again;

