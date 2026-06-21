-- =========================================================================
-- PROJET : Datamart Marketing Multi-Pays (BNP Paribas Personal Finance)
-- ETAPE 5 : Analyse Décisionnelle & Calcul des KPIs Métiers (SQL)
-- SGBD CIBLE : SQLite / PostgreSQL
-- =========================================================================

-- -------------------------------------------------------------------------
-- REQUÊTE 1 : KPIs Généraux du Portefeuille Actuel
-- Objectif : Mesurer le volume, l'encours moyen et le taux de défaut global.
-- -------------------------------------------------------------------------
SELECT 
    COUNT(SK_ID_CURR) as TOTAL_CLIENTS,
    ROUND(SUM(AMT_CREDIT), 2) as ENCOURS_TOTAL_EMPRUNTE,
    ROUND(AVG(AMT_CREDIT), 2) as MONTANT_MOYEN_CREDIT,
    ROUND(AVG(AMT_ANNUITY), 2) as MENSUALITE_MOYENNE,
    -- Taux de défaut global
    ROUND(100.0 * SUM(TARGET) / COUNT(*), 2) as TAUX_DEFAUT_GLOBAL_PCT
FROM F_APPLICATIONS;


-- -------------------------------------------------------------------------
-- REQUÊTE 2 : Analyse de la Performance par Type de Contrat
-- Objectif : Comparer les Prêts Personnels (Cash Loans) et Crédits Renouvelables.
-- -------------------------------------------------------------------------
SELECT 
    NAME_CONTRACT_TYPE,
    COUNT(SK_ID_CURR) as NB_DEMANDES,
    ROUND(100.0 * COUNT(SK_ID_CURR) / (SELECT COUNT(*) FROM F_APPLICATIONS), 2) as SHARE_PCT,
    ROUND(AVG(AMT_CREDIT), 2) as MONTANT_MOYEN_CREDIT,
    ROUND(100.0 * SUM(TARGET) / COUNT(*), 2) as TAUX_DEFAUT_PCT
FROM F_APPLICATIONS
GROUP BY NAME_CONTRACT_TYPE;


-- -------------------------------------------------------------------------
-- REQUÊTE 3 : Analyse Croisée de notre Segmentation Risque × Valeur
-- Objectif : Valider que le taux de défaut réel est corrélé à nos clusters.
--            C'est la requête reine pour prouver la valeur de la segmentation.
-- -------------------------------------------------------------------------
SELECT 
    s.SEGMENT_CLUSTER,
    s.SEGMENT_VALUE,
    s.SEGMENT_RISK,
    COUNT(f.SK_ID_CURR) as NB_CLIENTS,
    ROUND(AVG(f.AMT_CREDIT), 2) as ENCOURS_MOYEN,
    -- Risque interne (taux de défaut réel constaté TARGET=1)
    ROUND(100.0 * SUM(f.TARGET) / COUNT(f.SK_ID_CURR), 2) as TAUX_DEFAUT_REEL_PCT,
    -- Risque de retard moyen (D_PAYMENTS_HISTORY)
    ROUND(AVG(p.AVG_PAYMENT_DELAY), 1) as RETARD_PAIEMENT_MOYEN_JOURS
FROM F_APPLICATIONS f
JOIN D_SEGMENTATION s ON f.SK_ID_CURR = s.SK_ID_CURR
JOIN D_PAYMENTS_HISTORY p ON f.SK_ID_CURR = p.SK_ID_CURR
GROUP BY s.SEGMENT_CLUSTER, s.SEGMENT_VALUE, s.SEGMENT_RISK
ORDER BY TAUX_DEFAUT_REEL_PCT DESC;


-- -------------------------------------------------------------------------
-- REQUÊTE 4 : Analyse de l'Historique Interne vs Risque Actuel
-- Objectif : Vérifier si le taux d'acceptation historique influence le défaut.
-- -------------------------------------------------------------------------
WITH Previous_Stats AS (
    SELECT 
        CASE 
            WHEN APPROVAL_RATE_PREV = 0 THEN '0% (Aucun approuvé)'
            WHEN APPROVAL_RATE_PREV > 0 AND APPROVAL_RATE_PREV <= 0.5 THEN ']0% - 50%]'
            WHEN APPROVAL_RATE_PREV > 0.5 AND APPROVAL_RATE_PREV < 1.0 THEN ']50% - 100%['
            ELSE '100% (Tous approuvés)'
        END as TRANCHE_ACCEPTATION_HISTORIQUE,
        f.TARGET
    FROM F_APPLICATIONS f
    JOIN D_PREVIOUS_APPLICATIONS p ON f.SK_ID_CURR = p.SK_ID_CURR
)
SELECT 
    TRANCHE_ACCEPTATION_HISTORIQUE,
    COUNT(*) as NB_CLIENTS,
    ROUND(100.0 * SUM(TARGET) / COUNT(*), 2) as TAUX_DEFAUT_PCT
FROM Previous_Stats
GROUP BY TRANCHE_ACCEPTATION_HISTORIQUE
ORDER BY TAUX_DEFAUT_PCT DESC;


-- -------------------------------------------------------------------------
-- REQUÊTE 5 : Analyse Temporelle d'Octroi (par Mois de Décision)
-- Objectif : Suivre la dynamique commerciale sur notre ancrage temporel (Fin 2025).
-- -------------------------------------------------------------------------
SELECT 
    t.YEAR,
    t.MONTH_NAME,
    COUNT(f.SK_ID_CURR) as NB_CREDITS_OCTROYES,
    ROUND(SUM(f.AMT_CREDIT), 2) as VOLUME_FINANCE,
    ROUND(AVG(f.AMT_CREDIT), 2) as ENCOURS_MOYEN,
    ROUND(100.0 * SUM(f.TARGET) / COUNT(*), 2) as TAUX_DEFAUT_PCT
FROM F_APPLICATIONS f
JOIN D_TEMPS t ON f.DECISION_DATE_KEY = t.DATE_KEY
GROUP BY t.YEAR, t.MONTH, t.MONTH_NAME
ORDER BY t.YEAR, t.MONTH;
