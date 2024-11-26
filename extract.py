import requests
import pprint
import csv
from datetime import date

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

def get_request(lien, headers):
        response = requests.get(lien, headers=headers)
        if response.status_code == 204:
                raise NoContentError("Aucun contenu disponible pour les paramètres fournis.")
        elif response.status_code == 400:
                raise BadRequestError("La requête est invalide. Vérifiez vos paramètres.")
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

def yield_offres_france_travail(params=''):
        """
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
        
        if len(params) > 0:
                query_params, i  = '?', 0
                keys, values = params.keys(), params.values()

                for i in range(len(params)):
                        query_params += list(keys)[i] + '=' + list(values)[i] + '&'                        
                params = query_params

        try : 
                data = get_request(url + params, headers=headers)
        except NoContentError as e:
                raise NoContentError
        except BadRequestError as e:
                print(e)
        except ServerError as e:
                print(e)

        for offre in data['resultats']:
               yield offre


def france_travail_toCsv(offres, csv_name):
       """ Prends une liste d'offres en paramètre et ajoute l'intitulé, le nom de l'entreprise le lieu de travail et le codeNAF dans un CSV"""
       
       # a pour append ici
       with open(csv_name, 'a', newline='') as csvfile:
              csv_offres = csv.writer(csvfile, delimiter=',', quotechar='|', )
              for offre in offres:
                     csv_offres.writerow([
                            offre.get('intitule', None),                            
                            offre.get('codeROME', None),
                            offre.get('codeNAF', None), 
                            offre.get('typeContrat', None),
                            offre.get('lieuTravail', {}).get('codePostal', None), 
                            offre.get('entreprise', {}).get('nom', None),
                            offre.get('dateCreation', None)
                            ,
                            ''.join(offre.get('description', None).replace('\n',' ')), 
                            offre.get('salaire', None), 
                            ])

def getall_code_rome():
        """Récupère tous les codes Romes du réferentiel de France TRavail.
        Un code NAF représente un métier
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/metiers'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        metiers = get_request(url, headers)
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
        nafs = get_request(url, headers)
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
        communes = get_request(url, headers)
        for commune in communes:
               yield communes


def getall_type_contrat():
        """ Récupère tous les types de contrats
        """
        url = 'https://api.francetravail.io/partenaire/offresdemploi/v2/referentiel/typesContrats'
        headers = {
                'Authorization' : 'Bearer ' + get_access_token(),
                'Accept'         : 'application/json'
                }
        contrats = get_request(url, headers)
        for contrat in contrats:
               yield contrat


def main():
        """for offre in yield_offres_france_travail():
               pprint.pp(offre)"""
        step = 150
        start = 0
        while True:   
                try:           
                        france_travail_toCsv(yield_offres_france_travail(params={
                                        'range': f'{start}-{start + step - 1}'
                                        }), csv_name= f'offres{date.today()}.csv')   
                except Exception as e:
                       print(e)
                       break

                start += step
    
if __name__ == "__main__":
        main()
