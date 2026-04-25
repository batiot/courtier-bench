## ADDED Requirements

### Requirement: Taxonomie des lignes de produits
Le système SHALL exposer une classification des lignes de produits d'un courtier grossiste B2B couvrant au minimum : assurance emprunteur, santé individuelle et collective, prévoyance individuelle et professionnelle, dommages/IARD.

#### Scenario: Récupération de toutes les catégories d'offres
- **WHEN** le tool `get_offer_categories` est appelé sans filtre
- **THEN** le système retourne la liste complète des lignes de produits avec leur identifiant, leur libellé et l'entité grossiste associée (ex. Rikees Sol)

#### Scenario: Filtrage par entité distributrice
- **WHEN** le tool `get_offer_categories` est appelé avec le paramètre `entity = "Rikees Sol"`
- **THEN** le système retourne uniquement les lignes de produits distribuées par cette entité

#### Scenario: Question hors-scope sur une entité inexistante
- **WHEN** le tool `get_offer_categories` est appelé avec une entité fictive (ex. `entity = "Rikees Fictif"`)
- **THEN** le système retourne une liste vide et n'invente pas de catégories

### Requirement: Association entités / rôles B2B
Le système SHALL associer chaque entité du groupe (Rikees Sol, jRensure, Rikees France, Rikees Tech) à son rôle dans la chaîne de distribution B2B (grossiste, courtier gestionnaire, comparateur, SaaS).

#### Scenario: Identification du rôle d'une entité
- **WHEN** Genia reçoit la question "Quelle entité gère les adhésions et les sinistres pour le compte des courtiers ?"
- **THEN** Genia identifie Rikees France comme courtier gestionnaire pour le compte de tiers

#### Scenario: Distinction grossiste vs gestionnaire
- **WHEN** Genia reçoit "Quelle est la différence entre Rikees Sol et Rikees France ?"
- **THEN** Genia distingue le rôle de distribution grossiste (Rikees Sol) du rôle de gestion opérationnelle pour compte de tiers (Rikees France)

### Requirement: Canaux de distribution par ligne de produit
Le système SHALL indiquer pour chaque ligne de produit les canaux de distribution disponibles (extranet partenaire, API, comparateur en ligne, courtier de proximité).

#### Scenario: Canal digital pour l'assurance emprunteur
- **WHEN** Genia reçoit "Comment un courtier peut-il distribuer de l'assurance emprunteur via Rikees ?"
- **THEN** Genia cite l'espace partenaire Rikees Sol, les parcours digitaux jRensure et l'interfaçage avec les solutions SaaS Rikees Tech
