# Data Quality Scorecard 📊

Ce document présente l'audit automatique de qualité des données de notre **Datamart Marketing**. 
Il répond directement à la mission de gouvernance et qualité des données de la fiche de poste de BNP Paribas Personal Finance.

---

## 1. Synthèse Globale des Métriques

| Dimension de Qualité | Indicateur Clé (KPI) | Score | Statut | Commentaire |
| :--- | :--- | :---: | :---: | :--- |
| **Complétude** | Taux de champs non nulls (Variables Clés) | 97.43% | 🟢 Excellent | Complétude presque totale sur le scope d'octroi. |
| **Unicité** | Zéro doublon sur les Clés Primaires (PK) | 100.00% | 🟢 Conforme | Les identifiants clients sont uniques et sans doublons. |
| **Validité** | Respect des règles métier & limites physiques | 100.00% | 🟢 Conforme | Anomalies d'ancienneté corrigées lors de la transformation. |
| **Intégrité** | Taux de liaisons relationnelles valides | 100.00% | 🟢 Conforme | Aucun enregistrement orphelin (intégrité référentielle préservée). |

---

## 2. Détail des Dimensions

### A. Complétude par Attribut

| Table | Colonne | Taux de Complétude | Statut | Note |
| :--- | :--- | :---: | :---: | :--- |
| `D_CLIENT` | `CODE_GENDER` | 100.00% | 🟢 | Aucun manquant |
| `D_CLIENT` | `AMT_INCOME_TOTAL` | 100.00% | 🟢 | Indispensable pour le calcul du reste à vivre |
| `D_CLIENT` | `AGE_YEARS` | 100.00% | 🟢 | Calculé à partir de la date de naissance |
| `D_CLIENT` | `EMPLOYMENT_YEARS` | 81.99% | 🟡 | 18.01% de valeurs nulles (retraités/sans emploi) |
| `F_APPLICATIONS` | `AMT_CREDIT` | 100.00% | 🟢 | Montant de la transaction d'octroi |
| `F_APPLICATIONS` | `AMT_ANNUITY` | 100.00% | 🟢 | Mensualités dues |
| `F_APPLICATIONS` | `AMT_GOODS_PRICE` | 100.00% | 🟢 | Nettoyé par imputation du montant de crédit |

### B. Validité des Règles Métier

*   **Règle d'Âge Légal** : 100.00% de profils avec un âge valide (>= 18 ans).
*   **Règle de Cohérence Temporelle** : 100.00% des clients ont une ancienneté professionnelle inférieure ou égale à leur âge.
*   **Règle des Montants Positifs** : 100.00% des demandes de crédit possèdent un montant strictement positif.

### C. Cohérence Inter-Tables (Intégrité)

*   Demandes orphelines dans `F_APPLICATIONS` (sans correspondance socio-démographique) : **0** (0.00%)
*   Demandes orphelines de crédit sans historique interne (`D_PREVIOUS_APPLICATIONS`) : **0** (Géré par enregistrements factices par défaut)
*   Demandes orphelines de crédit sans historique concurrents (`D_EXTERNAL_BUREAU`) : **0** (Géré par enregistrements factices par défaut)
*   Demandes orphelines de crédit sans historique de remboursement (`D_PAYMENTS_HISTORY`) : **0** (Géré par enregistrements factices par défaut)

---

## 3. Recommandations d'Amélioration (Gouvernance)

1.  **Suivi de l'ancienneté (`EMPLOYMENT_YEARS`)** : Le taux de vacuité sur cette colonne correspond aux retraités et aux personnes sans emploi déclaré. Il convient de créer une colonne d'exclusion ou un indicateur `FLAG_SANS_EMPLOI` pour distinguer clairement les vraies valeurs manquantes des cas fonctionnels légitimes.
2.  **Imputation systématique** : L'imputation du montant des biens financés (`AMT_GOODS_PRICE`) par le montant du crédit (`AMT_CREDIT`) est fonctionnelle, mais il serait plus propre en production de séparer l'indicateur d'origine de l'indicateur nettoyé.
