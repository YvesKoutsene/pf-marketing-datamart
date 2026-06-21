import os
import sqlite3
import pandas as pd
import numpy as np

# Configuration des chemins
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_FILE = os.path.join(BASE_DIR, 'data', 'processed', 'datamart.db')

def calculate_segmentation():
    """Calcule la segmentation client (Risque × Valeur) et met à jour D_SEGMENTATION."""
    print("=========================================================================")
    print("LANCEMENT DU MOTEUR DE SEGMENTATION CLIENT (PYTHON)")
    print("=========================================================================\n")
    
    conn = sqlite3.connect(DB_FILE)
    
    # 1. Charger les données requises depuis la base
    print("Extraction des indicateurs clés depuis le Datamart...")
    query = """
        SELECT 
            c.SK_ID_CURR,
            c.AMT_INCOME_TOTAL,
            f.AMT_CREDIT,
            b.MAX_DAYS_OVERDUE_BUREAU,
            b.NB_ACTIVE_LOANS_BUREAU,
            p.AVG_PAYMENT_DELAY,
            p.TOTAL_MISSED_PAYMENTS,
            p.RATIO_PAID_VS_REQUIRED
        FROM D_CLIENT c
        JOIN F_APPLICATIONS f ON c.SK_ID_CURR = f.SK_ID_CURR
        JOIN D_EXTERNAL_BUREAU b ON c.SK_ID_CURR = b.SK_ID_CURR
        JOIN D_PAYMENTS_HISTORY p ON c.SK_ID_CURR = p.SK_ID_CURR
    """
    df = pd.read_sql(query, conn)
    print(f"Extraction terminée : {len(df)} profils chargés.\n")
    
    # 2. Calcul du Score de Valeur (AMT_CREDIT)
    # Nous découpons le montant du crédit en tertiles (Low, Medium, High Value)
    print("Calcul des segments de Valeur...")
    q33 = df['AMT_CREDIT'].quantile(0.33)
    q66 = df['AMT_CREDIT'].quantile(0.66)
    
    def get_value_segment(credit):
        if credit >= q66:
            return 'High Value'
        elif credit >= q33:
            return 'Medium Value'
        else:
            return 'Low Value'
            
    df['SEGMENT_VALUE'] = df['AMT_CREDIT'].apply(get_value_segment)
    
    # 3. Calcul du Score de Risque (Composite comportemental)
    print("Calcul des scores de Risque comportemental...")
    # Nous concevons un score de risque de 0 à 100 basé sur les incidents réels :
    # - Retard externe au Bureau du crédit : max_days_overdue > 0 (30 pts)
    # - Retards internes répétés : avg_payment_delay > 5 (20 pts)
    # - Échéances non payées en totalité : total_missed_payments > 2 (30 pts)
    # - Ratio de remboursement défaillant : ratio < 0.95 (20 pts)
    
    df['RISK_SCORE'] = 0
    df['RISK_SCORE'] += np.where(df['MAX_DAYS_OVERDUE_BUREAU'] > 0, 30, 0)
    df['RISK_SCORE'] += np.where(df['AVG_PAYMENT_DELAY'] > 5, 20, 0)
    df['RISK_SCORE'] += np.where(df['TOTAL_MISSED_PAYMENTS'] > 2, 30, 0)
    df['RISK_SCORE'] += np.where(df['RATIO_PAID_VS_REQUIRED'] < 0.95, 20, 0)
    
    # Classification du risque
    def get_risk_segment(score):
        if score >= 50:
            return 'High Risk'
        elif score >= 20:
            return 'Medium Risk'
        else:
            return 'Low Risk'
            
    df['SEGMENT_RISK'] = df['RISK_SCORE'].apply(get_risk_segment)
    
    # 4. Combinaison des segments pour former les clusters
    print("Génération des clusters bidimensionnels...")
    df['SEGMENT_CLUSTER'] = df['SEGMENT_VALUE'] + " - " + df['SEGMENT_RISK']
    
    # 5. Mise à jour de la table D_SEGMENTATION dans SQLite
    print("Mise à jour de la table D_SEGMENTATION dans la base de données...")
    cursor = conn.cursor()
    
    # Nous insérons les données par blocs pour de meilleures performances
    # En SQLite, on peut faire des requêtes de mise à jour préparées
    data_to_update = df[['SEGMENT_VALUE', 'SEGMENT_RISK', 'SEGMENT_CLUSTER', 'SK_ID_CURR']].values.tolist()
    
    cursor.executemany("""
        UPDATE D_SEGMENTATION
        SET SEGMENT_VALUE = ?,
            SEGMENT_RISK = ?,
            SEGMENT_CLUSTER = ?
        WHERE SK_ID_CURR = ?
    """, data_to_update)
    
    conn.commit()
    conn.close()
    
    print("\nMise à jour effectuée avec succès dans D_SEGMENTATION !")
    
    # 6. Afficher les statistiques de la segmentation pour validation
    print("\n--- STATISTIQUES DE DISTRIBUTION DES SEGMENTS ---")
    dist_cluster = df['SEGMENT_CLUSTER'].value_counts()
    dist_pct = df['SEGMENT_CLUSTER'].value_counts(normalize=True) * 100
    
    for cluster in dist_cluster.index:
        print(f"Cluster '{cluster}' : {dist_cluster[cluster]:,} clients ({dist_pct[cluster]:.2f}%)")
        
    print("\n=========================================================================")
    print("FIN DU TRAITEMENT DE LA SEGMENTATION CLIENT")
    print("=========================================================================\n")

if __name__ == '__main__':
    calculate_segmentation()
