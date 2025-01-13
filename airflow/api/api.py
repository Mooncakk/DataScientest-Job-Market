from fastapi import FastAPI, HTTPException
import psycopg2

#from typing_extensions import Annotated, Literal, Optional, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from scripts import load


app = FastAPI()

def create_connexion():
    conn = load.postgres_bdd_auth(database="jobmarket",
                                host="localhost",
                                user="postgres",
                                password="postgres",
                            port="5432")
    return conn

def create_connexion_to_container():
    conn = load.postgres_bdd_auth(database="france_emplois",
                                host="0.0.0.0",
                                user="admin",
                                password="datascientest",
                                port="5432")
    return conn

@app.get("/france_travail/verify")
async def verify():
    return {"message": "Hello World"}

class Secteur(BaseModel):
    Secteur : str
    CodeNAF : str

@app.get("/france_travail/most_recruiting_sector", name="Retourne les secteurs qui recrutent le plus et le code NAF associé d'après France_Travail", response_model=Secteur)
def get_most_recruiting_sector():
    conn = create_connexion_to_container()
    cur_secteurs = load.get_most_recruiting_sector(conn)
    secteurs_list = []
    for secteur in cur_secteurs:
        secteurs_list.append({
            "secteur": secteur[1],
            "Code Naf": secteur[0]
        })
    return JSONResponse(content=secteurs_list)

class Metier(BaseModel):
    Metier : str
    CodeROME : str

@app.get("/france_travail/most_recruiting_job", name="retourne les métiers qui recrutent le plus et leur code Rome associé, d'après France Travail", response_model=Metier)
def get_most_recruiting_job():
    conn = create_connexion_to_container()
    cur_jobs = load.get_most_recruiting_job(conn)
    jobs_list = []
    for job in cur_jobs:
        jobs_list.append({
            "Metier ": job[1],
            "Code Rome": job[1]
        })
    return JSONResponse(content=jobs_list)

class Ville(BaseModel):
    Ville: str
    Nombre_Offre : str

@app.get("/france_travail/most_recruiting_city", name="Retourne les villes qui recrutent le plus, d'après France Travail", response_model=Ville)
def get_most_recruiting_city():
    conn = create_connexion_to_container()
    cur_city = load.get_most_recruiting_city(conn)
    city_list = []
    for city in cur_city:
        city_list.append({
            "Ville": city[1],
            "Nombre_Offre": city[2]
        })
    return JSONResponse(content=city_list)

@app.get("/france_travail/most_recruiting_city/{code_rome}", name="Retourne les villes qui recrutent le plus selon un code Rome donné, selon France Travail", response_model=Ville)
def get_most_recruiting_city_with_code_rome(code_rome: str):
    conn = create_connexion_to_container()
    cur_city = load.get_most_recruiting_city_with_code_rome(conn, code_rome)
    city_list = []
    for city in cur_city:
        city_list.append({
        "Ville": city[1],
        "Nombre_Offre": city[2]
        })
    return JSONResponse(content = city_list)


def run_query(query):

    conn = psycopg2.connect(
        database="france_emplois",
        host="localhost",
        user="admin",
        password="datascientest",
        port="5432")
    cur = conn.cursor()
    cur.execute(query)

    return cur.fetchall()


@app.get('/nombres-offres-adzuna', name="nombre d'offres dans la table adzuna_offres")
def get_count():
    """Retourne le nombre d'offres dans la table adzuna_offres"""

    number = run_query('SELECT COUNT(*) FROM adzuna_offres')
    return {"nombres d'offres": number}


@app.get('/secteurs', name="secteurs de la table adzuna_offres")
def get_categories():
    """Retourne les différents secteurs de la table adzuna_offres"""

    categories = run_query('SELECT DISTINCT(SECTEUR) FROM adzuna_offres ORDER BY secteur')
    categories_formated = {}

    return categories



@app.get('/secteurs/{secteur_id:int}', name="les offres d'un secteur choisi par l'id")
def get_category(secteur_id):
    """Retourne les offres d'un secteur choisi par l'id"""

    categories = run_query("SELECT DISTINCT(SECTEUR) FROM adzuna_offres ORDER BY secteur")
    categories_formated = {}
    for id_, category in zip(range(len(categories)), categories):
        categories_formated[id_] = category[0]
    try:
        category = run_query(f"SELECT * FROM adzuna_offres WHERE secteur='{categories_formated[secteur_id]}'")
        return category

    except KeyError:
        raise HTTPException(
            status_code=404,
            detail=f"id {secteur_id} inexistant"
        )


@app.get('/offres-par-secteur', name="Nombres d'offres par secteur classeé par ordre décroissant")
def test():
    classment = run_query("SELECT secteur, count(*) FROM adzuna_offres GROUP BY secteur ORDER BY COUNT DESC")
    return classment

@app.get('/salaires-max', name="le salaire max de chaque secteur classé par odre décroissant")
def get_max_salary():
    """Retourne le salaire max de chaque secteur classé par odre décroissant"""

    salary = run_query("SELECT secteur, MAX(salaire_max) as Salaire_max  FROM adzuna_offres "
              "GROUP BY secteur ORDER BY Salaire_max DESC")
    return salary

