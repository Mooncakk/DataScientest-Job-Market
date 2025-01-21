from airflow import DAG
from datetime import timedelta, datetime, date

import os
import sys

from airflow.operators.python import PythonOperator
from airflow.contrib.sensors.file_sensor import FileSensor

sys.path.append('/home/aurellechef/airflow/dags')
import tasks.extract as extract
import tasks.transform as transform
import tasks.load as load


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

sensor_scrapped_offers = FileSensor(
        task_id="check_file_offre",
        fs_conn_id="my_filesystem_connection",
        filepath=f"/home/aurellechef/airflow/dags/data/offres{date.today()}.csv",
        timeout=5 * 30,
        mode='reschedule'
    )

sensor_processed_offers = FileSensor(
        task_id="check_file_offre_processed",
        fs_conn_id="my_filesystem_connection",
        filepath=f"/home/aurellechef/airflow/dags/data/offres{date.today()}_processed.csv",
        timeout=5 * 30,
        mode='reschedule'
    )



extract_france_travail_task = PythonOperator(
    task_id="extract_france_travail",
    python_callable=extract.main,
    dag=etl
)

transform_france_travail_task = PythonOperator(
    task_id="transform_france_travail",
    python_callable=transform.main,
    dag=etl
)

load_france_travail_task = PythonOperator(
    task_id="load_france_travail",
    python_callable=load.main,
    dag=etl
)

extract_france_travail_task >> sensor_scrapped_offers
sensor_scrapped_offers >> transform_france_travail_task
transform_france_travail_task >> sensor_processed_offers
sensor_processed_offers >> load_france_travail_task