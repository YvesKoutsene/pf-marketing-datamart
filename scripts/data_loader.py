import os
import sqlite3
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW_DIR = os.path.join(BASE_DIR, 'data', 'raw')
DATA_PROCESSED_DIR = os.path.join(BASE_DIR, 'data', 'processed')
SQL_SCHEMA_FILE = os.path.join(BASE_DIR, 'sql', 'schema_datamart.sql')
DB_FILE = os.path.join(DATA_PROCESSED_DIR, 'datamart.db')

def init_database():
    """Initialise la base de données SQLite en appliquant le schéma DDL."""
    print("--- ÉTAPE 1 : Initialisation de la base de données SQLite ---")
    if not os.path.exists(DATA_PROCESSED_DIR):
        os.makedirs(DATA_PROCESSED_DIR)
        
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    with open(SQL_SCHEMA_FILE, 'r', encoding='utf-8') as f:
        sql_script = f.read()
        
    # SQLite ne supporte pas les scripts multiples en execute() standard, on utilise executescript()
    cursor.executescript(sql_script)
    conn.commit()
    conn.close()
    print(f"Base de données initialisée avec succès à l'emplacement : {DB_FILE}\n")

def load_dimension_temps(conn):
    """Génère et peuple la dimension D_TEMPS avec un ancrage historique réel."""
    print("--- ÉTAPE 2.1 : Génération de la dimension temporelle D_TEMPS ---")
    # Date d'ancrage (Day 0) = 31 Décembre 2025
    anchor_date = datetime(2025, 12, 31)
    
    # On génère 12 ans de dates (de 2015 à 2026 inclus)
    start_date = datetime(2015, 1, 1)
    end_date = datetime(2026, 12, 31)
    
    dates = []
    current_date = start_date
    while current_date <= end_date:
        date_key = int(current_date.strftime("%Y%m%d"))
        dates.append({
            'DATE_KEY': date_key,
            'CALENDAR_DATE': current_date.strftime("%Y-%m-%d"),
            'YEAR': current_date.year,
            'MONTH': current_date.month,
            'MONTH_NAME': current_date.strftime("%B"),
            'QUARTER': (current_date.month - 1) // 3 + 1,
            'WEEK_OF_YEAR': current_date.isocalendar()[1],
            'DAY_OF_WEEK': current_date.isoweekday(),
            'DAY_OF_WEEK_NAME': current_date.strftime("%A")
        })
        current_date += timedelta(days=1)
        
    df_temps = pd.DataFrame(dates)
    df_temps.to_sql('D_TEMPS', conn, if_exists='append', index=False)
    print(f"Dimension D_TEMPS peuplée avec {len(df_temps)} jours (Ancrage Day 0 = {anchor_date.strftime('%Y-%m-%d')}).\n")
    return anchor_date

def load_dimension_client(conn, app_train):
    """Nettoie et charge la table D_CLIENT."""
    print("--- ÉTAPE 2.2 : Chargement de D_CLIENT ---")
    
    # Copie locale pour éviter les PerformanceWarning de fragmentation DataFrame
    d_client = app_train[[
        'SK_ID_CURR', 'CODE_GENDER', 'CNT_CHILDREN', 'AMT_INCOME_TOTAL',
        'NAME_INCOME_TYPE', 'NAME_EDUCATION_TYPE', 'NAME_FAMILY_STATUS',
        'NAME_HOUSING_TYPE', 'DAYS_BIRTH', 'DAYS_EMPLOYED'
    ]].copy()
    
    # Calcul de l'âge et de l'ancienneté professionnelle
    d_client['AGE_YEARS'] = np.floor(-d_client['DAYS_BIRTH'] / 365.25).astype(int)
    
    # DAYS_EMPLOYED > 0 (ex: 365243) est une anomalie (retraités/sans emploi) -> NULL
    d_client['EMPLOYMENT_YEARS'] = np.where(
        d_client['DAYS_EMPLOYED'] <= 0,
        np.floor(-d_client['DAYS_EMPLOYED'] / 365.25),
        np.nan
    )
    
    # Suppression des colonnes intermédiaires
    d_client = d_client.drop(columns=['DAYS_BIRTH', 'DAYS_EMPLOYED'])
    d_client['CODE_GENDER'] = d_client['CODE_GENDER'].fillna('XNA')
    
    d_client.to_sql('D_CLIENT', conn, if_exists='append', index=False)
    print(f"Dimension D_CLIENT chargée avec {len(d_client)} profils clients.\n")

