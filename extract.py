from random import choice

import requests
from selectolax.lexbor import LexborHTMLParser
from playwright.sync_api import sync_playwright
import pandas as pd


BASE_URL = 'https://fr.indeed.com'
JOBS_BASE_URL = 'https://fr.indeed.com/viewjob?jk='
URL = 'https://fr.indeed.com/jobs?q=emploi&l=france'


def get_headers_list():
    """Création d'une liste de user-agent"""

    SCRAPEOPS_URL = 'http://headers.scrapeops.io/v1/browser-headers?api_key='
    SCRAPEOPS_API_KEY = 'cf7a2b31-4c25-412c-bd51-5bdcc030a9d4'
    response = requests.get(SCRAPEOPS_URL + SCRAPEOPS_API_KEY)
    headers_list = response.json().get('result')

    return headers_list


def get_headers(headers_list):
    """Selection d'un user-agent"""

    return choice(headers_list)


headers_list = get_headers_list()
headers = get_headers(headers_list)


def get_jobs_sector():

    """recupérer les secteurs d'activité et leur code dans un dictionaire"""

    user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/111.0.0.0 Safari/537.36'

    with sync_playwright() as pw:

        browser = pw.firefox.launch()
        browser.new_context(user_agent=user_agent)
        page = browser.new_page()
        page.goto(URL)
        page.wait_for_load_state('networkidle')
        page.get_by_role("button", name="Secteurs filter").click()
        page_content = LexborHTMLParser(page.content())
        browser.close()

    sector_codes = page_content.css('.css-1gcq455')
    sector_names = page_content.css('.css-kmxpa3')
    jobs_sectors = {}

    for sector_name, sector_code in zip(sector_names, sector_codes):
        jobs_sectors[sector_name.text()] = sector_code.attributes['value']

    return jobs_sectors


def get_page(url):
    """recupère le contenu de la page"""""

    proxy_param = {
            'api_key': 'cf7a2b31-4c25-412c-bd51-5bdcc030a9d4',
            'url': url
            }

    proxies = {'http': 'http://brd-customer-hl_47ba7ac8-zone-residential_proxy1-country-fr:7ttmv9pcs4v2@brd.superproxy.io:22225',
            'https': 'http://brd-customer-hl_47ba7ac8-zone-residential_proxy1-country-fr:7ttmv9pcs4v2@brd.superproxy.io:22225'}
    response = requests.get('https://proxy.scrapeops.io/v1/', headers=headers, params=proxy_param)

    while response.status_code != 200:
        print(f'Status Code {response.status_code}\n'
              f'Nouvel essai...')
        response = requests.get('https://proxy.scrapeops.io/v1/', headers=headers, params=proxy_param)

    page = LexborHTMLParser(response.text)

    return page


def get_job_url(page_content):
    """Récupère l'id de l'offre d'emploi et retourne l'url de l'offre"""

    jobs_url = []
    job_id = page_content.css('ul li h2 a')
    for id in job_id:
        job_url = JOBS_BASE_URL+id.attributes['data-jk']
        jobs_url.append(job_url)

    return jobs_url


def get_job_infos(page_content):
    """Récupère les infos de l'offre d'emploi dans un dictionnaire"""

    job_infos = {'titre_offre': page_content.css_first('.jobsearch-JobInfoHeader-title span').text(),
                 'compagnie': page_content.css_first('.css-1ioi40n').text(deep=False),
                 'lieu': page_content.css_first('.css-45str8 span').text()}
    return job_infos


def get_next_page(page_content):
    """"Récupère le lien de la page suivante"""

    if page_content.css('.css-akkh0a')[-1].attributes['data-testid']=='pagination-page-next':
        next_page_url = page_content.css('.css-akkh0a')[-1].attributes['data-testid']
        return BASE_URL+next_page_url

def  create_csv(data):
    """Crée un fichier csv en prenant en entrée les infos des offres emplois"""

    df = pd.DataFrame(data)
    df.to_csv('indeed_jobs.csv', index=False)




if __name__=='__main__':

    jobs_sectors_infos = get_jobs_sector()
    all_jobs_infos = []

    for sector_name in jobs_sectors_infos:
        sector_code = jobs_sectors_infos[sector_name]
        url = f'https://fr.indeed.com/emplois?q=emploi&l=France&sc=0kf%3Acmpsec%28{sector_code}%29%3B'
        pagination = True

        while pagination:
            page = get_page(url)
            jobs_url = get_job_url(page)

            for url in jobs_url:
                job_page = get_page(url)
                job_infos = get_job_infos(job_page)
                job_infos['secteur'] = sector_name
                all_jobs_infos.append(job_infos)

            if get_next_page(page):
                next_ = get_next_page(page)
                page = get_page(next_)
            else:
                pagination = False

    create_csv(all_jobs_infos)

