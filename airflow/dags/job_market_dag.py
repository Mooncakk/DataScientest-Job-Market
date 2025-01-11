import os
from datetime import timedelta

from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.providers.docker.operators.docker import DockerOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.dates import days_ago
from docker.types import Mount

from adzuna_scripts.adzuna_data_collection import main as adzuna_get_data

from france_travail_scripts.transform import update_csv
from france_travail_scripts.load import main as load_main


if not os.environ['AIRFLOW_HOME']:
    os.environ['AIRFLOW_HOME'] = f'{os.getenv('HOME')}/airflow'

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

with DAG(
    dag_id='data_processing',
    description='traitement des données',
    tags=['datascientest'],
    schedule=timedelta(days=1),
    start_date=days_ago(0),
    catchup=False,
    default_args={
        'owner': 'admin',
    }
) as dag:

    init_=DummyOperator(
        task_id='init',
    )

    adzuna_extract=PythonOperator(
        task_id='adzuna_data_extraction',
        python_callable=adzuna_get_data,
    )

    france_travail_extract = DockerOperator(
            task_id='france_travail_data_extraction',
            image='aurel_extract_dock:v3',
            auto_remove='success',
            mounts=[
                Mount(source=f'{AIRFLOW_HOME}/data/france_travail_ressources/api_key', target='/app/api_key',
                      type='bind'),
                Mount(source=f'{AIRFLOW_HOME}/data/to_ingest/bronze/france_travail',
                      target='/app/data',
                      type='bind'),
                Mount(source=f'{AIRFLOW_HOME}/dags/france_travail_scripts',
                      target='/app/script',
                      type='bind'),
            ]
        )

    adzuna_data_transform = DockerOperator(
        task_id='data_transform',
        image='mooncak/adzuna_data_transform:1.0',
        auto_remove='success',
        network_mode='airflow_project_network',
        mounts=[
            Mount(source=f'{AIRFLOW_HOME}/data/to_ingest/bronze/adzuna', target='/adzuna/data', type='bind'),
            Mount(source=f'{AIRFLOW_HOME}/dags/adzuna_scripts', target='/adzuna/script', type='bind'),
        ],
    )

    france_travail_transform = PythonOperator(
        task_id='france_travail_data_transform',
        python_callable=update_csv
    )



init_ >> [france_travail_extract, adzuna_extract]
adzuna_extract >> adzuna_data_transform
france_travail_extract >> france_travail_transform