def load_dimension_previous(conn):
    """Agrège previous_application.csv et charge D_PREVIOUS_APPLICATIONS."""
    print("--- ÉTAPE 2.3 : Chargement de D_PREVIOUS_APPLICATIONS (Agrégation historique interne) ---")
    file_path = os.path.join(DATA_RAW_DIR, 'previous_application.csv')
    
    # Lecture optimisée : on ne charge que les colonnes nécessaires
    usecols = ['SK_ID_CURR', 'SK_ID_PREV', 'NAME_CONTRACT_STATUS', 'AMT_CREDIT', 'DAYS_DECISION']
    prev_df = pd.read_csv(file_path, usecols=usecols)
    
    # 1. Nombre d'applications passées
    agg_counts = prev_df.groupby('SK_ID_CURR')['SK_ID_PREV'].count().rename('NB_PREV_APPLICATIONS')
    
    # 2. Taux d'acceptation
    approved_mask = prev_df['NAME_CONTRACT_STATUS'] == 'Approved'
    agg_approved = prev_df[approved_mask].groupby('SK_ID_CURR')['SK_ID_PREV'].count()
    approval_rate = (agg_approved / agg_counts).fillna(0.0).rename('APPROVAL_RATE_PREV')
    
    # 3. Montant total emprunté
    agg_credit = prev_df.groupby('SK_ID_CURR')['AMT_CREDIT'].sum().fillna(0.0).rename('TOTAL_PREV_CREDIT')
    
    # 4. Statut de la dernière décision (DAYS_DECISION le plus proche de 0)
    prev_sorted = prev_df.sort_values(by=['SK_ID_CURR', 'DAYS_DECISION'], ascending=[True, False])
    last_status = prev_sorted.groupby('SK_ID_CURR')['NAME_CONTRACT_STATUS'].first().rename('LAST_DECISION_STATUS')
    
    # Assemblage
    d_prev = pd.concat([agg_counts, approval_rate, agg_credit, last_status], axis=1).reset_index()
    
    d_prev.to_sql('D_PREVIOUS_APPLICATIONS', conn, if_exists='append', index=False)
    print(f"Dimension D_PREVIOUS_APPLICATIONS chargée avec {len(d_prev)} lignes d'historique interne.\n")
    return d_prev['SK_ID_CURR'].unique()

def load_dimension_bureau(conn):
    """Agrège bureau.csv et charge D_EXTERNAL_BUREAU."""
    print("--- ÉTAPE 2.4 : Chargement de D_EXTERNAL_BUREAU (Agrégation risque externe) ---")
    file_path = os.path.join(DATA_RAW_DIR, 'bureau.csv')
    
    usecols = ['SK_ID_CURR', 'CREDIT_ACTIVE', 'AMT_CREDIT_SUM_DEBT', 'CREDIT_DAY_OVERDUE']
    bureau_df = pd.read_csv(file_path, usecols=usecols)
    
    # 1. Nombre de crédits actifs chez les concurrents
    active_mask = bureau_df['CREDIT_ACTIVE'] == 'Active'
    agg_active = bureau_df[active_mask].groupby('SK_ID_CURR')['CREDIT_ACTIVE'].count().rename('NB_ACTIVE_LOANS_BUREAU')
    
    # 2. Encours de dette totale à l'externe (AMT_CREDIT_SUM_DEBT)
    agg_debt = bureau_df.groupby('SK_ID_CURR')['AMT_CREDIT_SUM_DEBT'].sum().fillna(0.0).rename('TOTAL_DEBT_BUREAU')
    
    # 3. Retard maximum enregistré
    agg_overdue = bureau_df.groupby('SK_ID_CURR')['CREDIT_DAY_OVERDUE'].max().fillna(0).rename('MAX_DAYS_OVERDUE_BUREAU')
    
    # Assemblage
    d_bureau = pd.DataFrame(index=bureau_df['SK_ID_CURR'].unique())
    d_bureau = d_bureau.join(agg_active).fillna(0)
    d_bureau = d_bureau.join(agg_debt)
    d_bureau = d_bureau.join(agg_overdue)
    d_bureau = d_bureau.reset_index().rename(columns={'index': 'SK_ID_CURR'})
    
    d_bureau['NB_ACTIVE_LOANS_BUREAU'] = d_bureau['NB_ACTIVE_LOANS_BUREAU'].astype(int)
    d_bureau['MAX_DAYS_OVERDUE_BUREAU'] = d_bureau['MAX_DAYS_OVERDUE_BUREAU'].astype(int)
    
    d_bureau.to_sql('D_EXTERNAL_BUREAU', conn, if_exists='append', index=False)
    print(f"Dimension D_EXTERNAL_BUREAU chargée avec {len(d_bureau)} lignes de risque externe.\n")
    return d_bureau['SK_ID_CURR'].unique()

