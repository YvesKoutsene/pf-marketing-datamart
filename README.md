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
├── README.md                # Guide de cadrage et présentation générale (ce fichier)
├── requirements.txt         # Dépendances Python requises pour le projet
│
├── notebooks/               # Notebooks Jupyter de recherche, d'exploration et de prototypage
│   ├── 1.0_exploration_profiling.ipynb   # Étape 2 : Profilage initial des données
│   ├── 2.0_data_quality.ipynb           # Étape 3 : Data Quality & Détection d'anomalies
│   └── 3.0_customer_segmentation.ipynb  # Étape 4 : Modélisation de la segmentation
│
├── scripts/                 # Scripts Python industrialisés et réutilisables
│   ├── __init__.py
│   ├── data_loader.py       # Chargement optimisé des volumétries
│   ├── quality_engine.py    # Calculs du Scorecard Qualité
│   └── segmenter.py         # Moteur de segmentation algorithmique
│
├── sql/                     # Scripts SQL avancés (requêtes analytiques & DDL)
│   ├── schema_datamart.sql  # Étape 1 : MCD / Définition des tables (DDL)
│   ├── quality_checks.sql   # Étape 3 : Détection d'anomalies (CTE, Window functions)
│   └── business_kpis.sql    # Étape 5 : Calcul des indicateurs de performance
│
├── powerbi/                 # Modèle de données et documentation Power BI
│   ├── datamart_dashboard.pbix   # Fichier Power BI Desktop (placeholder)
│   └── dax_formulas.md           # Répertoire des mesures DAX calculées
│
└── docs/                    # Documentation technique et fonctionnelle
    ├── data_dictionary.md   # Dictionnaire de données enrichi (métadonnées)
    ├── methodology.md       # Règles métier, définitions de KPIs et d'anomalies
    └── pitch_presentation.md # Support synthétique préparé pour l'entretien
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
Les données doivent être placées dans le répertoire parent `home-credit-default-risk/` (au même niveau que le dossier `bnp-pf-marketing-datamart/`) :
*   `application_train.csv` (Données clients principales)
*   `previous_application.csv` (Demandes historiques chez Home Credit)
*   `bureau.csv` (Crédits externes)
*   `installments_payments.csv` (Calendrier des règlements d'échéances)
*   `HomeCredit_columns_description.csv` (Référentiel de base)

---

## Contact & Présentation

Ce projet a été entièrement conçu par **Jean-Yves**, étudiant passionné et candidat au poste d'Alternant Business Data Analyst en Finance.
*   **LinkedIn** : [linkedin.com/in/jean-yves-koutsene](https://linkedin.com/in/jean-yves-koutsene)
*   **GitHub** : [https://github.com/YvesKoutsene](https://github.com/YvesKoutsene)