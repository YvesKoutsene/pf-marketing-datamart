# Référentiel des Formules DAX — Tableau de bord Décisionnel

Ce référentiel contient les mesures DAX (Data Analysis Expressions) conçues pour le modèle Power BI en étoile. Elles respectent les conventions de nommage professionnelles et sont optimisées pour le moteur VertiPaq.

---

## 1. KPIs Fondamentaux (Portefeuille)

### Nombre de Clients Actuels
```dax
[Total Clients] = COUNTROWS(F_APPLICATIONS)
```

### Encours Total Financé
```dax
[Volume Crédit Total] = SUM(F_APPLICATIONS[AMT_CREDIT])
```

### Mensualité Moyenne
```dax
[Mensualité Moyenne] = AVERAGE(F_APPLICATIONS[AMT_ANNUITY])
```

### Taux de Défaut Réel (TARGET)
```dax
[Taux de Défaut] = 
DIVIDE(
    CALCULATE(
        COUNTROWS(F_APPLICATIONS),
        F_APPLICATIONS[TARGET] = 1
    ),
    [Total Clients],
    0
)
```
*Note : TARGET = 1 représente un défaut de paiement sur la première échéance.*

---

## 2. Indicateurs Comportementaux (Dimensions)

### Taux d'Acceptation Historique (Internal History)
```dax
[Taux Acceptation Historique] = AVERAGE(D_PREVIOUS_APPLICATIONS[APPROVAL_RATE_PREV])
```

### Retard Moyen de Paiement (Jours)
```dax
[Retard Moyen Paiement] = AVERAGE(D_PAYMENTS_HISTORY[AVG_PAYMENT_DELAY])
```

### Encours de Dette Externe Moyen (Bureau concurrents)
```dax
[Dette Externe Moyenne] = AVERAGE(D_EXTERNAL_BUREAU[TOTAL_DEBT_BUREAU])
```

---

## 3. Intelligence Temporelle (Time Intelligence)

Ces mesures s'appuient sur la relation active entre `F_APPLICATIONS[DECISION_DATE_KEY]` et `D_TEMPS[DATE_KEY]`.

### Volume Financé sur le Mois Précédent (MoM)
```dax
[Volume Crédit M-1] = 
CALCULATE(
    [Volume Crédit Total],
    DATEADD(D_TEMPS[CALENDAR_DATE], -1, MONTH)
)
```

### Évolution Mensuelle du Volume (%)
```dax
[Evolution Volume MoM %] = 
VAR _actuel = [Volume Crédit Total]
VAR _precedent = [Volume Crédit M-1]
RETURN
DIVIDE(
    _actuel - _precedent,
    _precedent,
    0
)
```

### Cumul Annuel à Date (YTD)
```dax
[Volume Crédit YTD] = 
TOTALYTD(
    [Volume Crédit Total],
    D_TEMPS[CALENDAR_DATE]
)
```

---

## 4. Mesures de Segmentation & Dynamique Risque

Ces mesures permettent d'adapter dynamiquement la vision des segments dans les visuels.

### Part du Volume par Segment (%)
```dax
[Part Volume Segment %] = 
DIVIDE(
    [Volume Crédit Total],
    CALCULATE(
        [Volume Crédit Total],
        ALL(D_SEGMENTATION)
    ),
    0
)
```

### Taux de Défaut Relatif du Segment
Ce calcul compare le taux de défaut d'un segment par rapport au taux de défaut moyen de tout le portefeuille pour mesurer la sur-représentation du risque.
```dax
[Indice de Risque Segment] = 
VAR _taux_segment = [Taux de Défaut]
VAR _taux_global = CALCULATE([Taux de Défaut], ALL(D_SEGMENTATION))
RETURN
DIVIDE(
    _taux_segment,
    _taux_global,
    0
)
```
*Interprétation : Un indice de 1.5 signifie que ce segment fait 50% de défauts de plus que la moyenne générale.*

---

## 5. Gouvernance & Qualité de la Donnée

Ces mesures servent à piloter la qualité de la donnée sur la Page 3 du dashboard.

### Index Qualité Global (Pour le visuel Gauge/Jauge)
Il calcule la moyenne agrégée de nos contrôles clés : complétude des colonnes stratégiques et respect des règles de cohérence fonctionnelle.
```dax
[Index Qualité Global] = 
-- 1. Taux de complétude des variables clés (CODE_GENDER, AMT_INCOME_TOTAL, AGE_YEARS, AMT_CREDIT)
VAR _completude_gender = 
    DIVIDE(
        CALCULATE(COUNTROWS(D_CLIENT), NOT(ISBLANK(D_CLIENT[CODE_GENDER]))), 
        COUNTROWS(D_CLIENT), 
        0
    )

VAR _completude_income = 
    DIVIDE(
        CALCULATE(COUNTROWS(D_CLIENT), NOT(ISBLANK(D_CLIENT[AMT_INCOME_TOTAL]))), 
        COUNTROWS(D_CLIENT), 
        0
    )

VAR _completude_age = 
    DIVIDE(
        CALCULATE(COUNTROWS(D_CLIENT), NOT(ISBLANK(D_CLIENT[AGE_YEARS]))), 
        COUNTROWS(D_CLIENT), 
        0
    )

VAR _completude_credit = 
    DIVIDE(
        CALCULATE(COUNTROWS(F_APPLICATIONS), NOT(ISBLANK(F_APPLICATIONS[AMT_CREDIT]))), 
        COUNTROWS(F_APPLICATIONS), 
        0
    )

-- 2. Taux de validité des règles métiers (Âge >= 18 et Ancienneté pro <= Âge)
VAR _validite_age = 
    DIVIDE(
        CALCULATE(COUNTROWS(D_CLIENT), D_CLIENT[AGE_YEARS] >= 18), 
        COUNTROWS(D_CLIENT), 
        0
    )

VAR _validite_anciennete = 
    DIVIDE(
        CALCULATE(COUNTROWS(D_CLIENT), D_CLIENT[EMPLOYMENT_YEARS] <= D_CLIENT[AGE_YEARS] || ISBLANK(D_CLIENT[EMPLOYMENT_YEARS])), 
        COUNTROWS(D_CLIENT), 
        0
    )

-- 3. Moyenne des 6 indicateurs de qualité
RETURN
DIVIDE(
    _completude_gender + _completude_income + _completude_age + _completude_credit + _validite_age + _validite_anciennete,
    6,
    0
)
```