def load_dimension_payments(conn):
    """Agrège installments_payments.csv et charge D_PAYMENTS_HISTORY."""
    print("--- ÉTAPE 2.5 : Chargement de D_PAYMENTS_HISTORY (Comportement de remboursement) ---")
    file_path = os.path.join(DATA_RAW_DIR, 'installments_payments.csv')
    
    # Lecture séquentielle par morceaux pour optimiser l'empreinte mémoire
    chunksize = 1_000_000
    usecols = ['SK_ID_CURR', 'DAYS_INSTALMENT', 'DAYS_ENTRY_PAYMENT', 'AMT_INSTALMENT', 'AMT_PAYMENT']
    
    stats = {}
    
    print("Lecture séquentielle de installments_payments.csv...")
    for chunk in pd.read_csv(file_path, usecols=usecols, chunksize=chunksize):
        # Calcul du retard : max(0, date_paiement - date_échéance)
        delay = (chunk['DAYS_ENTRY_PAYMENT'] - chunk['DAYS_INSTALMENT']).fillna(0)
        chunk['PAYMENT_DELAY'] = np.where(delay > 0, delay, 0)
        
        # Incident : paiement manqué ou partiel
        chunk['MISSED_PAYMENT'] = np.where(
            chunk['AMT_PAYMENT'].fillna(0.0) < chunk['AMT_INSTALMENT'].fillna(0.0),
            1, 0
        )
        
        # Ratio payé / requis
        ratio = chunk['AMT_PAYMENT'].fillna(0.0) / np.where(chunk['AMT_INSTALMENT'] > 0, chunk['AMT_INSTALMENT'], 1.0)
        chunk['PAID_VS_REQUIRED'] = ratio
        
        for name, group in chunk.groupby('SK_ID_CURR'):
            if name not in stats:
                stats[name] = {
                    'delay_sum': 0.0,
                    'delay_count': 0,
                    'missed_sum': 0,
                    'ratio_sum': 0.0,
                    'ratio_count': 0
                }
            stats[name]['delay_sum'] += group['PAYMENT_DELAY'].sum()
            stats[name]['delay_count'] += group['PAYMENT_DELAY'].count()
            stats[name]['missed_sum'] += group['MISSED_PAYMENT'].sum()
            stats[name]['ratio_sum'] += group['PAID_VS_REQUIRED'].sum()
            stats[name]['ratio_count'] += group['PAID_VS_REQUIRED'].count()
            
    # Finalisation des agrégations
    aggregated = []
    for sk_id, s in stats.items():
        avg_delay = s['delay_sum'] / s['delay_count'] if s['delay_count'] > 0 else 0.0
        avg_ratio = s['ratio_sum'] / s['ratio_count'] if s['ratio_count'] > 0 else 0.0
        aggregated.append({
            'SK_ID_CURR': sk_id,
            'AVG_PAYMENT_DELAY': round(avg_delay, 2),
            'TOTAL_MISSED_PAYMENTS': s['missed_sum'],
            'RATIO_PAID_VS_REQUIRED': round(avg_ratio, 4)
        })
        
    d_payments = pd.DataFrame(aggregated)
    d_payments.to_sql('D_PAYMENTS_HISTORY', conn, if_exists='append', index=False)
    print(f"Dimension D_PAYMENTS_HISTORY chargée avec {len(d_payments)} profils de paiement.\n")
    return d_payments['SK_ID_CURR'].unique()

def load_dimension_segmentation(conn, all_client_ids):
    """Initialise D_SEGMENTATION avec des NULLs. Les segments réels seront calculés à l'étape 4."""
    print("--- ÉTAPE 2.6 : Initialisation de D_SEGMENTATION ---")
    d_seg = pd.DataFrame({'SK_ID_CURR': all_client_ids})
    d_seg['SEGMENT_VALUE'] = None
    d_seg['SEGMENT_RISK'] = None
    d_seg['SEGMENT_CLUSTER'] = None
    
    d_seg.to_sql('D_SEGMENTATION', conn, if_exists='append', index=False)
    print(f"Dimension D_SEGMENTATION initialisée avec {len(d_seg)} identifiants clients.\n")

def load_fact_applications(conn, app_train, anchor_date):
    """Nettoie et charge la table de faits F_APPLICATIONS."""
    print("--- ÉTAPE 2.7 : Chargement de la table de faits F_APPLICATIONS ---")
    
    # Copie locale pour éviter les warnings
    f_apps = app_train[[
        'SK_ID_CURR', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
        'NAME_CONTRACT_TYPE', 'TARGET'
    ]].copy()
    
    # Générer une date de décision pour chaque client répartie sur les 3 derniers mois de 2025.
    np.random.seed(42)
    random_days = np.random.randint(0, 91, size=len(f_apps))
    
    dates_decision = [anchor_date - timedelta(days=int(d)) for d in random_days]
    f_apps['DECISION_DATE_KEY'] = [int(d.strftime("%Y%m%d")) for d in dates_decision]
    
    # Nettoyage
    f_apps['AMT_ANNUITY'] = f_apps['AMT_ANNUITY'].fillna(0.0)
    f_apps['AMT_GOODS_PRICE'] = f_apps['AMT_GOODS_PRICE'].fillna(f_apps['AMT_CREDIT'])
    
    # Réarrangement des colonnes conforme au schéma
    f_apps = f_apps[[
        'SK_ID_CURR', 'DECISION_DATE_KEY', 'AMT_CREDIT', 'AMT_ANNUITY', 'AMT_GOODS_PRICE',
        'NAME_CONTRACT_TYPE', 'TARGET'
    ]]
    
    f_apps.to_sql('F_APPLICATIONS', conn, if_exists='append', index=False)
    print(f"Table de faits F_APPLICATIONS chargée avec {len(f_apps)} demandes de crédit.\n")

