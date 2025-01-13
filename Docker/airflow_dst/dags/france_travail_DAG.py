from airflow import DAG
import os
from datetime import timedelta, datetime
from airflow.providers.docker.operators.docker import DockerOperator
from docker.types import Mount


# Rappel : le scheduler de Airflow lance le DAG quand 1 schedule interval s'est passé depuis la start_date au minmmum. Ex : si je veux faire dérouler un DAG de façon daily et que ma start date est today, il sera lancé pour la premiere fois demain


etl = DAG(
    dag_id='ETL_france_travail',
    description='Daily Run of france travail job offers',
    tags=['france_travail', 'scraping',"ETL"],
    schedule_interval='@daily',
    default_args={
        'owner': 'Aurelien_claux',
        'start_date': datetime(2025, 1, 1),
    }
)


extract_france_travail_task = DockerOperator(
    task_id="extract_france_travail",
    image="aurelclx/extract_france_travail:latest",
    mounts=[Mount(
        source=os.path.join(os.getcwd(), "data"), 
        target="/app/data", 
        type="bind"
        )
    ],
    auto_remove=True,
    api_version='auto',
    dag=etl
)