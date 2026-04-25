# Interactions Espace partenaire Rikees Sol

> **Périmètre** : ce document cartographie les univers accessibles et les interactions fonctionnelles réalisables par un courtier depuis l'Espace partenaire Rikees Sol. Les outils hors portail (TopScan, SaaS Rikees Tech standalone, etc.) sont hors scope.
>
> **Statut** : référence d'exemple basée sur les sources disponibles ; non contractuelle.

---

## 1. Univers accessibles depuis le portail

Depuis l'Espace partenaire Rikees Sol, le courtier accède à **7 univers produits** :

| Univers | Actions disponibles |
|---|---|
| Santé (individuelle & collective) | Tarification, devis, souscription, suivi des dossiers |
| Obsèques | Tarification, devis, souscription |
| GAV | Tarification, devis, souscription |
| Dommages | Tarification, devis, souscription |
| Emprunteur | Tarification, comparaison multi-offres, devis, souscription, suivi, pilotage |
| Prévoyance professionnelle | Tarification, comparaison, devis, souscription, suivi |
| Santé internationale | Tarification, devis, souscription |

---

## 2. Parcours de tarification et de devis

### 2.1 Vue d'ensemble

Le portail propose un parcours de tarification guidé pour chaque univers, permettant au courtier d'obtenir un tarif immédiat et de générer un devis conforme aux exigences réglementaires.

### 2.2 Étapes du parcours

```
1. Sélection de l'univers produit
       ↓
2. Saisie du profil client
       ↓
3. Obtention du tarif (moteur de tarification en ligne)
       ↓
4. Comparaison multi-offres (si disponible sur l'univers)
       ↓
5. Sélection de l'offre retenue
       ↓
6. Export / téléchargement du devis
```

### 2.3 Détail des étapes

#### Étape 2 — Saisie du profil client

Selon l'univers, le portail demande les informations suivantes :

| Univers | Données collectées |
|---|---|
| Emprunteur | Type de prêt, montant, durée, profil médical, profession, quotités co-emprunteurs |
| Santé | Âge, situation familiale (conjoint, enfants), régime social (salarié, TNS), profil médical si nécessaire |
| Prévoyance pro | Statut (TNS, salarié, dirigeant), revenus, activité, niveau de garanties souhaité |
| Dommages | Type de véhicule ou de bien, usage, antécédents sinistres |
| Obsèques / GAV | Âge, situation familiale |
| Santé internationale | Pays de destination, durée du séjour, nombre de personnes couvertes |

#### Étape 3 — Obtention du tarif

- Le moteur de tarification calcule le tarif en temps réel à partir du profil client.
- Pour l'emprunteur, le parcours jRensure génère une **comparaison multi-offres** de la gamme Rikees Sol.

#### Étape 5 — Sélection de l'offre

- Le courtier peut comparer les offres disponibles (garanties, tarifs, gammes économique / protectrice).
- La sélection déclenche la génération du document de devis.

#### Étape 6 — Export du devis

- Le portail génère un **document de devis téléchargeable**, conforme aux exigences DDA.
- Le devis peut être transmis au client directement depuis le portail ou exporté au format PDF.

---

## 3. Parcours de souscription

### 3.1 Vue d'ensemble

Depuis le devis validé, le courtier initie la souscription depuis le portail. Le parcours est entièrement digitalisé.

### 3.2 Étapes du parcours

```
1. Démarrage depuis un devis validé
       ↓
2. Saisie / vérification des données client (KYC, questionnaire de risque)
       ↓
3. Chargement des pièces justificatives
       ↓
4. Signature électronique (client ou courtier selon cas)
       ↓
5. Transmission du dossier à l'assureur / grossiste
       ↓
6. Retour du statut de souscription
       ↓
7. Récupération des documents contractuels
```

### 3.3 Détail des étapes

#### Étape 2 — Données client (KYC et questionnaire de risque)

