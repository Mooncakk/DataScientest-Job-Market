import requests
import pprint
import csv
from datetime import date, datetime
import time
import load
import psycopg2

# TO DO : mettre dans une variable global l'access token pour ne pas faire un appel a access token a chaque besoin d'afficher des offres. Un token est valable ^l

# Récupération des données de France-Travail via API
# Clé renvoyée par l'api par Offre
# dict_keys(['id', 'intitule', 'description', 'dateCreation', 'dateActualisation', 'lieuTravail',
# 'romeCode', 'romeLibelle', 'appellationlibelle', 'entreprise', 'typeContrat', 'typeContratLibelle', 
# 'natureContrat', 'experienceExige', 'experienceLibelle', 'competences', 'salaire', 'dureeTravailLibelle', 
# 'dureeTravailLibelleConverti', 'alternance', 'contact', 'agence', 'nombrePostes', 'accessibleTH', 
# 'qualificationCode', 'qualificationLibelle', 'codeNAF', 'secteurActivite', 'secteurActiviteLibelle', 
# 'qualitesProfessionnelles', 'origineOffre', 'offresManqueCandidats'])
#

class APIError(Exception):
    """Exception levée pour les erreurs liées à l'API avec status code inconnu."""
    pass

class NoContentError(APIError):
    """Pas de contenu avec les paramètres indiqués (204)."""
    pass

class BadRequestError(APIError):
    """Requête incorrecte(400)."""
    pass

class ServerError(APIError):
    """Internal server error : impossible de joindre France Travail (500)."""
    pass

def post_request(lien, params):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(lien, params=params, headers=headers).json()

def get_request(lien, headers, params={}):
        response = requests.get(lien,params=params ,headers=headers)
        if response.status_code == 204:
                raise NoContentError("Aucun contenu disponible pour les paramètres fournis." + str(params))
        elif response.status_code == 400:
                raise BadRequestError("La requête est invalide. Vérifiez vos paramètres." + str(params))
                
        elif response.status_code == 500:
                raise ServerError("Erreur serveur. Veuillez réessayer plus tard.")
        
        return response.json()

def get_access_token():
        url = 'https://entreprise.francetravail.fr/connexion/oauth2/access_token'
        params={
                            'realm'                         : '/partenaire',
                            'grant_type'                    : 'client_credentials',
                            'client_id'                     : 'PAR_dashboardemploi_f99386bde90949946d6513fd76b3d48567c931283b93d35217068957c73245d4',
                            'client_secret'                 : '88c04482d5a4149bdf3be704350c7e82c8840f4167b665996cea737fe6000a8d',
                            'scope'                         : 'o2dsoffre api_offresdemploiv2',
                    }
        
        response = post_request(url, params=params)
        return response['access_token']


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


############################################"
# Fonctions permettant de boucler sur l'API
#########################################"

