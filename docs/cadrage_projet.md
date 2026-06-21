# Étape 0 : Cadrage Stratégique & Métier du Projet

Ce document sert de charte de cadrage pour le projet **Datamart Marketing Multi-Pays**. Il définit la vision business, le périmètre analytique, et formule les questions clés auxquelles le projet répondra afin de guider nos développements techniques ultérieurs.

---

## 1. Contexte & Enjeux Business (Le "Why")

Au sein de **BNP Paribas Personal Finance** (BNP PF), leader européen du crédit à la consommation, le **Centre d'expertise Analytics & BI** pilote l'activité commerciale et le risque d'un portefeuille international. 

L'un des défis majeurs de ce centre d'expertise est de centraliser, fiabiliser et analyser des données provenant de multiples pays, canaux de distribution, et partenaires commerciaux afin de prendre des décisions d'octroi et de marketing éclairées.

En exploitant un jeu de données réel et anonymisé de crédit à la consommation (**Home Credit Default Risk**), ce projet simule cette activité de pilotage à travers un cas d'usage concret : **l'optimisation du portefeuille et la fiabilisation des données d'octroi.**

---

## 2. Périmètre Analytique (Les Données)

Le projet s'appuie sur un croisement de 4 sources de données transactionnelles (Home Credit) et de données sectorielles externes (BCE/Eurostat) :

1.  **Le Profil Client Actuel (`application_train.csv`)** : Caractéristiques socio-démographiques, revenus, situation financière, et comportement de remboursement (variable cible `TARGET` : 1 = défaut de paiement, 0 = remboursement à temps).
2.  **L'Historique Commercial Interne (`previous_application.csv`)** : Historique des demandes passées chez Home Credit (statut d'acceptation, type de produit demandé, canal de distribution).
3.  **L'Historique des Paiements Réels (`installments_payments.csv`)** : Calendrier des règlements d'échéances passés (montant exigé vs montant payé, date prévue vs date de paiement réelle).
4.  **L'Historique de Risque Externe (`bureau.csv`)** : Crédits souscrits par nos clients auprès d'autres institutions financières (déclarés au Bureau du Crédit).
5.  **Données Macro-Économiques Externes (Données de Marché)** : Données agrégées sur l'encours du crédit conso et les taux d'usure en Europe (France, Italie, Espagne, Belgique) pour apporter la vision "Multi-Pays" et replacer nos analyses clients dans leur contexte de marché.

---

## 3. Les Problématiques Business (Les Questions Clés)

Pour que notre démarche technique apporte une réelle valeur ajoutée, nous structurons notre analyse autour de **4 grandes questions stratégiques** :

### Question 1 : Gouvernance & Qualité (La donnée est-elle fiable ?)
*   *Sous-questions :* Quels sont les taux de complétude de nos données d'octroi ? Existe-t-il des anomalies systémiques de saisie (ex. : valeurs par défaut aberrantes) ? Y a-t-il des ruptures de cohérence temporelle entre l'ancienneté d'un contrat et l'âge du client ?
*   *Livrable SQL/Python :* Un **Data Quality Scorecard** mesurant les indicateurs d'intégrité de nos tables sources.

### Question 2 : Performance Commerciale & Octroi (Comment performe notre réseau ?)
*   *Sous-questions :* Quel est le taux d'acceptation global de nos dossiers de crédit ? Comment ce taux varie-t-il selon les canaux d'acquisition (Internet, Points de Vente, Agences) et selon le type de produit (Crédit Auto, Prêt Personnel) ?
*   *Livrable SQL :* Calcul des **KPIs d'octroi** (Taux d'acceptation, Taux d'annulation, Volume d'encours financé).

### Question 3 : Profilage du Risque de Crédit (Quels signaux prédisent le défaut ?)
*   *Sous-questions :* Les retards de paiement passés (internes ou externes) sont-ils des indicateurs fiables du risque de défaut futur ? Comment le taux de défaut actuel est-il corrélé au ratio d'endettement des clients ?
*   *Livrable SQL/Python :* Analyse croisée du comportement historique (retards de paiement) et du taux d'impayés actuel.

### Question 4 : Segmentation Marketing (Comment cibler efficacement nos clients ?)
*   *Sous-questions :* Comment cartographier notre base clients selon un prisme "Risque de défaut" vs "Valeur d'emprunt" ? Quels sont les segments de clients à forte valeur et faible risque sur lesquels le marketing de BNP PF doit faire de la multi-détention ?
*   *Livrable Python :* Une **Segmentation Client de Scoring** en deux dimensions, intégrée comme dimension dans le Datamart.

---

## 4. Indicateurs Clés de Performance (KPIs) Cibles

Nous concevrons des requêtes SQL et des calculs DAX (Power BI) pour mesurer précisément :
*   **Approval Rate (Taux d'acceptation)** : $Nombre\ de\ contrats\ approuvés / Nombre\ total\ de\ demandes$
*   **Default Rate (Taux de défaut)** : $Nombre\ de\ clients\ en\ défaut\ (TARGET=1) / Nombre\ total\ de\ clients$
*   **Average Credit Amount (Montant moyen financé)** : Moyenne du montant du crédit accordé par client.
*   **Repayment Delay Index (Indice de retard de paiement)** : Écart moyen en jours entre la date d'échéance prévue et la date de paiement réelle.
*   **Data Completeness Score (Score de complétude)** : % de valeurs non nulles sur les variables clés d'octroi.
