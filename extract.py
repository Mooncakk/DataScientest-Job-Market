import requests
import pprint
import csv
from datetime import date, datetime
import time
import load

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
            print(n)
        except BadRequestError as b :
            print(b)
        except Exception as e:
                print(e)
                print(url + params)
                print(data)
                raise Exception(e)

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
        

############################################"
# Fonctions d'insérer dans un CSV
########################'#################"

def france_travail_to_CSV(conn, csv_name=f'offres{date.today()}.csv'):    
    # Récupère tous les codes ROMES et type contrat, On peut avoir max que 3150 résultats max par requete, pagination inclus
    cur1 = load.create_cursor(conn)
    cur1.execute("SELECT * from Type_contrat")
    types_contrat = cur1.fetchall()

    cur2 = load.create_cursor(conn)
    cur2.execute("SELECT * from Metier ")
    codes_rome = cur2.fetchall()

    buffer = []
        
    # Requete sur l'API France Travail en modifiant le paramètre Code ROME et insère dans le CSV
    with open(csv_name, 'a', newline='') as csvfile:
        csv_offres = csv.writer(csvfile, delimiter=',', quotechar='|', )
        try: 
            for type_contrat in  types_contrat:
                print(type_contrat[0] + str(datetime.now()))
                for code_rome in codes_rome:
                    #time.sleep(0.05)
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

######################################
# Fonctions liées aux référentiels
####################################
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
        
        
        conn = load.postgres_bdd_auth(database="jobmarket",
                            host="localhost",
                            user="postgres",
                            password="postgres",
                            port="5432")
        
        france_travail_to_CSV(conn)
          
if __name__ == "__main__":
        main()
