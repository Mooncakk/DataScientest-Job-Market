import psycopg2
import extract
import pprint
from datetime import date

#TODO : Transformer le main en fonction

def postgres_bdd_auth(database, host, user, password, port):
    try:
        conn = psycopg2.connect(database=database,
                                host=host,
                                user=user,
                                password=password,
                                port=port)
        print(f"Vous êtes connectés à postgres sur la bd \"{database}\" et le port \"{port}\"")
    except Exception as e:
        print(f"Erreur: {e}")
    return conn

def create_cursor(conn):
    try:
        return conn.cursor()
    except Exception as e:
        print(f"Erreur: {e}")
    

def load_metier(conn, cur):
    """ Charge le réferentiel des métiers (code ROME) dans la table Metier"""
    try:
        for metier in extract.getall_code_rome():
            cur.execute(f"INSERT INTO METIER (code_rome, libelle) VALUES (%s,%s)", (metier.get('code') ,metier.get('libelle')))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans Metier : {e}")
        conn.rollback()
    finally:
        conn.close()

def load_commune(conn, cur):
    """ Charge le réferentiel Communes dans la table Commune"""
    try:
        # Listes des codes hors référentiels
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('00000', 00000, 'Noname', '000'))
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('75056', 75000, 'Paris', '75'))
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('69152', 69310, 'Paris', '75'))
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('13055', 13000, 'Marseille', '13'))
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('69123', 69000, 'Lyon', '69'))
        for commune in extract.getall_communes():
            cur.execute("SELECT 1 FROM Commune WHERE code_commune = %s", (commune.get('code'),))
            exists = cur.fetchone()
            if not exists:
                cur.execute(
                    "INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",
                    (commune.get('code'), commune.get('codePostal'), commune.get('libelle'), commune.get('codeDepartement'))
                )
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans Commune : {e}")
        conn.rollback()
    finally:
        conn.close()
    
def load_type_contrat(conn, cur):
    """ Charge le référentiel des Types de contrats dans la table type_contrat"""
    try:
        for type in extract.getall_type_contrat():
            cur.execute(f"INSERT INTO Type_contrat (code_contrat, libelle) VALUES (%s,%s)", (type.get('code') ,type.get('libelle')))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans Type_Contrat : {e}")
        conn.rollback()
    finally:
        conn.close()

def load_code_naf(conn, cur):
    """ Charge dans la table type_contrat, le code contrat et son libelle"""
    try:
        cur.execute(f"INSERT INTO Secteur (code_naf, libelle) VALUES (%s,%s)", ('00.00X' , 'NoName'))
        for secteur in extract.getall_code_naf():
            cur.execute(f"INSERT INTO Secteur (code_naf, libelle) VALUES (%s,%s)", (secteur.get('code') ,secteur.get('libelle')))
        conn.commit()
    except Exception as e:
        print(f"Erreur lors de l'insertion des données dans Secteur : {e}")
        conn.rollback()
    finally:
        conn.close()

def load_repository_table(conn, cur):
    "Charge les données des référentiels de France Travail dans chacune des tables : Secteur, Commune, Metier, Type_contrat"
    load_code_naf(conn, cur)
    load_commune(conn, cur)
    load_metier(conn, cur)
    load_type_contrat(conn, cur)

def insert_France_travail_to_BD(conn, csv_name=f"offres{date.today()}_processed.csv"):
    cur = create_cursor(conn)
    try : 
        with open(csv_name, 'r') as file:
            sql_command = "COPY offre (code_rome,code_naf, code_contrat,code_commune, intitule, nom_entreprise, date_creation, salaire, description_) FROM STDIN WITH DELIMITER ',' CSV QUOTE '|' HEADER ;"
            cur.copy_expert(sql_command, file)
            conn.commit()  

    except Exception as e: 
        print("L'exception est la suivante : " + str(e) ) 
        print("l'exception s'est lancé lors de la commande SQL : " + sql_command )
        conn.rollback()
    finally:
        conn.close()
    
        

def main():
    
    conn = postgres_bdd_auth(database="jobmarket",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")
    """cur = create_cursor(conn)
    cur.execute(
                    "INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",
                    ('50015', 50272, 'ANNOVILLE', '50')
                )
    conn.commit()"""
    insert_France_travail_to_BD(conn)


if __name__ == "__main__":
        main()