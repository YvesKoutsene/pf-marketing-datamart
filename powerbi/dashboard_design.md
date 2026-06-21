# Cahier des Charges & Design du Dashboard Power BI 🎨

Ce document détaille la charte graphique, le modèle de relations, la configuration technique de la connexion et l'agencement visuel page par page du dashboard **`datamart_dashboard.pbix`** à l'attention de Joséphine et Grégory.

---

## 1. Guide de Configuration Technique (Connexion SQLite)

Pour connecter Power BI Desktop à notre base de données locale `datamart.db` :

1.  **Installer le pilote SQLite ODBC** :
    *   Télécharger et installer le pilote ODBC SQLite pour Windows (ex: *SQLite ODBC Driver* de Christian Werner).
2.  **Configurer la source de données (DSN)** :
    *   Ouvrir l'outil *Administrateur de sources de données ODBC (64 bits)* de Windows.
    *   Ajouter un DSN utilisateur nommé `SQLite_BNP_PF` pointant vers ton fichier de base de données : `C:\Users\jeany\OneDrive\Bureau\Jean-Yves\Projet\BNP\DBA\bnp-pf-marketing-datamart\data\processed\datamart.db`.
3.  **Importer dans Power BI** :
    *   Dans Power BI Desktop, cliquer sur **Obtenir des données** > **ODBC**.
    *   Sélectionner `SQLite_BNP_PF` et importer l'ensemble des 7 tables.

---

## 2. Modélisation des Relations (Vue Modèle)

Dans l'onglet **Modèle** de Power BI, configurer les relations en respectant le modèle en étoile (Star Schema). Toutes les relations doivent être de type **1 à Plusieurs (1:*)** et le sens du filtrage doit être unique (**Unique**), de la dimension vers la table de faits.

```text
┌───────────────────────────────────────────────────────────────────────────┐
│                                DIMENSIONS                                 │
└───────────────────────────────────────────────────────────────────────────┘
   D_CLIENT                 [1] ───► [*] (SK_ID_CURR)
   D_PREVIOUS_APPLICATIONS  [1] ───► [*] (SK_ID_CURR)
   D_EXTERNAL_BUREAU        [1] ───► [*] (SK_ID_CURR)   F_APPLICATIONS
   D_PAYMENTS_HISTORY       [1] ───► [*] (SK_ID_CURR)    (Table de faits)
   D_SEGMENTATION           [1] ───► [*] (SK_ID_CURR)
   D_TEMPS                  [1] ───► [*] (DECISION_DATE_KEY -> DATE_KEY)
```

---

## 3. Charte Graphique & Identité Visuelle (Premium BNP PF)

*   **Couleurs Thématiques :**
    *   **Vert BNP PF (Primaire) :** `#00965E` (Symbole de croissance et d'accompagnement).
    *   **Vert Foncé (Texte & Titres) :** `#0A3B22`
    *   **Gris Ardoise (Secondaire) :** `#4A5568`
    *   **Rouge Alerte (Défaut / Risque) :** `#E53E3E`
    *   **Fond de page :** Blanc cassé ou Gris très clair (`#F7FAFC`) pour faire ressortir les cartes.
*   **Typographie :** *Segoe UI* ou *Outfit* pour une lisibilité moderne et corporate.

---

## 4. Agencement Visuel des Pages (Mise en Page)

Le dashboard est structuré en **3 pages complémentaires** pour répondre aux questions clés définies dans le cadrage.

### Page 1 : Pilotage du Portefeuille & Performance (Vue Executive)
*   **Objectif :** Suivre la dynamique commerciale d'octroi et mesurer le risque global de défaut.
*   **Éléments Visuels :**
    *   **Bandeau supérieur (KPI Cards) :**
        *   Card 1 : `[Total Clients]` (ex: *307,51k*)
        *   Card 2 : `[Volume Crédit Total]` (ex: *184,28 Md€*)
        *   Card 3 : `[Taux de Défaut]` (ex: *8,08%* - avec mise en forme conditionnelle : rouge si > 8%).
        *   Card 4 : `[Retard Moyen Paiement]` (ex: *1,1 jour*).
    *   **Graphique Principal (Courbe et Histogramme cumulés) :**
        *   *Axe X :* `D_TEMPS[MONTH_NAME]` (Octobre, Novembre, Décembre 2025).
        *   *Colonnes :* `[Volume Crédit Total]` (Volume d'octroi par mois).
        *   *Ligne (Axe secondaire) :* `[Taux de Défaut]` (% de clients en incident par mois).
    *   **Graphique 2 (Donut Chart) :** Répartition des encours par type de contrat (`F_APPLICATIONS[NAME_CONTRACT_TYPE]`).
    *   **Filtres de page (Slicers) :** Genre, Niveau d'études, Type de revenus.

---

### Page 2 : Segmentation Client & Stratégie Marketing (Ciblage)
*   **Objectif :** Identifier les gisements de croissance et surveiller les populations à risque.
*   **Éléments Visuels :**
    *   **Graphique Central (Matrice Risque x Valeur) :**
        *   *Lignes (Y) :* `D_SEGMENTATION[SEGMENT_RISK]` (Low, Medium, High).
        *   *Colonnes (X) :* `D_SEGMENTATION[SEGMENT_VALUE]` (Low, Medium, High).
        *   *Valeur :* `[Total Clients]` et `[Taux de Défaut]` avec échelle de couleurs (du vert pour le faible risque au rouge pour le fort risque).
    *   **Visual 2 (Scatter Plot - Nuage de points) :**
        *   *Axe X :* `[Dette Externe Moyenne]` (Encours concurrents).
        *   *Axe Y :* `[Taux de Défaut]` (Risque réel).
        *   *Détail (Points) :* Les 9 clusters de `D_SEGMENTATION[SEGMENT_CLUSTER]`.
        *   *Taille du point :* `[Total Clients]`.
        *   *Lecture directe :* Visualise instantanément que le cluster `High Value - Low Risk` se trouve en bas à droite (forte valeur, faible risque).
    *   **Visual 3 (Treemap) :** Part de chaque segment dans le portefeuille (`[Part Volume Segment %]`).

---

### Page 3 : Gouvernance de la Donnée & Qualité (Scorecard)
*   **Objectif :** Piloter la fiabilité des données et identifier les chantiers de redressement (Data Office).
*   **Éléments Visuels :**
    *   **Visual 1 (Gauge - Jauge semi-circulaire) :** Index de qualité global.
        *   *Valeur :* Moyenne des taux de complétude et validité.
        *   *Cible :* 100%.
    *   **Visual 2 (Tableau détaillé de Complétude) :**
        *   *Colonnes :* Table, Colonne, Taux de complétude.
        *   *Mise en forme conditionnelle :* Icônes de feux tricolores (Vert si 100%, Orange si 95%-99%, Rouge si < 95%).
    *   **Visual 3 (Bar Chart horizontal) :** Répartition des anomalies par type (ex : Nb d'anciennetés pro supérieures à l'âge).