- **KYC** : identité, coordonnées, coordonnées bancaires (SEPA si prélèvement).
- **Questionnaire de risque** : questionnaire médical (emprunteur, prévoyance), déclaration de profession, état de santé.
- Les données sont pré-remplies depuis la tarification ; le courtier complète les éléments manquants.

#### Étape 3 — Pièces justificatives

- Pièce d'identité du client.
- Offre de prêt (assurance emprunteur).
- Justificatifs médicaux le cas échéant.
- Les documents sont téléversés directement depuis le portail.

#### Étape 4 — Signature électronique

- Le portail intègre un mécanisme de **signature électronique** dans le parcours digital.
- Selon l'offre, la signature peut être réalisée :
  - Par le courtier (mandat de gestion),
  - Par le client final (signature à distance, lien envoyé par email ou SMS).

#### Étape 6 — Statuts de souscription

| Statut | Description |
|---|---|
| **Brouillon** | Dossier en cours de saisie, non encore soumis |
| **Soumis** | Dossier transmis à l'assureur / grossiste, en attente de traitement |
| **Accepté** | Souscription validée par l'assureur ; contrat émis |
| **Refusé** | Souscription rejetée (profil non éligible, pièce manquante, risque refusé) |
| **En attente de pièces** | Dossier incomplet ; pièces complémentaires requises avant traitement |

Les statuts sont synchronisés en temps réel entre le portail et les SI de l'assureur / grossiste.

#### Étape 7 — Documents contractuels

Après acceptation, le courtier peut télécharger depuis le portail :

- **Numéro de police** (identifiant unique du contrat)
- **Attestation d'assurance**
- **Conditions particulières**
- **Tableau des garanties**

---

## 4. Suivi des dossiers et gestion du portefeuille

### 4.1 Consultation des dossiers en cours

Depuis la section « Suivi » du portail, le courtier visualise l'ensemble de ses dossiers avec leur statut en temps réel :

| Vue | Données disponibles |
|---|---|
| Liste des dossiers | Référence, client, univers produit, statut, date de dernière mise à jour |
| Filtres disponibles | Par univers, par statut (en cours, en attente, émis, refusé), par période |
| Détail dossier | Historique des actions, documents téléchargeables, statut d'avancement |

### 4.2 Vue portefeuille

Depuis la section « Portefeuille », le courtier accède à la vue globale de ses contrats actifs :

| Vue | Données disponibles |
|---|---|
| Contrats actifs | Numéro de police, assuré, univers produit, prime, date d'échéance |
| Contrats résiliés | Historique accessible et filtrable |
| Filtres | Par univers produit, par période, par statut (actif, résilié, suspendu) |
| Échéances à venir | Alertes sur les renouvellements et fins de contrats proches |

### 4.3 Tableaux de bord d'activité

Le portail met à disposition des **tableaux de bord de pilotage** :

| Indicateur | Description |
|---|---|
| **Production par univers** | Nombre de devis générés, taux de transformation, contrats émis sur la période |
| **Dossiers en cours** | Volume de dossiers par statut (soumis, en attente, refusés) |
| **Commissions et quittancement** | Accès aux bordereaux de commissions et informations de quittancement disponibles sur le portail |
| **Performances commerciales** | Suivi de l'activité du courtier par période et par ligne de produit |

---

## 5. Synthèse des actions disponibles par univers

| Univers | Tarification | Comparaison multi-offres | Devis DDA | Souscription en ligne | Signature électronique | Suivi dossier | Vue portefeuille | Tableau de bord |
|---|---|---|---|---|---|---|---|---|
| Emprunteur | ✓ | ✓ (jRensure) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Santé individuelle | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Santé collective | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Prévoyance pro | ✓ | ✓ (jRensure) | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dommages | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| Obsèques | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| GAV | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
| Santé internationale | ✓ | — | ✓ | ✓ | ✓ | ✓ | ✓ | — |
