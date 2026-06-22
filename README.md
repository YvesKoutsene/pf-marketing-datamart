# Datamart Marketing Multi-Pays — Qualité, Segmentation & Pilotage du Portefeuille Crédit Conso

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue.svg?logo=python&logoColor=white)](https://www.python.org/)
[![SQL](https://img.shields.io/badge/SQL-Advanced-orange.svg?logo=postgresql&logoColor=white)](https://en.wikipedia.org/wiki/SQL)
[![PowerBI](https://img.shields.io/badge/Power_BI-Interactive_Dashboards-yellow.svg?logo=power-bi&logoColor=black)](https://powerbi.microsoft.com/)
[![Ecosystem](https://img.shields.io/badge/BNP_Paribas-Analytics_%26_BI-emerald.svg)](https://www.personalfinance.bnpparibas/)

## Présentation du Projet

Ce projet simule l'activité réelle d'un **Business Data Analyst** au sein du **Centre d'expertise Analytics & BI** de **BNP Paribas Personal Finance**. 

L'objectif principal est de piloter l'activité de crédit à la consommation en concevant un **Datamart Marketing** complet à partir de données réelles et anonymisées d'un leader du secteur (**Home Credit Default Risk**, disponible sur Kaggle), complétées par des données macro-économiques européennes (BCE, Eurostat).

Le projet est conçu pour illustrer de bout en bout les compétences clés requises en entreprise :
*   **Gouvernance & Qualité de Donnée (Data Quality Scorecard)** : Profilage, nettoyage et détection d'anomalies réelles.
*   **Modélisation Décisionnelle (Modèle en Étoile)** : Conception d'un MCD/MLD optimisé pour l'analyse décisionnelle.
*   **Analyses Quantitatives (SQL & Python)** : Création d'une segmentation client (Risque vs Valeur) et calcul d'indicateurs de performance clés (KPIs).
*   **Restitution Business (Power BI / DAX)** : Conception de tableaux de bord interactifs d'aide à la décision.
*   **Documentation Rigoureuse** : Rédaction d'un dictionnaire de données complet et de guides méthodologiques.

---

## Architecture du Projet

Le dépôt est structuré selon les standards professionnels de l'industrie pour assurer la reproductibilité, le partage de connaissances et la maintenabilité :

```text
bnp-pf-marketing-datamart/
├── .gitignore               # Configuration des exclusions Git
├── README.md                # Présentation générale du projet (ce fichier)
├── requirements.txt         # Dépendances Python requises pour le projet
│
├── data/                    # Répertoire des données locales (exclu de Git)
│   ├── raw/                 # Fichiers sources CSV bruts de Kaggle (Home Credit)
│   │   ├── application_train.csv
│   │   ├── previous_application.csv
│   │   ├── bureau.csv
│   │   └── installments_payments.csv
│   └── processed/           # Base de données décisionnelle consolidée
│       └── datamart.db      # Fichier SQLite généré après exécution de l'ETL
│
├── notebooks/               # Notebooks Jupyter de recherche et prototypage
│   ├── 1.0_exploration_profiling.ipynb   # Étape 2 : Profilage initial des données
│   ├── 2.0_data_quality.ipynb           # Étape 3 : Data Quality & Détection d'anomalies
│   └── 3.0_customer_segmentation.ipynb  # Étape 4 : Modélisation de la segmentation
│
├── scripts/                 # Scripts Python industrialisés
│   ├── __init__.py
│   ├── data_loader.py       # Chargement optimisé des données sources
│   ├── quality_engine.py    # Exécution automatisée des tests de qualité
│   ├── segmenter.py         # Moteur de segmentation client Risque × Valeur
│   ├── generate_docx_report.py   # Générateur local du Rapport Word (exclu de Git)
│   └── generate_fiche_projection.py # Générateur local de la Note de Projection (exclu)
│
├── sql/                     # Requêtes SQL analytiques & Schémas DDL
│   ├── schema_datamart.sql  # Définition physique des tables du Data Warehouse (DDL)
│   ├── quality_checks.sql   # Détection des anomalies en base (CTE, Fenêtrage)
│   └── business_kpis.sql    # Calcul des indicateurs clés et des insights métiers
│
├── powerbi/                 # Tableau de bord décisionnel & Métadonnées
│   ├── datamart_dashboard.pbix   # Fichier Power BI Desktop
│   ├── dax_formulas.md           # Bibliothèque de formules DAX (Gouvernance & KPIs)
│   └── dashboard_design.md       # Notes de conception visuelle (exclu de Git)
│
└── docs/                    # Livrables et documents de synthèse du projet
    ├── Rapport_Projet_Datamart.docx   # Rapport Word complet rédigé pour l'entretien
    ├── Fiche Projection.docx          # Note de projection professionnelle pour le pôle
    ├── data_dictionary.md             # Dictionnaire des métadonnées du datamart
    ├── methodology.md                 # Documentation fonctionnelle des KPIs & règles
    └── pitch_presentation.md          # Support personnel de préparation (exclu de Git)
```

*Note : Les données sources de Home Credit sont conservées dans un répertoire parent `../home-credit-default-risk/` (en dehors du dépôt Git) afin de ne pas surcharger le dépôt et de respecter les consignes de sécurité.*

---

## Cartographie Métier (Fiche de Poste vs Livrables)

| Mission de la Fiche de Poste (BNP Paribas PF) | Livrable du Projet | Technologie Clé |
| :--- | :--- | :---: |
| **Gouvernance de la plateforme data & qualité** | Data Quality Scorecard complet (Complétude, Validité, Unicité) | SQL + Python |
| **Conception de KPIs & indicateurs** | Calcul de taux d'acceptation, taux d'incidents, volume de crédit, défaut | SQL (CTE, Fenêtrage) |
| **Identifier des anomalies & axes d'amélioration** | Détection d'anomalies réelles (ex: l'anomalie `DAYS_EMPLOYED` à 365243 jours) | SQL & Python |
| **Création de segmentations clients** | Segmentation bidimensionnelle : Score de Risque Externe × Capacité Financière | Python (Pandas) |
| **Documentation des données et indicateurs** | Dictionnaire de données et référentiel méthodologique centralisé | Markdown (`docs/`) |
| **Pilotage d'un environnement international** | Intégration d'une page Power BI de contexte macro-économique européen | Power BI / DAX |

---

## Guide d'Installation et Lancement

### 1. Prérequis
Assurez-vous d'avoir Python 3.9+ d'installé sur votre machine.

### 2. Cloner le dépôt et installer les dépendances
```bash
# Se placer dans le dossier du projet
cd bnp-pf-marketing-datamart

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Sur Windows : venv\Scripts\activate

# Installer les packages requis
pip install -r requirements.txt
```

### 3. Récupérer les données
Les données sources CSV de Kaggle doivent être placées dans le dossier local `data/raw/` de l'architecture :
*   `application_train.csv` (Données clients principales et prêts courants)
*   `previous_application.csv` (Historique des demandes internes passées)
*   `bureau.csv` (Historique des encours de crédits concurrents externes)
*   `installments_payments.csv` (Historique complet des remboursements d'échéances)
*   `HomeCredit_columns_description.csv` (Dictionnaire de données officiel)

Une fois les données placées dans `data/raw/`, vous pouvez lancer le script de chargement global pour initialiser et peupler la base de données relationnelle SQLite `data/processed/datamart.db` :
```bash
python scripts/data_loader.py
```

---

## Restitution Graphique & Visualisations Power BI

Le tableau de bord Power BI comprend 3 pages interactives d'aide à la décision :

### 1. Pilotage du Portefeuille & Performance (Page 1)
Ce cockpit stratégique permet d'analyser la croissance des encours et de surveiller en temps réel le taux de défaut global.
![Page 1 - Pilotage du Portefeuille & Performance](docs/Images/Page%201%20-%20Pilotage%20du%20Portefeuille%20%26%20Performance.png)

*   **Indicateurs clés associés** : KPI Cards consolidées (Volume de crédit, Clients actifs, Taux de défaut global).
*   **Courbe de tendance** : Croisement mensuel du volume de production d'octroi et du taux de défaut.

### 2. Segmentation Client & Ciblage Marketing (Page 2)
Cette vue opérationnelle permet d'isoler les segments de clients selon leur niveau de risque (comportemental) et leur valeur (encours).
![Page 2 - Segmentation Client & Stratégie Marketing](docs/Images/Page%202%20-%20Segmentation%20Client%20%26%20Strat%C3%A9gie%20Marketing.png)

*   **Heatmap Risque × Valeur** : Distribution croisée pour cibler les offres (ex: offres exclusives pour les "Champions").
*   **Treemap** : Part relative des 9 clusters décisionnels dans le portefeuille total.

### 3. Gouvernance & Qualité des Données (Page 3)
Ce volet technique sert de \"Quality Gate\" pour certifier l'intégrité de la plateforme data.
![Gouvernance et Qualité des Données](docs/Images/Gouvernance%20de%20la%20Donn%C3%A9e%20%26%20Qualit%C3%A9.png)

*   **Index de Qualité Global (IQG)** : Jauge dynamique mesurant le score de conformité (complétude et validité).
*   **Tableau de Complétude** : Taux de présence attribut par attribut avec indicateurs de couleurs conditionnels.
*   **Top des Anomalies** : Suivi des volumes de lignes en anomalie pour chaque règle de gouvernance.

---

## Contact & Présentation

Ce projet a été entièrement conçu par **Jean-Yves**, étudiant passionné et candidat au poste d'Alternant Business Data Analyst en Finance.
*   **LinkedIn** : [linkedin.com/in/jean-yves-koutsene](https://linkedin.com/in/jean-yves-koutsene)
*   **GitHub** : [https://github.com/YvesKoutsene](https://github.com/YvesKoutsene)