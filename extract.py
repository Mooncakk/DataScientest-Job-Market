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

def post_request(lien, params):
        headers = {'Content-Type': 'application/x-www-form-urlencoded'}
        return requests.post(lien, params=params, headers=headers).json()

def get_request(lien, headers):
        return requests.get(lien, headers=headers).json()

def get_access_token():
        response = post_request('https://entreprise.francetravail.fr/connexion/oauth2/access_token', 
                    params={
                            'realm'                         : '/partenaire',
                            'grant_type'                    : 'client_credentials',
                            'client_id'                     : 'PAR_dashboardemploi_f80b1ec5d219063f6fde2c02b399657f48fc4fcb15671542e42fbf914ced66fa',
                            'client_secret'                 : 'aa36cce260bbace220de16acdaa7e93e3c719dbd6871e603e309d8bf1dc074df',
                            'scope'                         : 'o2dsoffre api_offresdemploiv2',
                    })
        return response['access_token']


"""
    La fonction permet de se faire retourner les offres d'emploi présentes sur la plateforme France Travail
        en fonction des paramètres. (Ex : Code Rome). 


        On peut trouver la liste des paramètres sur ce lien : https://francetravail.io/produits-partages/catalogue/offres-emploi/documentation#/api-reference/operations/recupererListeOffre

    Si pas de paramètre alors la fonction renvoie uniquement les dernières offres publiées.

    Args:
        params (dict): Un dictionnaire ou les clés sont les différents paramètres que puissent prendre l'API. Chaine de caractère vide par défaut
    
    Returns:
        data['resultats'] (a list of dict): chaque dictionnaire représente une offre d'emploi

    Examples:
        Example usage of the function, ideally with a Python REPL format.

        >>> for offres in yield_offres_france_travail(params={'codeROME':'M1403', 'entreprisesAdaptees' : 'false'}):
        >>>        pprint.pp(offres)
    """
def yield_offres_france_travail(params=''):

        if len(params) > 0:
                
                query_params = '?'
                i = 0

                for i in range(len(params)):
                        query_params += list(params.keys())[i] + '=' + list(params.values())[i] + '&'                        
                params = query_params

        data = get_request('https://api.francetravail.io/partenaire/offresdemploi/v2/offres/search' + params,
                                        headers={
                                                'Authorization' : 'Bearer ' + get_access_token(),
                                                'Accept'         : 'application/json'
                                                }
                        )

        yield data['resultats']




def main():
        for offres in yield_offres_france_travail(params={'codeROME':'M1403'}):
                pprint.pp(offres)


if __name__ == "__main__":
        main()
