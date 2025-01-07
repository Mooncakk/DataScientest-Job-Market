import extract as extract
import load
import csv
from datetime import date
import pandas as pd

def update_csv(csv_name=f'offres{date.today()}.csv'):
    df = pd.read_csv(csv_name, quotechar='|', sep=',')
    df.columns = ['romeCode', 'codeNaf','typeContrat','lieuTravail', 'intitule', 'entreprise', 'dateCreation', 'salaire', 'description']
    df = df.drop_duplicates()
    df['salaire'] = df.salaire.fillna('39800')
    df['entreprise'] = df.entreprise.fillna('NoName')
    df['lieuTravail'] = df.lieuTravail.fillna('00000') 
    df['codeNaf'] = df.codeNaf.fillna('00.00X')
    df.to_csv(f'offres{date.today()}_processed.csv', sep=',', quotechar='|', index=False)

def main():
    update_csv()
    
   


if __name__ == "__main__":
    main()