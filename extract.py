import requests
import pprint

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
                            'client_id'                     : 'PAR_dashboardemploi_f80b1ec5d219063f6fde2c02b399657f48fc4fcb15671542e42fbf914ced66fa',
                            'client_secret'                 : 'aa36cce260bbace220de16acdaa7e93e3c719dbd6871e603e309d8bf1dc074df',
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
                print(e)
        except BadRequestError as e:
                print(e)
        except ServerError as e:
                print(e)

        yield data['resultats']




def main():
        for offres in yield_offres_france_travail(params={'codeROME':'M1403'}):
                pprint.pp(offres)


if __name__ == "__main__":
        main()
