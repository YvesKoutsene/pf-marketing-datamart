# Étape 1 : Conception & Modélisation Décisionnelle (MCD/MLD)

Pour transformer des données brutes hétérogènes en un système d'information performant et propice à l'analyse (Power BI), nous concevons un **Datamart en étoile** (Star Schema). 

Ce choix d'architecture respecte les préconisations de **Ralph Kimball**, référence absolue en business intelligence. Il permet de :
1.  **Simplifier l'écriture des requêtes analytiques** (SQL plus lisible, moins de jointures complexes).
2.  **Optimiser les performances** de Power BI grâce au moteur tabulaire VertiPaq.
3.  **Éviter les ambiguïtés de filtrage** courantes dans les modèles relationnels en flocons ou en "flat tables".

---

## 1. Schéma Conceptuel du Datamart en Étoile

La table de faits centrale représente l'acte de demande de crédit actuel (notre unité de mesure ou grain de la table). Elle est entourée de tables de dimensions décrivant les clients, leur historique de crédit interne, leur historique externe (bureau) et leur comportement de paiement.

```text
                  ┌─────────────────────────────────┐
                  │          D_TEMPS                │
                  │  (Date de décision, Mois...)    │
                  └────────────────┬────────────────┘
                                   │
                                   ▼ (1)
┌──────────────────┐ (1)  ┌─────────────────┐  (1) ┌────────────────────────┐
│  D_CLIENT        ├─────►│ F_APPLICATIONS  │◄─────┤ D_PREVIOUS_APPLICATIONS│
│ (Socio-démo)     │      │  (Faits/Prêts)  │      │ (Synthèse des demandes)│
└──────────────────┘      └────────┬────────┘      └────────────────────────┘
                                   ▲
                                   │ (1)
                  ┌────────────────┴────────────────┐
                  │  D_EXTERNAL_BUREAU              │
                  │  (Historique concurrents)      │
                  └─────────────────────────────────┘
                                   ▲
                                   │ (1)
                  ┌────────────────┴────────────────┐
                  │  D_PAYMENTS_HISTORY             │
                  │  (Comportement de paiement)     │
                  └─────────────────────────────────┘
                                   ▲
                                   │ (1)
                  ┌────────────────┴────────────────┐
                  │  D_SEGMENTATION                 │
                  │  (Risque × Valeur - Étape 4)    │
                  └─────────────────────────────────┘
```

---

## 2. Dictionnaire et Description des Tables

### Table de Faits : `F_APPLICATIONS` (Fait principal)
Chaque ligne correspond à une demande de crédit actuelle reçue par BNP PF.
*   `SK_ID_CURR` (INT, PK/FK) : Identifiant unique de la demande actuelle et du client.
*   `AMT_CREDIT` (DECIMAL) : Montant total du crédit accordé ou demandé.
*   `AMT_ANNUITY` (DECIMAL) : Mensualité (annuité) du crédit à rembourser.
*   `AMT_GOODS_PRICE` (DECIMAL) : Prix d'achat du bien financé par le crédit.
*   `NAME_CONTRACT_TYPE` (VARCHAR) : Type de prêt (Cash Loans ou Revolving Loans).
*   `TARGET` (INT) : Statut de remboursement de la première échéance (1 = défaut ou impayé, 0 = remboursement conforme).

### Dimension : `D_CLIENT` (Socio-Démographique)
Contient les attributs stables du demandeur.
*   `SK_ID_CURR` (INT, PK) : Identifiant unique du client.
*   `CODE_GENDER` (VARCHAR) : Genre du client (M / F).
*   `CNT_CHILDREN` (INT) : Nombre d'enfants à charge.
*   `AMT_INCOME_TOTAL` (DECIMAL) : Revenu annuel du client.
*   `NAME_INCOME_TYPE` (VARCHAR) : Origine des revenus (Salarié, Retraité, Commercial...).
*   `NAME_EDUCATION_TYPE` (VARCHAR) : Niveau d'études maximal atteint.
*   `NAME_FAMILY_STATUS` (VARCHAR) : Statut familial (Marié, Célibataire...).
*   `NAME_HOUSING_TYPE` (VARCHAR) : Mode de logement (Propriétaire, Locataire...).
*   `AGE_YEARS` (INT) : Âge du client calculé en années à partir de sa date de naissance.
*   `EMPLOYMENT_YEARS` (INT) : Ancienneté professionnelle calculée en années.

