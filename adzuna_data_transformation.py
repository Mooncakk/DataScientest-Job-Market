
from pyspark.sql import SparkSession
from pyspark.sql.types import *
from pyspark.sql.functions import *

from unidecode import unidecode


spark = SparkSession.builder.appName('adzuna_data_transformation').master('local')\
    .config('spark.jars', './postgresql-42.7.4.jar').getOrCreate()

df = spark.read.csv('Adzuna_Jobs_listing.csv', header=True)

# Renomme les colonnes
df = df.withColumnsRenamed({'category': 'secteur', 'company': 'entreprise', 'contract_type': 'type_contrat',
                            'created': 'date_creation', 'location': 'lieu', 'salary_max': 'salaire_max',
                            'salary_min': 'salaire_min', 'title': 'titre'})

df = df.dropDuplicates()


#Supprime les entrées qui ont une mauvaise cqtégorie
df = df.filter(col('secteur').startswith('Emplois') | (col('secteur') == 'Unknown'))

#Supprime le mot "Emplois " dans la colonne secteur
df = df.withColumn('secteur', regexp_replace(string='secteur', pattern='Emplois ', replacement=''))

#Supprime les lignes avec un type de contrat erroné
df = df.filter((df.type_contrat == 'contract') |
          (df.type_contrat == 'permanent') |
          (isnull(df.type_contrat)))

#Remplace certaines valeurs dans la colonne type_contrat
df = df.withColumn('type_contrat', regexp_replace(string='type_contrat', pattern='permanent', replacement='CDI'))\
              .withColumn('type_contrat', regexp_replace(string='type_contrat', pattern='contract', replacement='CDD'))

#Remplace les valeurs manquantes de la colonne type_contrat
df = df.na.fill({'type_contrat': 'non communiqué'})

#Remplace le terme "Unknown" par "Autres" dans la colonne secteur
df = df.withColumn('secteur', regexp_replace(string='secteur', pattern='Unknown', replacement='Autres'))

df = df.withColumn('date_creation', regexp_replace(string='date_creation', pattern='T', replacement=' '))\
              .withColumn('date_creation', regexp_replace(string='date_creation', pattern='Z', replacement=''))

#Change le type de certaines colonnes
df = df.withColumn('date_creation', col('date_creation').cast(DateType()))\
        .withColumn('salaire_min', col('salaire_min').cast(FloatType()))\
        .withColumn('salaire_max', col('salaire_max').cast(FloatType()))

#Converti la colonne lieu en liste
df = df.withColumn('lieu', split(col('lieu'), ',').cast(ArrayType(StringType())))

df = df.withColumn('commune', col('lieu').getItem(0))

df = df.withColumn('commune', lower(col('commune')))\
        .withColumn('commune', regexp_replace('commune', "saint", 'st'))\
        .withColumn('commune', regexp_replace('commune', '-', ' '))\
        .withColumn('commune', regexp_replace('commune', "'", ' '))

unidecode_udf = udf(lambda x: unidecode(x), StringType())

df = df.withColumn('commune', unidecode_udf(df.commune))

df2 = spark.read.csv('france_commune.csv', header=True, sep=';')

df2 = df2.select('Nom_de_la_commune', 'Code_postal')

df2 = df2.withColumnsRenamed({'Nom_de_la_commune': 'commune', 'Code_postal': 'code_postal'})

df2 = df2.withColumn('commune', lower(col('commune')))

df2 = df2.dropDuplicates()

cities = spark.createDataFrame([('paris', '75000'),
                                ('lyon', '69000'),
                                ('marseille', '13000')],
                               ['commune', 'code_postal'])

df2 = df2.union(cities)

df = df.join(df2, 'commune', how='inner').withColumn('code_postal', df2.code_postal.cast(IntegerType()))

df = df.drop('commune')\
    .drop('lieu')

#Classe les colonnes
df = df.select('titre', 'description', 'secteur', 'entreprise', 'code_postal','type_contrat',
               'salaire_min', 'salaire_max', 'date_creation')


df.write.format('jdbc')\
    .mode('overwrite')\
    .option('url', 'jdbc:postgresql://postgres_db:5432/france_emplois')\
    .option('dbtable', 'Adzuna')\
    .option('driver', 'org.postgresql.Driver')\
    .option('user', 'admin').option('password', 'datascientest')\
    .save()

