import os
import datetime

import requests
import pandas as pd

APP_ID = '5e9cc582'
APP_KEY = 'a19391efced0d83ae86dd7e452060b10'

CURRENT_DATE = datetime.date.today()

if not os.environ['AIRFLOW_HOME']:
    os.environ['AIRFLOW_HOME'] = f'{os.getenv('HOME')}/airflow'

AIRFLOW_HOME = os.getenv('AIRFLOW_HOME')

def get_category():
    """Création de la liste des secteurs d'activité"""
    response = requests.get('https://api.adzuna.com/v1/api/jobs/fr/categories?'
                            f'app_id={APP_ID}&app_key={APP_KEY}')

    return response.json()['results']

def get_jobs_listing(page_number, category):
    """Requête qui récupère toutes les offres d'emploi en France"""

    response = requests.get(f'https://api.adzuna.com/v1/api/jobs/fr/search/{page_number}?'
                            f'app_id={APP_ID}&app_key={APP_KEY}&results_per_page=50&category={category}')

    return response.json()['results']

def get_jobs_dict(jobs_list, jobs_dict):
    """Mets dans un dictionnaire les informations qui nous intéresse sur les offres d'emploi"""

    for job in jobs_list:

        data = {
                'title': job.get('title'),
                'company': job['company'].get('display_name'),
                'location': job['location'].get('display_name'),
                'category': job['category'].get('label'),
                'description': job.get('description'),
                'created': job.get('created'),
                'salary_max': job.get('salary_max'),
                'salary_min': job.get('salary_min'),
                'contract_type': job.get('contract_type'),
                'longitude': job.get('longitude'),
                'latitude': job.get('latitude')
                }
        jobs_dict.append(data)


def data_to_csv(data):
    """Crée un fichier CSV contenant les offres d'emploi"""

    df = pd.DataFrame(data)
    df.to_csv(f'{AIRFLOW_HOME}/data/to_ingest/bronze/adzuna/adzuna_{CURRENT_DATE}.csv', mode='a', index=False,
              header= not os.path.exists(f'adzuna_{CURRENT_DATE}.csv'))

    return print(f'Offres enregistrées dans adzuna_{CURRENT_DATE}.csv')


def main():
    jobs_data = []
    category = get_category()

    for cat in category:
        page_num = 1
        print(cat.get('label'),'\n')
        reconnection = 0

        while page_num <= 100 and reconnection <= 10:
            try:
                print(f'--Page : {page_num}--\n')
                get_jobs_dict(get_jobs_listing(page_num, cat.get('tag')), jobs_data)
                page_num += 1
                reconnection = 0
            except:
                reconnection += 1
                print(f'Reconnexion {reconnection}/10...')

        if reconnection > 10:
            data_to_csv(jobs_data)
            print('Fin de la collecte')
            break

        data_to_csv(jobs_data)