### Dimension : `D_PREVIOUS_APPLICATIONS` (Historique Commercial Interne)
Synthèse au niveau client de ses précédentes demandes d'engagement chez nous. Elle évite d'avoir une relation 1-N complexe dans Power BI.
*   `SK_ID_CURR` (INT, PK) : Identifiant unique du client.
*   `NB_PREV_APPLICATIONS` (INT) : Nombre total de demandes de crédit passées.
*   `APPROVAL_RATE_PREV` (DECIMAL) : Part des demandes passées qui ont été acceptées.
*   `TOTAL_PREV_CREDIT` (DECIMAL) : Montant total déjà emprunté chez nous historiquement.
*   `LAST_DECISION_STATUS` (VARCHAR) : Statut de la toute dernière demande passée (Approved, Refused, Canceled).

### Dimension : `D_EXTERNAL_BUREAU` (Historique Risque Externe)
Données agrégées issues du Bureau du Crédit (crédits chez nos concurrents).
*   `SK_ID_CURR` (INT, PK) : Identifiant unique du client.
*   `NB_ACTIVE_LOANS_BUREAU` (INT) : Nombre de crédits en cours d'amortissement chez les concurrents.
*   `TOTAL_DEBT_BUREAU` (DECIMAL) : Montant total restant dû chez les concurrents.
*   `MAX_DAYS_OVERDUE_BUREAU` (INT) : Nombre maximal de jours de retard de paiement enregistrés à l'externe.

### Dimension : `D_PAYMENTS_HISTORY` (Comportement Réel de Remboursement)
Indicateurs issus de l'analyse historique des échéanciers de paiement passés.
*   `SK_ID_CURR` (INT, PK) : Identifiant unique du client.
*   `AVG_PAYMENT_DELAY` (DECIMAL) : Nombre moyen de jours de retard de paiement sur ses contrats passés.
*   `TOTAL_MISSED_PAYMENTS` (INT) : Nombre d'échéances pour lesquelles le client a versé moins que le montant requis.
*   `RATIO_PAID_VS_REQUIRED` (DECIMAL) : Part moyenne du montant de l'échéance effectivement payée par le client.

---

## 3. Définitions des Règles Métier Clés

Pour que les analystes des pays parlent le même langage, nous formalisons dès la modélisation les règles métier :

1.  **Taux d'acceptation historique (`APPROVAL_RATE_PREV`)** :
    $$\text{Taux d'acceptation} = \frac{\text{Nombre de demandes au statut 'Approved'}}{\text{Nombre total de demandes du client}}$$
2.  **Ancienneté Professionnelle (`EMPLOYMENT_YEARS`)** :
    $$\text{Ancienneté} = \frac{\text{DAYS\_EMPLOYED}}{-365.25}$$
    *Règle d'anomalie :* Si `DAYS_EMPLOYED` vaut une valeur positive aberrante (ex: $365243$ jours), l'ancienneté est forcée à `NULL` (traitée à l'Étape 3).
3.  **Taux de Défaut Actuel (`Default Rate`)** :
    $$\text{Taux de défaut} = \frac{\sum(\text{TARGET})}{\text{Nombre de clients total}}$$
4.  **Jour de retard de paiement sur une échéance** :
    $$\text{Retard} = \max(0, \text{DAYS\_ENTRY\_PAYMENT} - \text{DAYS\_INSTALMENT})$$
    *(DAYS_ENTRY_PAYMENT est la date de paiement réelle et DAYS_INSTALMENT est la date prévue. Une valeur négative indique un paiement en avance, donc on applique la fonction max pour ne garder que les retards réels).*
