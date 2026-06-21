# Pitch de Présentation : Cas d'Usage Décisionnel 🎯

Ce document constitue le support synthétique de présentation du projet **Datamart Marketing Multi-Pays** pour ton entretien avec **Joséphine** et **Grégory** (Direction Data & IA - Centre d'expertise Analytics & BI chez BNP Paribas Personal Finance).

---

## 1. L'Accroche : Pourquoi ce projet ? (Le Pitch Business)

> *"Pour accompagner l'objectif de BNP Paribas Personal Finance de faire croître ses encours de +4% par an tout en visant un RONE de 17% d'ici 2028, la maîtrise du risque et le ciblage marketing ne sont pas des sujets secondaires : ce sont des impératifs stratégiques. J'ai conçu ce projet de bout en bout pour démontrer comment un Business Data Analyst peut fiabiliser des flux complexes et les transformer en leviers de croissance directe pour les pays."*

---

## 2. La Démonstration Technique : Ce que j'ai réalisé

J'ai pris un jeu de données réel et complexe de crédit à la consommation (**307 511 clients**, plusieurs millions de lignes d'historiques) pour simuler les flux multi-pays de Personal Finance et j'ai construit :

1.  **Une Modélisation Décisionnelle (MCD/MLD en Étoile)** : Un modèle Kimball à 7 tables (faits `F_APPLICATIONS` entourée de dimensions socio-démographiques, historiques internes, externes et temporelles) optimisé pour le moteur VertiPaq de Power BI.
2.  **Un Pipeline d'Ingestion & Nettoyage (Python)** : Chargement optimisé par blocs (*chunks*) pour économiser la mémoire RAM et imputation automatique des anomalies (ex. correction des anciennetés de travail aberrantes).
3.  **Un Moteur de Qualité (Data Quality Scorecard)** : Un script Python/SQL automatisé évaluant 4 dimensions (Complétude, Unicité, Validité, Intégrité référentielle) pour garantir une donnée 100% fiable avant reporting.
4.  **Une Segmentation Client Algorithmique (Python)** : Une matrice Risque comportemental (0-100 basé sur les incidents Bureau et retards réels) × Valeur (tertiles d'encours de crédit demandé).

---

## 3. Les Révélations Métiers (Le "Wow" de l'entretien)

En croisant ma segmentation avec les performances réelles du portefeuille dans la base de données, j'ai dégagé des insights stratégiques majeurs pour les équipes marketing :

*   **Identification du Segment Champion (`High Value - Low Risk`)** :
    *   **Volume** : Représente **25,18%** de notre portefeuille (77 431 clients).
    *   **Performance** : Affiche le taux de défaut le plus bas de tout le portefeuille (**5,86%** contre une moyenne globale de 8,08%) et un retard de paiement moyen quasi nul (**0,1 jour**).
    *   **Recommandation Marketing** : C'est notre cible prioritaire pour des campagnes de multi-détention (assurance, cartes de crédit) et des hausses de plafonds d'octroi.
*   **Alerte sur le Segment Critique (`Medium Value - High Risk`)** :
    *   **Volume** : Représente 6,30% du portefeuille (19 368 clients).
    *   **Performance** : Son taux de défaut réel explose à **13,24%** (plus du double du segment champion) avec un indice de retard de 3,3 jours.
    *   **Recommandation Octroi** : Mettre en place des politiques d'octroi restrictives et un système d'alerte précoce (Early Warning System) sur ce segment.

---

## 4. Pourquoi cela prouve que je suis opérationnel dès le Jour 1

*   **Rigueur SQL & Python** : Je ne fais pas que des requêtes simples, j'écris des CTE, du fenêtrage, et des jointures complexes pour auditer la cohérence de modèles entiers.
*   **Culture Data Warehouse** : Je maîtrise l'intégrité référentielle et les relations entre tables de faits et de dimensions (Kimball), garantissant des rapports stables et performants.
*   **Orientation Business** : Je sais traduire des lignes de code en indicateurs clés de performance et en recommandations commerciales actionnables pour les pays.
*   **Autonomie & Posture** : La gestion d'un pipeline complet en local montre ma capacité à prendre en main des projets transverses de A à Z avec rigueur et méthode.
