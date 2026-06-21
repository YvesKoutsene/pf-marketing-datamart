# Dictionnaire de Données — Datamart Marketing Multi-Pays 📖

Ce dictionnaire de données documente l'ensemble des tables et des colonnes constituant notre **Datamart en Étoile**. Il sert de référence unique (Single Source of Truth) pour les analystes métiers et les équipes IT de BNP Paribas Personal Finance.

---

## 1. Table de Faits : `F_APPLICATIONS`
*   **Description :** Centralise les demandes de crédit à la consommation courantes. Chaque ligne représente une demande d'octroi active.
*   **Grain de la table :** 1 ligne = 1 demande de crédit client (`SK_ID_CURR`).

| Nom de la Colonne | Type SQL | Clé / Index | Table Source (Origine) | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | `application_train.csv` | Identifiant unique de la demande de crédit courante et du client associé. | Non nul, strictement unique. |
| `DECISION_DATE_KEY` | `INT` | `FK` | Généré (Python) | Clé de dimension temporelle pointant vers la table `D_TEMPS` (Format `YYYYMMDD`). | Clé de jointure temporelle obligatoire. |
| `AMT_CREDIT` | `DECIMAL` | - | `application_train.csv` | Montant total du crédit consenti par l'établissement. | Strictement positif (> 0). |
| `AMT_ANNUITY` | `DECIMAL` | - | `application_train.csv` | Montant de l'annuité (mensualité de remboursement) due par le client. | Rempli par 0.0 si manquant. |
| `AMT_GOODS_PRICE` | `DECIMAL` | - | `application_train.csv` | Prix d'achat du bien financé par le crédit (ex: voiture pour crédit auto). | Imputé avec le montant du crédit si manquant. |
| `NAME_CONTRACT_TYPE` | `VARCHAR` | - | `application_train.csv` | Catégorie de prêt demandé (Cash loans / Revolving loans). | Choix limité : Prêt amortissable ou Réserve. |
| `TARGET` | `INT` | - | `application_train.csv` | Variable cible de risque : 1 = Impayé de remboursement sur la 1ère échéance ; 0 = Remboursement OK. | Valeurs booléennes autorisées : (0, 1) uniquement. |

---