def main():
    start_time = datetime.now()
    print("=========================================================================")
    print("LANCEMENT DE L'INGESTION & CONSTITUTION DU DATAMART")
    print("=========================================================================\n")
    
    # Initialisation de la BDD
    init_database()
    
    # Connexion SQLite
    conn = sqlite3.connect(DB_FILE)
    
    try:
        # Chargement en mémoire
        print("Chargement en mémoire de application_train.csv...")
        app_train_path = os.path.join(DATA_RAW_DIR, 'application_train.csv')
        app_train = pd.read_csv(app_train_path)
        print(f"application_train.csv chargé ({len(app_train)} lignes).\n")
        
        all_client_ids = app_train['SK_ID_CURR'].unique()
        
        # 1. Alimenter D_TEMPS (Dimension indépendante)
        anchor_date = load_dimension_temps(conn)
        
        # 2. Alimenter D_CLIENT
        load_dimension_client(conn, app_train)
        
        # 3. Alimenter les dimensions agrégées (Internal/External histories)
        prev_ids = load_dimension_previous(conn)
        bureau_ids = load_dimension_bureau(conn)
        pay_ids = load_dimension_payments(conn)
        
        # 4. Assurer l'intégrité relationnelle
        print("--- ÉTAPE 2.6.Bis : Alignement d'intégrité référentielle des dimensions ---")
        
        missing_prev = list(set(all_client_ids) - set(prev_ids))
        if missing_prev:
            df_missing_prev = pd.DataFrame({
                'SK_ID_CURR': missing_prev,
                'NB_PREV_APPLICATIONS': 0,
                'APPROVAL_RATE_PREV': 0.0,
                'TOTAL_PREV_CREDIT': 0.0,
                'LAST_DECISION_STATUS': 'No history'
            })
            df_missing_prev.to_sql('D_PREVIOUS_APPLICATIONS', conn, if_exists='append', index=False)
            print(f"Intégrité D_PREVIOUS_APPLICATIONS : Ajout de {len(missing_prev)} clients sans historique.")
            
        missing_bureau = list(set(all_client_ids) - set(bureau_ids))
        if missing_bureau:
            df_missing_bureau = pd.DataFrame({
                'SK_ID_CURR': missing_bureau,
                'NB_ACTIVE_LOANS_BUREAU': 0,
                'TOTAL_DEBT_BUREAU': 0.0,
                'MAX_DAYS_OVERDUE_BUREAU': 0
            })
            df_missing_bureau.to_sql('D_EXTERNAL_BUREAU', conn, if_exists='append', index=False)
            print(f"Intégrité D_EXTERNAL_BUREAU : Ajout de {len(missing_bureau)} clients sans historique.")
            
        missing_pay = list(set(all_client_ids) - set(pay_ids))
        if missing_pay:
            df_missing_pay = pd.DataFrame({
                'SK_ID_CURR': missing_pay,
                'AVG_PAYMENT_DELAY': 0.0,
                'TOTAL_MISSED_PAYMENTS': 0,
                'RATIO_PAID_VS_REQUIRED': 1.0
            })
            df_missing_pay.to_sql('D_PAYMENTS_HISTORY', conn, if_exists='append', index=False)
            print(f"Intégrité D_PAYMENTS_HISTORY : Ajout de {len(missing_pay)} clients sans historique.")
            
        # 5. D_SEGMENTATION
        load_dimension_segmentation(conn, all_client_ids)
        
        # 6. F_APPLICATIONS
        load_fact_applications(conn, app_train, anchor_date)
        
        print("\n=========================================================================")
        print("PIPELINE D'INGESTION REUSSI AVEC SUCCES !")
        print(f"Temps total d'exécution : {datetime.now() - start_time}")
        print("=========================================================================")
        
    except Exception as e:
        print(f"\n[ERROR] ERREUR LORS DE L'INGESTION : {str(e)}")
        raise e
    finally:
        conn.close()

if __name__ == '__main__':
    main()
