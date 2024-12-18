from fastapi import FastAPI
#from typing_extensions import Annotated, Literal, Optional, List
from pydantic import BaseModel
from fastapi.responses import JSONResponse
import load


app = FastAPI()

def create_connexion():
    conn = load.postgres_bdd_auth(database="jobmarket",
                                host="localhost",
                                user="postgres",
                                password="postgres",
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
    conn = create_connexion()
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
    conn = create_connexion()
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
    conn = create_connexion()
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
    conn = create_connexion()
    cur_city = load.get_most_recruiting_city_with_code_rome(conn, code_rome)
    city_list = []
    for city in cur_city:
        city_list.append({
        "Ville": city[1],
        "Nombre_Offre": city[2]
        })
    return JSONResponse(content = city_list)