def yield_offre_france_travail(params=''):
        """
        !! Ne fait pas la pagination !!
    Retourne les offres d'emploi disponibles sur la plateforme France Travail
    en fonction des paramètres spécifiés (par exemple, le Code ROME).

    La liste des paramètres disponibles pour l'API est accessible ici : 
    https://francetravail.io/produits-partages/catalogue/offres-emploi/documentation#/api-reference/operations/recupererListeOffre

    Si aucun paramètre n'est fourni, la fonction renvoie uniquement les dernières offres publiées.

    Args:
        params (dict): Un dictionnaire contenant les paramètres de recherche acceptés par l'API, tels que 
            le code ROME ou l'indicateur d'adaptation pour les entreprises. Par défaut, une chaîne vide.

    Returns:
        generator: Un générateur qui produit une liste de dictionnaires, où chaque dictionnaire représente 
            une offre d'emploi avec ses détails spécifiques.

    Examples:
        Utilisation de la fonction avec des paramètres spécifiques :

        >>> for offre in yield_offres_france_travail(params={'codeROME': 'M1403', 'entreprisesAdaptees': 'false'}):
        >>>     pprint.pp(offre)
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        try : 
                
                data = get_request(url, params=params, headers=headers)
                #print(len(data))
                for offre in data['resultats']:
                    yield offre
        
        except NoContentError as n :
            print(e)
        except BadRequestError as b :
            print(b)
        except Exception as e:
            print(e)
            print(url + params)
            print(data)

        if len(data['resultats']) is None:
                print("Pas de données récupérées")

def france_travail_yield(params):
    """ Permet de yield sur des offres France travail en foncton des paramètres"""
    step = 150
    start = 0
    # Tant qu'il est possible d'insérer en base
    
    while True:  
        try:
            if start == 3149:
                break
            for offre in yield_offre_france_travail({'range': f'{start}-{start + step - 1}'} | (params)): 
                yield offre 
                            
        except Exception as e:
                """print('Erreur dans France travail Yield ' )
                print(e)"""
                # permet de ne pas incrémententer start si la requête ne renvoie rien
                break
        start += step
        

############################################
# Insertion dans un CSV
########################'#################

# Insère les offres dans un CSV et utilise les référentiels en base de données.
def france_travail_to_CSV(conn, csv_name=f'offres{date.today()}.csv'):    
    # Récupère tous les codes ROMES et type contrat, On peut avoir max que 3150 résultats max par requete, pagination inclus
    cur1 = create_cursor(conn)
    cur1.execute("SELECT * from Type_contrat")
    types_contrat = cur1.fetchall()
    cur2 = create_cursor(conn)
   

    buffer = []
        
    # Requete sur l'API France Travail en modifiant le paramètre Code ROME et insère dans le CSV
    with open(csv_name, 'a', newline='', encoding='utf-8') as csvfile:
        csv_offres = csv.writer(csvfile, delimiter=',', quotechar='|', )
        try: 
            for type_contrat in  types_contrat:
                print(type_contrat[0] + str(datetime.now()))
                cur2.execute("SELECT * from Metier ")
                codes_rome = cur2.fetchall()
                for code_rome in codes_rome:
                    time.sleep(0.05)
                    for offre in france_travail_yield(params={'codeROME': code_rome[0], 'typeContrat' : type_contrat[0]}):
                        buffer.append([
                        offre.get('romeCode', None), 
                        offre.get('codeNAF', None), 
                        offre.get('typeContrat', None), 
                        offre.get('lieuTravail', {}).get('commune', None) ,
                        offre.get('intitule', None),
                        offre.get('entreprise', {}).get('nom', None),
                        offre.get('dateCreation', None), 
                        str(offre.get('salaire',{}).get('libelle', None)) + ' ' + str(offre.get('salaire',{}).get('commentaire', None)) + ' ' + str(offre.get('salaire',{}).get('complement1', None)) + ' ' + str(offre.get('salaire',{}).get('complement2', None))  ,                                                
                        (offre.get('description', None) or '').replace('\n',' ')
                        
                    ])
                    # ecriture par lot 
                    if len(buffer) >= 25:  
                        csv_offres.writerows(buffer)
                        buffer = []
        except Exception as e:                 
            print(f"Erreur lors du lancement de France_Travail_to_CSV dans extract.py : {e} ")   

# Même chose mais utilise des CSVs
def france_travail_to_CSV2(csv_name=f'offres{date.today()}.csv'):
    """ Génère un fichier CSV contenant les offres à partir des fichiers CSV existants."""

    # Charger les types de contrats depuis le CSV
    types_contrat = []
    with open('referentiels/type_contrat.csv', mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            types_contrat.append(row['code_contrat'])

    # Charger les métiers (codes ROME) depuis le CSV
    codes_rome = []
    with open('referentiels/metier.csv', mode='r', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        for row in reader:
            codes_rome.append(row['code_rome'])

    buffer = []

    # Écriture des offres dans le fichier CSV
    with open(csv_name, 'a', newline='', encoding='utf-8') as csvfile:
        
        csv_offres = csv.writer(csvfile, delimiter=',', quotechar='|', quoting=csv.QUOTE_MINIMAL)

        try:
            for type_contrat in types_contrat:
                print(f"Traitement type contrat: {type_contrat} - {datetime.now()}")
                for code_rome in codes_rome:
                    time.sleep(0.05)
                    for offre in france_travail_yield(params={'codeROME': code_rome, 'typeContrat': type_contrat}):
                        buffer.append([
                            offre.get('romeCode', None),
                            offre.get('codeNAF', None),
                            offre.get('typeContrat', None),
                            offre.get('lieuTravail', {}).get('commune', None),
                            offre.get('intitule', None),
                            offre.get('entreprise', {}).get('nom', None),
                            offre.get('dateCreation', None),
                            f"{offre.get('salaire', {}).get('libelle', '')} {offre.get('salaire', {}).get('commentaire', '')} {offre.get('salaire', {}).get('complement1', '')} {offre.get('salaire', {}).get('complement2', '')}",
                            (offre.get('description', None) or '').replace('\n', ' ')
                        ])

                        # Écriture par lot
                        if len(buffer) >= 25:
                            csv_offres.writerows(buffer)
                            buffer = []

            # Écrire les éléments restants dans le buffer
            if buffer:
                csv_offres.writerows(buffer)

        except Exception as e:
            print(f"Erreur lors de l'exécution de france_travail_to_CSV : {e}")




######################################
# Fonctions liées aux référentiels - Mode Insertion en base de données 
####################################

def create_cursor(conn):
    try:
        return conn.cursor()
    except Exception as e:
        print(f"Erreur: {e}")
    

def load_metier(conn, cur):
    """ Charge le réferentiel des métiers (code ROME) dans la table Metier"""
    try:
        for metier in getall_code_rome():
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
        cur.execute("INSERT INTO Commune (code_commune, code_postal, libelle, code_departement) VALUES (%s, %s, %s, %s)",('50602', 50110, 'Tourlaville', '50'))
        for commune in getall_communes():
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
        for type in getall_type_contrat():
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
        for secteur in getall_code_naf():
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


######################################
# Fonctions liées aux référentiels - Mode CSV
####################################

# Fonction générique pour écrire dans un fichier CSV
def write_to_csv(file_name, fieldnames, rows):
    try:
        with open(file_name, mode='w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)
        print(f"Données écrites avec succès dans {file_name}")
    except Exception as e:
        print(f"Erreur lors de l'écriture dans {file_name} : {e}")

# Charger les métiers dans un fichier CSV
def load_metier_to_csv():
    """ Charge le référentiel des métiers (code ROME) dans un fichier CSV """
    file_name = 'metier.csv'
    fieldnames = ['code_rome', 'libelle']
    rows = [{'code_rome': metier.get('code'), 'libelle': metier.get('libelle')} for metier in getall_code_rome()]
    write_to_csv(file_name, fieldnames, rows)

# Charger les communes dans un fichier CSV
def load_commune_to_csv():
    """ Charge le référentiel Communes dans un fichier CSV """
    file_name = 'commune.csv'
    fieldnames = ['code_commune', 'code_postal', 'libelle', 'code_departement']
    rows = [
        {'code_commune': '00000', 'code_postal': 00000, 'libelle': 'Noname', 'code_departement': '000'},
        {'code_commune': '75056', 'code_postal': 75000, 'libelle': 'Paris', 'code_departement': '75'},
        {'code_commune': '69152', 'code_postal': 69310, 'libelle': 'Paris', 'code_departement': '75'},
        {'code_commune': '13055', 'code_postal': 13000, 'libelle': 'Marseille', 'code_departement': '13'},
        {'code_commune': '69123', 'code_postal': 69000, 'libelle': 'Lyon', 'code_departement': '69'},
        {'code_commune': '50602', 'code_postal': 50110, 'libelle': 'Tourlaville', 'code_departement': '50'}
    ]
    # Ajouter les données depuis getall_communes
    for commune in getall_communes():
        rows.append({
            'code_commune': commune.get('code'),
            'code_postal': commune.get('codePostal'),
            'libelle': commune.get('libelle'),
            'code_departement': commune.get('codeDepartement')
        })
    write_to_csv(file_name, fieldnames, rows)

# Charger les types de contrats dans un fichier CSV
def load_type_contrat_to_csv():
    """ Charge le référentiel des Types de contrats dans un fichier CSV """
    file_name = 'type_contrat.csv'
    fieldnames = ['code_contrat', 'libelle']
    rows = [{'code_contrat': type.get('code'), 'libelle': type.get('libelle')} for type in getall_type_contrat()]
    write_to_csv(file_name, fieldnames, rows)

# Charger les codes NAF dans un fichier CSV
def load_code_naf_to_csv():
    """ Charge le référentiel des codes NAF dans un fichier CSV """
    file_name = 'secteur.csv'
    fieldnames = ['code_naf', 'libelle']
    rows = [{'code_naf': '00.00X', 'libelle': 'NoName'}]
    rows.extend([
        {'code_naf': secteur.get('code'), 'libelle': secteur.get('libelle')} for secteur in getall_code_naf()
    ])
    write_to_csv(file_name, fieldnames, rows)



#############################
# Générateur récupérant les les référentiels depuis leurs API respectives
#############################

def getall_code_rome():
        """Récupère tous les codes Romes du réferentiel de France TRavail.
        Un code NAF représente un métier
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/metiers'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        metiers = get_request(url, headers=headers)
        for metier in metiers:
               yield metier
        
def getall_code_naf():
        """ Récupère tous les codes NAF du réferentiel de France Travail.
        Un code NAF représente  un secteur d'activité
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/nafs'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        nafs = get_request(url, headers=headers)
        for naf in nafs:
               yield naf

def getall_communes():
        """ Récupère toutes les communes avec le code du departement et le code postal
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/communes'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        communes = get_request(url, headers=headers)
        for commune in communes:
               yield commune

def getall_type_contrat():
        """ Récupère tous les types de contrats
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/typesContrats'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        contrats = get_request(url, headers=headers)
        for contrat in contrats:
               yield contrat

def main():
        """for offre in yield_offres_france_travail():
                pprint.pp(offre)
                france_travail_toCsv(params={'codeROME': 'M1403'})"""
        #france_travail_to_CSV(conn)
        france_travail_to_CSV2()


        #load_metier_to_csv()
        #load_commune_to_csv()
        #load_type_contrat_to_csv()
        #load_code_naf_to_csv()
        

        

        #conn = load.postgres_bdd_auth(database="jobmarket", host="localhost", user="postgres", password="postgres", port="5432")
        #cur = create_cursor(conn)
        #load_repository_table(conn, cur)



        
        
          
if __name__ == "__main__":
        main()
