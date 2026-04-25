## ADDED Requirements

### Requirement: Univers produits accessibles depuis le portail
Le système SHALL documenter la liste complète des univers produits accessibles depuis l'Espace partenaire Rikees Sol, avec pour chaque univers l'identifiant, le libellé, l'entité distributrice associée et le périmètre de produits disponibles.

#### Scenario: Liste des univers disponibles
- **WHEN** un courtier se connecte à l'Espace partenaire Rikees Sol
- **THEN** il accède aux univers suivants : santé individuelle, obsèques, GAV, dommages, emprunteur, prévoyance pro, santé internationale

#### Scenario: Entité associée à un univers
- **WHEN** la documentation décrit l'univers emprunteur
- **THEN** elle identifie Rikees Sol comme distributeur grossiste et jRensure comme fournisseur du comparateur et du parcours digital associé

### Requirement: Parcours de tarification et de devis
Le système SHALL documenter les étapes du parcours de tarification disponible depuis l'Espace partenaire : saisie du profil client, obtention du tarif, comparaison multi-offres et export du devis.

#### Scenario: Démarrage d'une tarification emprunteur
- **WHEN** un courtier initie une tarification dans l'univers emprunteur
- **THEN** le portail lui permet de saisir le profil emprunteur (type de prêt, montant, durée, profil médical) et d'obtenir une comparaison des offres disponibles dans la gamme

#### Scenario: Export d'un devis
- **WHEN** le courtier sélectionne une offre tarifée
- **THEN** le portail génère un document de devis téléchargeable conforme aux exigences réglementaires (DDA)

### Requirement: Parcours de souscription en ligne
Le système SHALL documenter le parcours de souscription accessible depuis le portail : transmission du dossier client, signature électronique, gestion des statuts et récupération des documents contractuels.

#### Scenario: Transmission du dossier de souscription
- **WHEN** un courtier soumet un dossier de souscription depuis le portail
- **THEN** les données client (KYC, questionnaire de risque, pièces justificatives) sont transmises à l'assureur/grossiste et un statut de souscription est retourné (brouillon, soumis, accepté, refusé, en attente de pièces)

#### Scenario: Récupération des documents contractuels
- **WHEN** la souscription est acceptée
- **THEN** le courtier peut télécharger depuis le portail le numéro de police, l'attestation d'assurance et les conditions particulières

#### Scenario: Intégration de la signature électronique
- **WHEN** le parcours de souscription requiert une signature du client
- **THEN** le portail propose un mécanisme de signature électronique intégré au parcours digital

### Requirement: Suivi des dossiers et portefeuille
Le système SHALL documenter les fonctions de suivi disponibles depuis le portail : consultation des dossiers en cours, états d'avancement et accès au portefeuille global du courtier.

#### Scenario: Consultation des dossiers en cours
- **WHEN** un courtier accède à la section suivi du portail
- **THEN** il visualise l'ensemble de ses dossiers avec leur statut en temps réel (en cours, en attente, émis, refusé)

#### Scenario: Vue portefeuille
- **WHEN** un courtier accède à la vue portefeuille
- **THEN** il peut consulter ses contrats actifs, les échéances à venir et les contrats résiliés, filtrables par univers produit

### Requirement: Tableaux de bord et pilotage de l'activité
Le système SHALL documenter les outils de pilotage accessibles depuis l'Espace partenaire : indicateurs de production, performances commerciales et suivi des encaissements.

#### Scenario: Tableau de bord de production
- **WHEN** un courtier accède au tableau de bord
- **THEN** il dispose d'indicateurs de production par univers produit (nombre de devis, taux de transformation, contrats émis sur la période)

#### Scenario: Suivi des flux financiers depuis le portail
- **WHEN** le courtier consulte la section commissions/primes
- **THEN** il accède aux informations de quittancement et aux bordereaux de commissions disponibles sur le portail
