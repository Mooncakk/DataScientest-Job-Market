import json

import requests
import pandas as pd

APP_ID = '391724e4'
APP_KEY = '0d06504c0e49c865ff78ca08a2ca3128'

r = requests.get('https://api.adzuna.com/v1/api/jobs/fr/categories?app_id=5e9cc582&app_key=a19391efced0d83ae86dd7e452060b10')


def get_jobs_listing(page_number):
    """Requête qui récupère toutes les offres d'emploi en France"""

    response = requests.get(f'https://api.adzuna.com/v1/api/jobs/fr/search/{page_number}?app_id={APP_ID}'
                            f'&app_key={APP_KEY}&content-type=application/json&results_per_page=50')

    return response.json()['results']


def get_jobs_dict(jobs_list, jobs_dict):
    """Mets dans un dictionnaire les informations qui nous intéresse sur les offres d'emploi"""

    for job in jobs_list:

        data = {'id': job.get('id', ''),
                'title': job.get('title', ''),
                'company': job['company'].get('display_name', ''),
                'location': job['location'].get('area', ''),
                'category': job['category'].get('label', ''),
                'description': job.get('description', ''),
                'created': job.get('created', ''),
                'salary_max': job.get('salary_max', ''),
                'salary_min': job.get('salary_min', ''),
                'contract_type': job.get('contract_type')
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
    df.to_csv('Adzuna_Jobs_listing.csv')

    return print('Fichier Adzuna_Jobs_listing.csv créé')


if __name__ == '__main__':

    jobs_data = []
    collect = True
    page_num = 1

    while collect:
        try:
            print(f'--Page : {page_num}--\n')
            get_jobs_dict(get_jobs_listing(page_num), jobs_data)
            page_num += 1

        except:
            collect = False
            print('Fin de la collecte')

    save_json_file(jobs_data)
    data_to_csv(jobs_data)
