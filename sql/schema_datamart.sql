-- =========================================================================
-- PROJET : Datamart Marketing Multi-Pays (BNP Paribas Personal Finance)
-- ETAPE 1 : Modélisation Décisionnelle - Script de création des tables (DDL)
-- SGBD CIBLE : SQLite / PostgreSQL (Syntaxe standard ANSI)
-- =========================================================================

-- Réinitialisation des tables existantes (Respect de l'ordre des contraintes)
DROP TABLE IF EXISTS F_APPLICATIONS;
DROP TABLE IF EXISTS D_CLIENT;
DROP TABLE IF EXISTS D_PREVIOUS_APPLICATIONS;
DROP TABLE IF EXISTS D_EXTERNAL_BUREAU;
DROP TABLE IF EXISTS D_PAYMENTS_HISTORY;
DROP TABLE IF EXISTS D_SEGMENTATION;
DROP TABLE IF EXISTS D_TEMPS;

-- -------------------------------------------------------------------------
-- 1. Table de Dimension : D_CLIENT (Informations Socio-Démographiques)
-- -------------------------------------------------------------------------
CREATE TABLE D_CLIENT (
    SK_ID_CURR INT PRIMARY KEY,
    CODE_GENDER VARCHAR(10),
    CNT_CHILDREN INT,
    AMT_INCOME_TOTAL DECIMAL(15, 2),
    NAME_INCOME_TYPE VARCHAR(50),
    NAME_EDUCATION_TYPE VARCHAR(100),
    NAME_FAMILY_STATUS VARCHAR(50),
    NAME_HOUSING_TYPE VARCHAR(50),
    AGE_YEARS INT,
    EMPLOYMENT_YEARS INT
);

-- -------------------------------------------------------------------------
-- 2. Table de Dimension : D_PREVIOUS_APPLICATIONS (Historique Interne)
-- -------------------------------------------------------------------------
CREATE TABLE D_PREVIOUS_APPLICATIONS (
    SK_ID_CURR INT PRIMARY KEY,
    NB_PREV_APPLICATIONS INT,
    APPROVAL_RATE_PREV DECIMAL(5, 4),
    TOTAL_PREV_CREDIT DECIMAL(15, 2),
    LAST_DECISION_STATUS VARCHAR(30)
);

-- -------------------------------------------------------------------------
-- 3. Table de Dimension : D_EXTERNAL_BUREAU (Risque Financier Externe)
-- -------------------------------------------------------------------------
CREATE TABLE D_EXTERNAL_BUREAU (
    SK_ID_CURR INT PRIMARY KEY,
    NB_ACTIVE_LOANS_BUREAU INT,
    TOTAL_DEBT_BUREAU DECIMAL(15, 2),
    MAX_DAYS_OVERDUE_BUREAU INT
);

-- -------------------------------------------------------------------------
-- 4. Table de Dimension : D_PAYMENTS_HISTORY (Comportement de Remboursement)
-- -------------------------------------------------------------------------
CREATE TABLE D_PAYMENTS_HISTORY (
    SK_ID_CURR INT PRIMARY KEY,
    AVG_PAYMENT_DELAY DECIMAL(8, 2),
    TOTAL_MISSED_PAYMENTS INT,
    RATIO_PAID_VS_REQUIRED DECIMAL(5, 4)
);

-- -------------------------------------------------------------------------
-- 5. Table de Dimension : D_SEGMENTATION (Dimension Analytique Risque/Valeur)
-- -------------------------------------------------------------------------
CREATE TABLE D_SEGMENTATION (
    SK_ID_CURR INT PRIMARY KEY,
    SEGMENT_VALUE VARCHAR(30),        -- ex: 'High Value', 'Medium Value', 'Low Value'
    SEGMENT_RISK VARCHAR(30),         -- ex: 'Low Risk', 'Medium Risk', 'High Risk'
    SEGMENT_CLUSTER VARCHAR(50)       -- ex: 'High Value - Low Risk' (Segment cible)
);

-- -------------------------------------------------------------------------
-- 6. Table de Dimension : D_TEMPS (Dimension Temporelle pour Business Intelligence)
-- -------------------------------------------------------------------------
CREATE TABLE D_TEMPS (
    DATE_KEY INT PRIMARY KEY,         -- Format YYYYMMDD (ex: 20251231)
    CALENDAR_DATE DATE UNIQUE NOT NULL,
    YEAR INT NOT NULL,
    MONTH INT NOT NULL,
    MONTH_NAME VARCHAR(15) NOT NULL,
    QUARTER INT NOT NULL,
    WEEK_OF_YEAR INT NOT NULL,
    DAY_OF_WEEK INT NOT NULL,
    DAY_OF_WEEK_NAME VARCHAR(15) NOT NULL
);

-- -------------------------------------------------------------------------
-- 7. Table de Faits Principale : F_APPLICATIONS (Demandes de crédit actuelles)
-- -------------------------------------------------------------------------
CREATE TABLE F_APPLICATIONS (
    SK_ID_CURR INT PRIMARY KEY,
    DECISION_DATE_KEY INT,               -- Clé pointant vers D_TEMPS
    AMT_CREDIT DECIMAL(15, 2),
    AMT_ANNUITY DECIMAL(15, 2),
    AMT_GOODS_PRICE DECIMAL(15, 2),
    NAME_CONTRACT_TYPE VARCHAR(50),
    TARGET INT CHECK (TARGET IN (0, 1)), -- 0 = OK, 1 = Défaut d'impayé
    
    -- Clés Étrangères pointant vers nos Dimensions
    FOREIGN KEY (SK_ID_CURR) REFERENCES D_CLIENT(SK_ID_CURR),
    FOREIGN KEY (SK_ID_CURR) REFERENCES D_PREVIOUS_APPLICATIONS(SK_ID_CURR),
    FOREIGN KEY (SK_ID_CURR) REFERENCES D_EXTERNAL_BUREAU(SK_ID_CURR),
    FOREIGN KEY (SK_ID_CURR) REFERENCES D_PAYMENTS_HISTORY(SK_ID_CURR),
    FOREIGN KEY (SK_ID_CURR) REFERENCES D_SEGMENTATION(SK_ID_CURR),
    FOREIGN KEY (DECISION_DATE_KEY) REFERENCES D_TEMPS(DATE_KEY)
);

