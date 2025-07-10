# Analyse du marché du travail français

Ce projet a été réalise par :
- Aurélien CLAUX - aurelien.claux.pro@gmail.com
- Marvin NIMOH

## 🎯 Objectif du projet

Ce projet a pour ambition de créer des indicateurs clés liés au marché du travail en France, en exploitant des données d'offres d'emploi issues de deux sources majeures : France Travail et Adzuna.

### Objectifs principaux

- Fournir une analyse détaillée et des insights pertinents sur les tendances du marché de l'emploi en France
- Identifier les compétences les plus recherchées
- Analyser l'évolution des salaires
- Cartographier la répartition géographique des offres d'emploi

## 📊 Sources de données

### France Travail
Les données sont récupérées via [francetravail.io](https://francetravail.io), une plateforme offrant un accès complet aux offres d'emploi en France.

### Adzuna
Les données sont également collectées depuis [developer.adzuna.com](https://developer.adzuna.com), un moteur de recherche d'emplois qui agrège des offres de diverses sources.

## 🛠️ Technologies utilisées

### Traitement des données
- **Pandas** & **PySpark** : Les transformations et le traitement des données sont effectués en utilisant des technologies robustes et performantes. Cela nous permet de manipuler et d'analyser de grands volumes de données de manière efficace.

### Base de données
- **PostgreSQL** : Pour le stockage des données, nous utilisons PostgreSQL, une base de données relationnelle avancée qui garantit l'intégrité et la sécurité des données.

### Orchestration
- **Airflow** : Le pipeline ETL (Extract, Transform, Load) est orchestré par Airflow. Cela nous permet de planifier, surveiller et gérer nos workflows de données de manière centralisée et automatisée.

### API
- **FastAPI** : Les insights générés à partir de ces données sont accessibles via une API développée avec FastAPI. Cette API offre une interface flexible et performante pour accéder aux informations et les intégrer dans diverses applications.

### Monitoring
- **Prometheus** & **Grafana** : Nous permet de surveiller en temps réel les performances et la santé de notre infrastructure, assurant ainsi une disponibilité et une fiabilité optimales.

## ⚡ Fonctionnalités clés

### Collecte et traitement des données
Automatisation de la collecte et du nettoyage des données pour garantir leur qualité et leur cohérence.

### Accès aux données
Une API robuste pour permettre un accès facile et sécurisé aux données et aux insights générés.

### Monitoring et maintenance
Surveillance continue des performances et de la santé du système pour assurer une disponibilité et une fiabilité optimales.

## 🚀 Make it works

1. Récupérer vos clefs d'API Travail travail.io  et modifier le fichier config dans airflow/data/
2. Adzuna :

Le docker-compose lance :

Une base de donnée Postgres  
  
un conteneur avec des scripts FastAPI qui exposent en local
  
3 conteneurs dédiés au monitoring :
  
Prometheus
    
Postgresql-exporter
    
Grafana

Une fois les cléfs récupérés :

    cd airflow
    docker-compose up --build

Les ports exposés : 
5432 : Postgres
8000 : Api
3000 : Grafana

Le script airflow est a copier dans le repertoire ou vous executez vos DAGS

## 📈 Roadmap

![Image](https://github.com/user-attachments/assets/ec404823-23ef-499d-8260-9bcf151341a7)
