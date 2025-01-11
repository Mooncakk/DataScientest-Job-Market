import psycopg2

import pprint
from datetime import date

#TODO : Transformer le main en fonction
#exemple de requete : curl -X GET http://127.0.0.1:8000/france_travail/most_recruiting_city/H1206


def create_cursor(conn):
    try:
        return conn.cursor()
    except Exception as e:
        print(f"Erreur: {e}")
    


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


def insert_France_travail_to_BD_in_container(csv_name=f"data/offres{date.today()}_processed.csv"):
    """
    Fonction utilisé pour insérer dans la BD l'extraction des offres d'emploi de France Travail_ connexion modifié pour foncitonner dans les container du projet Job Market"""
    conn = postgres_bdd_auth(database="france_emplois",
                            host="aurelclx_villani", # renseigner le nom du container ou l'adresse IP en fonction de si le code est lancé en local ou en container
                            user="admin",
                            password="datascientest",
                            port="5432")
    cur = create_cursor(conn)
    cur.execute("Delete from offre")
    conn.commit()

    # La table temporaire va permettre d'insérer en base de données bien qu'une commune ne soit pas présente dans la table Commune (Contrainte de clé étrangère)
    # On COPY le CSV dans la table temporaire, On insère dans la table Offre les enregistrements de la table temporaire dont le code Commune existe dans la table Commune.
    # Ensuite on affiche dans le terminal les codes communes n'existant pas dans la table pour les insérer dans la base de données en ajoutant le nouvel enregistrement a la main dans requete.sql et bien sur on oublie pas de re build l'image de la database pour que Commune se crée avec la nouvelle Commune
    cur.execute("""
    CREATE TEMP TABLE temp_offre (
        code_rome VARCHAR(5),
        code_naf VARCHAR(6),
        code_contrat VARCHAR(3),
        code_commune VARCHAR(5),
        intitule VARCHAR(500),
        nom_entreprise VARCHAR(1000),
        date_creation DATE,
        salaire VARCHAR(1000),
        description_ VARCHAR(10000)
    )
    """)
    conn.commit()

    try : 
        with open(csv_name, 'r') as file:
            sql_command = "COPY temp_offre (code_rome,code_naf, code_contrat,code_commune, intitule, nom_entreprise, date_creation, salaire, description_) FROM STDIN WITH DELIMITER ',' CSV QUOTE '|' HEADER;"
            cur.copy_expert(sql_command, file)
            conn.commit()  

        # on insère uniquement les lignes avec des communes existant dans notre referentiel
        cur.execute("""
        INSERT INTO offre (code_rome, code_naf, code_contrat, code_commune, intitule, nom_entreprise, date_creation, salaire, description_)
        SELECT code_rome, code_naf, code_contrat, code_commune, intitule, nom_entreprise, date_creation, salaire, description_
        FROM temp_offre
        WHERE code_commune IN (SELECT code_commune FROM Commune);
        """)
        conn.commit()

        # On identifie les codes Communes n'existant pas dans Commune
        cur.execute("""
        SELECT DISTINCT code_commune
        FROM temp_offre
        WHERE code_commune NOT IN (SELECT code_commune FROM Commune);
        """)
        communes_not_in_commune_table = cur.fetchall()

        # On les affiche ici pour les ajouter à la main dans requete SQL, on peut trouver les informations des Communes 
        if communes_not_in_commune_table:
            print("Les code_commune problématiques sont :")
            for code in communes_not_in_commune_table:
                print(code[0])

    except Exception as e: 
        print("L'exception est la suivante : " + str(e) ) 
        print("l'exception s'est lancé lors de la commande SQL : " + sql_command )
        conn.rollback()
    finally:
        cur.execute("DROP TABLE temp_offre")
        conn.commit()
        conn.close()
    
def get_most_recruiting_sector(conn):
    cur = create_cursor(conn)
    cur.execute("SELECT s.code_naf, s.libelle AS secteur, COUNT(o.id_offre) AS nombre_offres \
                FROM Offre o JOIN Secteur s ON o.code_naf = s.code_naf \
                GROUP BY \
                    s.code_naf, s.libelle \
                ORDER BY  \
                    nombre_offres DESC\
                LIMIT 5;")
    return cur.fetchall()

def get_most_recruiting_job(conn):
    cur = create_cursor(conn)
    cur.execute("SELECT m.code_rome, m.libelle AS metier, COUNT(o.id_offre) AS nombre_offres \
    FROM Offre o \
    JOIN Metier m ON o.code_rome = m.code_rome \
    GROUP BY m.code_rome, m.libelle \
    ORDER BY nombre_offres DESC \
    LIMIT 10;")
    return cur.fetchall()

def get_most_recruiting_city(conn):
    cur = create_cursor(conn)
    cur.execute("SELECT c.code_commune, c.libelle AS ville, COUNT(o.id_offre) AS nombre_offres \
    FROM Offre o \
    JOIN Commune c ON o.code_commune = c.code_commune \
    GROUP BY c.code_commune, c.libelle \
    ORDER BY nombre_offres DESC LIMIT 10")
    return cur.fetchall()

def get_data_engineer_most_recruiting_city(conn):
    cur = create_cursor(conn)
    cur.execute("SELECT c.code_commune, c.libelle AS ville, COUNT(o.id_offre) AS nombre_offres \
    FROM Offre o \
    JOIN Commune c ON o.code_commune = c.code_commune \
    WHERE o.intitule ILIKE '%data engineer%' OR  \
    o.intitule ILIKE '%ingénieur data%' OR  \
    o.description_ ILIKE '%data engineer%' OR  \
    o.description_ ILIKE '%ingénieur data%' OR  \
    o.description_ ILIKE '%data engineering%' OR \
    o.code_rome = 'M1811' \
    GROUP BY c.code_commune, c.libelle \
    ORDER BY nombre_offres DESC \
    LIMIT 10;")
    return cur.fetchall()

def get_most_recruiting_city_with_code_rome(conn, codeRome):
    """
    Retourne les villes qui recrutent le plus pour un code Rome donné
    """
    cur = create_cursor(conn)
    print(cur)
    cur.execute(f"SELECT c.code_commune, c.libelle AS ville, COUNT(o.id_offre) AS nombre_offres \
    FROM Offre o \
    JOIN Commune c ON o.code_commune = c.code_commune \
    WHERE o.code_rome = '{codeRome}' \
    GROUP BY c.code_commune, c.libelle \
    ORDER BY nombre_offres DESC \
    LIMIT 10;")
    return cur.fetchall()

def main():
    """conn = postgres_bdd_auth(database="jobmarket",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")"""
    insert_France_travail_to_BD_in_container()

if __name__ == "__main__":
        main()