import extract
import load
import csv
from datetime import date
import pandas as pd

def update_csv(csv_name=f'offres{date.today()}.csv'):
    df = pd.read_csv(csv_name, quotechar='|', sep=',')
    df.columns = ['romeCode', 'codeNaf','typeContrat','lieuTravail', 'intitule', 'entreprise', 'dateCreation', 'salaire', 'description']
    print(df.head(10))
    print(len(df))
    df = df.drop_duplicates()
    print("######## drop_duplicates")
    print(len(df))
    df['salaire'] = df.salaire.fillna('39800')
    print("########salaire")
    print(len(df))
    
    df['entreprise'] = df.entreprise.fillna('NoName')
    print("########entreprise")
    print(len(df))
    df['lieuTravail'] = df.lieuTravail.fillna('00000')
    print("########lieuTravail")
    print(len(df))
    df['codeNaf'] = df.codeNaf.fillna('00.00X')
    print("########codeNaf")
    print(len(df))
    print(df.head(10))
    df.to_csv(f'offres{date.today()}_processed.csv', sep=',', quotechar='|', index=False)

def main():
    update_csv()
    
   


if __name__ == "__main__":
    main()