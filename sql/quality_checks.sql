-- =========================================================================
-- PROJET : Datamart Marketing Multi-Pays (BNP Paribas Personal Finance)
-- ETAPE 3 : Gouvernance & Qualité de la Donnée - Requêtes d'audit (DQL)
-- SGBD CIBLE : SQLite / PostgreSQL
-- =========================================================================

-- -------------------------------------------------------------------------
-- REQUÊTE 1 : Diagnostic d'Unicité & Doublons
-- Objectif : S'assurer que le grain de la table (SK_ID_CURR) est unique.
-- -------------------------------------------------------------------------
WITH Unicite_Fact AS (
    SELECT 
        SK_ID_CURR, 
        COUNT(*) as OCCURRENCES
    FROM F_APPLICATIONS
    GROUP BY SK_ID_CURR
)
SELECT 
    'F_APPLICATIONS' as TABLE_NAME,
    COUNT(CASE WHEN OCCURRENCES > 1 THEN 1 END) as NB_DOUBLONS_IDS,
    MAX(OCCURRENCES) as MAX_OCCURRENCES_PAR_ID
FROM Unicite_Fact;


-- -------------------------------------------------------------------------
-- REQUÊTE 2 : Diagnostic de Complétude
-- Objectif : Mesurer la présence de valeurs NULL sur les colonnes décisionnelles.
-- -------------------------------------------------------------------------
SELECT 
    COUNT(*) as TOTAL_CONTRATS,
    -- Mesure sur F_APPLICATIONS
    SUM(CASE WHEN AMT_CREDIT IS NULL THEN 1 ELSE 0 END) as NULL_AMT_CREDIT,
    SUM(CASE WHEN AMT_ANNUITY IS NULL THEN 1 ELSE 0 END) as NULL_AMT_ANNUITY,
    SUM(CASE WHEN AMT_GOODS_PRICE IS NULL THEN 1 ELSE 0 END) as NULL_AMT_GOODS_PRICE,
    -- Taux de complétude global sur F_APPLICATIONS (%)
    ROUND(100.0 * SUM(CASE WHEN AMT_CREDIT IS NOT NULL THEN 1 ELSE 0 END) / COUNT(*), 2) as COMPLETUDE_CREDIT_PCT
FROM F_APPLICATIONS;


-- -------------------------------------------------------------------------
-- REQUÊTE 3 : Diagnostic de Validité et Cohérence Temporelle (Outliers)
-- Objectif : Identifier les anomalies de saisie et de logique métier.
-- -------------------------------------------------------------------------
WITH Client_Validation AS (
    SELECT 
        SK_ID_CURR,
        AGE_YEARS,
        EMPLOYMENT_YEARS,
        -- Règle V1 : L'ancienneté pro ne peut pas dépasser l'âge
        CASE WHEN EMPLOYMENT_YEARS > AGE_YEARS THEN 1 ELSE 0 END as ANOMALIE_ANC_SUP_AGE,
        -- Règle V2 : L'âge doit être légal et cohérent (ex: entre 18 et 100 ans)
        CASE WHEN AGE_YEARS < 18 OR AGE_YEARS > 100 THEN 1 ELSE 0 END as ANOMALIE_AGE_ILLEGAL,
        -- Règle V3 : Revenu total aberrant ou négatif
        CASE WHEN AMT_INCOME_TOTAL <= 0 THEN 1 ELSE 0 END as ANOMALIE_REVENU_NEG_OU_NUL
    FROM D_CLIENT
)
SELECT 
    COUNT(*) as TOTAL_CLIENTS,
    SUM(ANOMALIE_ANC_SUP_AGE) as NB_ANOMALIES_ANC_SUP_AGE,
    ROUND(100.0 * SUM(ANOMALIE_ANC_SUP_AGE) / COUNT(*), 4) as TAUX_ANC_SUP_AGE_PCT,
    SUM(ANOMALIE_AGE_ILLEGAL) as NB_ANOMALIES_AGE_ILLEGAL,
    SUM(ANOMALIE_REVENU_NEG_OU_NUL) as NB_ANOMALIES_REVENU_NEG_OU_NUL
FROM Client_Validation;


-- -------------------------------------------------------------------------
-- REQUÊTE 4 : Détection des Ruptures d'Intégrité Référentielle (Orphelins)
-- Objectif : Vérifier qu'aucune demande dans la table de faits n'est orpheline.
-- -------------------------------------------------------------------------
SELECT 
    COUNT(f.SK_ID_CURR) as TOTAL_FAITS,
    COUNT(CASE WHEN c.SK_ID_CURR IS NULL THEN 1 END) as ORPHELINS_CLIENTS,
    COUNT(CASE WHEN p.SK_ID_CURR IS NULL THEN 1 END) as ORPHELINS_PREV_APPL,
    COUNT(CASE WHEN b.SK_ID_CURR IS NULL THEN 1 END) as ORPHELINS_BUREAU,
    COUNT(CASE WHEN pm.SK_ID_CURR IS NULL THEN 1 END) as ORPHELINS_PAYMENTS
FROM F_APPLICATIONS f
LEFT JOIN D_CLIENT c ON f.SK_ID_CURR = c.SK_ID_CURR
LEFT JOIN D_PREVIOUS_APPLICATIONS p ON f.SK_ID_CURR = p.SK_ID_CURR
LEFT JOIN D_EXTERNAL_BUREAU b ON f.SK_ID_CURR = b.SK_ID_CURR
LEFT JOIN D_PAYMENTS_HISTORY pm ON f.SK_ID_CURR = pm.SK_ID_CURR;


-- -------------------------------------------------------------------------
-- REQUÊTE 5 : Analyse des Valeurs Aberrantes Multi-Variables (outliers de distribution)
-- Objectif : Repérer les clients dont les revenus dépassent 5 écarts-types (Méthode Z-Score simplifiée).
-- -------------------------------------------------------------------------
WITH Income_Stats AS (
    SELECT 
        AVG(AMT_INCOME_TOTAL) as AVG_INCOME,
        -- Calcul de l'écart-type de manière agrégée
        -- SQRT( SUM((x - avg)^2) / count )
        (SELECT AVG((AMT_INCOME_TOTAL - (SELECT AVG(AMT_INCOME_TOTAL) FROM D_CLIENT)) * 
                    (AMT_INCOME_TOTAL - (SELECT AVG(AMT_INCOME_TOTAL) FROM D_CLIENT))) 
         FROM D_CLIENT) as VAR_INCOME
    FROM D_CLIENT
),
Outlier_Thresholds AS (
    SELECT 
        AVG_INCOME,
        -- Écart-type = racine carrée de la variance
        -- SQLite n'a pas SQRT par défaut dans certaines configurations compilées de base,
        -- mais pour être compatible, on utilise la méthode d'approximation ou on s'attend à une variance brute.
        -- Dans SQLite standard, SQRT() est supporté depuis la version 3.35.0.
        SQRT(VAR_INCOME) as STD_INCOME
    FROM Income_Stats
)
SELECT 
    c.SK_ID_CURR,
    c.AMT_INCOME_TOTAL,
    c.NAME_INCOME_TYPE,
    c.AGE_YEARS,
    ROUND((c.AMT_INCOME_TOTAL - t.AVG_INCOME) / t.STD_INCOME, 2) as Z_SCORE
FROM D_CLIENT c
CROSS JOIN Outlier_Thresholds t
WHERE (c.AMT_INCOME_TOTAL - t.AVG_INCOME) / t.STD_INCOME > 5.0
ORDER BY c.AMT_INCOME_TOTAL DESC;
