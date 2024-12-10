import json
import os

import requests
import pandas as pd

APP_ID = '5e9cc582'
APP_KEY = 'a19391efced0d83ae86dd7e452060b10'


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


def save_json_file(data):
    """Crée un fichier JSON contenant les offres d'emploi issu des requêtes vers l'API"""

    with open('Adzuna_Jobs_listing.json', 'a', encoding='utf-8') as jsonfile:
        json.dump(data, jsonfile, indent=4)

    return print('Fichier Adzuna_Jobs_listing.json créé')


def data_to_csv(data):
    """Crée un fichier CSV contenant les offres d'emploi"""

    df = pd.DataFrame(data)
    df.to_csv('Adzuna_Jobs_listing.csv', mode='a', index=False,
              header= not os.path.exists('Adzuna_Jobs_listing.csv'))

    return print('Fichier Adzuna_Jobs_listing.csv créé')


if __name__ == '__main__':

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
            break

        data_to_csv(jobs_data)

    save_json_file(jobs_data)
