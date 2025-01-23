# Production d'indicateurs lié au marché du travail français
Ce projet a été réalise par :
Aurélien CLAUX - aurelien.claux.pro@gmail.com
Marvin NIMOH - 

Ce projet à pour but de créer des indicateurs liés au marché du travail en France.

Source de données : 
France travail : https://francetravail.io
ADzuna : https://developer.adzuna.com

Les scripts d'ETL sont containerisées.
Les transformations sont effectués par pandas et spark.

# Make it works

1. Récupérer vos clefs d'API Travail travail.io  et modifier le fichier config dans airflow/data/
2. Adzuna :

Le docker-compose lance :
  Une base de donnée Postgres
  un conteneur avec des scripts FastAPI qui exposent en local
  3 conteneurs dédiés au monitoring 
    Prometheus
    Postgresql-exporter
    Grafana

Une fois les cléfs récupéré
cd airflow
docker-compose up --build

Les ports exposés : 
5432 : Postgres
8000 : Api
3000 : Grafana
Le script airflow est a copier dans le repertoire ou vous executez vos DAGS







![Image](https://github.com/user-attachments/assets/ec404823-23ef-499d-8260-9bcf151341a7)