## 2. Dimension : `D_CLIENT` (Socio-Démographique)
*   **Description :** Attributs socio-démographiques stables du client demandeur.
*   **Grain :** 1 ligne = 1 client unique.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | `application_train.csv` | Identifiant unique du client. | Clé de jointure. |
| `CODE_GENDER` | `VARCHAR` | - | `application_train.csv` | Genre déclaratif du client (M, F). | Remplacé par `XNA` si non renseigné. |
| `CNT_CHILDREN` | `INT` | - | `application_train.csv` | Nombre d'enfants à charge déclarés par le client. | Valeur entière positive ou nulle. |
| `AMT_INCOME_TOTAL` | `DECIMAL` | - | `application_train.csv` | Revenu total annuel déclaré par le demandeur. | Supérieur à 0. |
| `NAME_INCOME_TYPE` | `VARCHAR` | - | `application_train.csv` | Catégorie professionnelle (Salarié, Retraité, Commercial, etc.). | Valeurs issues d'une table de référence. |
| `NAME_EDUCATION_TYPE` | `VARCHAR` | - | `application_train.csv` | Niveau d'études maximal déclaré. | Métrique d'évaluation comportementale. |
| `NAME_FAMILY_STATUS` | `VARCHAR` | - | `application_train.csv` | Statut matrimonial (Marié, Célibataire, Divorcé, etc.). | Variable d'appréciation du foyer. |
| `NAME_HOUSING_TYPE` | `VARCHAR` | - | `application_train.csv` | Statut de logement (Propriétaire, Locataire, Logé par l'employeur, etc.). | Indicateur de stabilité budgétaire. |
| `AGE_YEARS` | `INT` | - | `application_train.csv` | Âge du client au moment de la demande en années. | Calculé : $\text{floor}(-DAYS\_BIRTH / 365.25)$. Doit être >= 18. |
| `EMPLOYMENT_YEARS` | `INT` | - | `application_train.csv` | Ancienneté professionnelle déclarée en années. | Calculé : $\text{floor}(-DAYS\_EMPLOYED / 365.25)$. Forcé à `NULL` si `DAYS_EMPLOYED > 0`. |

---

## 3. Dimension : `D_PREVIOUS_APPLICATIONS` (Historique Interne)
*   **Description :** Historique agrégé des demandes passées du client au sein de BNP PF.
*   **Grain :** 1 ligne = 1 client unique.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | `previous_application.csv` | Identifiant client. | Clé de jointure. |
| `NB_PREV_APPLICATIONS` | `INT` | - | `previous_application.csv` | Nombre de demandes de financement historiques chez nous. | Valeur par défaut : 0 si aucun historique. |
| `APPROVAL_RATE_PREV` | `DECIMAL` | - | `previous_application.csv` | Taux d'acceptation de ses demandes passées (ex: 0.75 pour 3 approuvées sur 4). | Taux compris entre 0.00 et 1.00. |
| `TOTAL_PREV_CREDIT` | `DECIMAL` | - | `previous_application.csv` | Somme cumulée des financements accordés par le passé. | Valeur par défaut : 0.00 si aucun historique. |
| `LAST_DECISION_STATUS` | `VARCHAR` | - | `previous_application.csv` | Statut de la toute dernière demande passée (Approved, Refused, Canceled). | Remplacé par `No history` si aucun antécédent. |

---

## 4. Dimension : `D_EXTERNAL_BUREAU` (Risque Concurrentiel)
*   **Description :** Crédits en cours et antécédents de paiement chez d'autres banques (Bureau du Crédit).
*   **Grain :** 1 ligne = 1 client unique.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | `bureau.csv` | Identifiant client. | Clé de jointure. |
| `NB_ACTIVE_LOANS_BUREAU` | `INT` | - | `bureau.csv` | Nombre de prêts actuellement ouverts et actifs chez la concurrence. | Valeur par défaut : 0. |
| `TOTAL_DEBT_BUREAU` | `DECIMAL` | - | `bureau.csv` | Encours total de la dette restant à rembourser chez les concurrents. | Valeur par défaut : 0.00. Source : `AMT_CREDIT_SUM_DEBT`. |
| `MAX_DAYS_OVERDUE_BUREAU` | `INT` | - | `bureau.csv` | Nombre maximum de jours de retard de paiement enregistrés à l'externe. | Valeur par défaut : 0. |

---

## 5. Dimension : `D_PAYMENTS_HISTORY` (Comportement de Remboursement)
*   **Description :** Indicateurs comportementaux d'incidents de paiement sur les anciens prêts accordés.
*   **Grain :** 1 ligne = 1 client unique.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | `installments_payments.csv` | Identifiant client. | Clé de jointure. |
| `AVG_PAYMENT_DELAY` | `DECIMAL` | - | `installments_payments.csv` | Nombre moyen de jours de retard constatés sur ses échéances passées. | Moyenne de : $\max(0, entry - instalment)$. Valeur par défaut : 0.0. |
| `TOTAL_MISSED_PAYMENTS` | `INT` | - | `installments_payments.csv` | Nombre total d'échéances payées partiellement ou non payées. | Comptabilise les lignes où $AMT\_PAYMENT < AMT\_INSTALMENT$. Défaut : 0. |
| `RATIO_PAID_VS_REQUIRED` | `DECIMAL` | - | `installments_payments.csv` | Somme payée sur somme requise moyenne (ex: 1.00 pour remboursement complet). | Cadré à 1.00 pour les clients sans historique. |

---

## 6. Dimension : `D_SEGMENTATION` (Marketing et Scoring)
*   **Description :** Classification bidimensionnelle (Valeur × Risque) calculée par notre moteur en Python.
*   **Grain :** 1 ligne = 1 client unique.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `SK_ID_CURR` | `INT` | `PK` | Généré (Python) | Identifiant client. | Clé de jointure. |
| `SEGMENT_VALUE` | `VARCHAR` | - | Calculé | Niveau de valeur du client selon son montant de crédit demandé (Low, Medium, High). | Découpé en tertiles. |
| `SEGMENT_RISK` | `VARCHAR` | - | Calculé | Niveau de risque de crédit estimé selon son historique d'incidents (Low, Medium, High). | Calculé sur un score comportemental pondéré de 0 à 100. |
| `SEGMENT_CLUSTER` | `VARCHAR` | - | Calculé | Cluster croisé final (ex : `High Value - Low Risk`). | Concaténation : `SEGMENT_VALUE + " - " + SEGMENT_RISK`. |

---

## 7. Dimension : `D_TEMPS` (Calendaire)
*   **Description :** Table calendaire pour la gestion de l'intelligence temporelle dans Power BI.
*   **Grain :** 1 ligne = 1 jour calendaire.

| Nom de la Colonne | Type SQL | Clé | Table Source | Description Fonctionnelle | Règle de Qualité / Imputation |
| :--- | :--- | :---: | :--- | :--- | :--- |
| `DATE_KEY` | `INT` | `PK` | Généré | Clé unique au format numérique YYYYMMDD (ex : 20251231). | Strictement unique et ordonnée. |
| `CALENDAR_DATE` | `DATE` | - | Généré | Date au format standard ISO (YYYY-MM-DD). | Unique et continue (sans trou de date). |
| `YEAR` | `INT` | - | Généré | Année civile associée. | Valeur entre 2015 et 2026. |
| `MONTH` | `INT` | - | Généré | Numéro du mois (1 à 12). | - |
| `MONTH_NAME` | `VARCHAR` | - | Généré | Nom complet du mois en texte (ex : Décembre). | Utile pour les axes de graphiques Power BI. |
| `QUARTER` | `INT` | - | Généré | Trimestre associé (1 à 4). | - |
| `WEEK_OF_YEAR` | `INT` | - | Généré | Numéro de la semaine dans l'année (1 à 53). | - |
| `DAY_OF_WEEK` | `INT` | - | Généré | Index du jour de la semaine (1 = Lundi, 7 = Dimanche). | - |
| `DAY_OF_WEEK_NAME` | `VARCHAR` | - | Généré | Nom du jour de la semaine en texte (ex : Mercredi). | - |
