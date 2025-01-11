import csv
import os
from datetime import date
import pandas as pd

"""if not os.environ['AIRFLOW_HOME']:
    os.environ['AIRFLOW_HOME'] = f'{os.getenv('HOME')}/airflow'

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')"""
os.environ['AIRFLOW_HOME'] = f'{os.getenv('HOME')}/job_market/airflow'
AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

def update_csv(csv_name=f'{AIRFLOW_HOME}/data/to_ingest/bronze/france_travail/france_travail_{date.today()}.csv'):
    df = pd.read_csv(csv_name, quotechar='|', sep=',')
    df.columns = ['romeCode', 'codeNaf','typeContrat','lieuTravail', 'intitule', 'entreprise', 'dateCreation', 'salaire', 'description']
    df = df.drop_duplicates()
    df['salaire'] = df.salaire.fillna('39800')
    df['entreprise'] = df.entreprise.fillna('NoName')
    df['lieuTravail'] = df.lieuTravail.fillna('00000') 
    df['codeNaf'] = df.codeNaf.fillna('00.00X')
    df.to_csv(f'{AIRFLOW_HOME}/data/to_ingest/silver/france_travail/france_travail_{date.today()}_processed.csv', sep=',', quotechar='|', index=False)

def update_csv_in_container(csv_name=f'data/offres{date.today()}.csv'):
    df = pd.read_csv(csv_name, quotechar='|', sep=',')
    df.columns = ['romeCode', 'codeNaf','typeContrat','lieuTravail', 'intitule', 'entreprise', 'dateCreation', 'salaire', 'description']
    df = df.drop_duplicates()
    df['salaire'] = df.salaire.fillna('39800')
    df['entreprise'] = df.entreprise.fillna('NoName')
    df['lieuTravail'] = df.lieuTravail.fillna('00000') 
    df['codeNaf'] = df.codeNaf.fillna('00.00X')
    df.to_csv(f'data/offres{date.today()}_processed.csv', sep=',', quotechar='|', index=False)

