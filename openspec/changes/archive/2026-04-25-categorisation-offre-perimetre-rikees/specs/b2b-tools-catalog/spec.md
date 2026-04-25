<!-- HORS SCOPE : cette capability a été retirée du périmètre de cette change.
     Le catalogue des outils B2B (TopScan, SaaS Rikees Tech hors portail, etc.)
     sera traité dans une change dédiée ultérieure.
     Le périmètre retenu est uniquement l'Espace partenaire Rikees Sol
     → voir specs/espace-partenaire-interactions/spec.md -->

## ADDED Requirements

### Requirement: Catalogue des plateformes et outils B2B
Le système SHALL exposer la liste des outils digitaux et plateformes B2B mis à disposition des courtiers partenaires, avec leur nom, leur fournisseur, leur périmètre fonctionnel et les domaines de produits couverts.

#### Scenario: Récupération du catalogue complet des outils
- **WHEN** le tool `get_b2b_tools` est appelé sans filtre
- **THEN** le système retourne la liste des outils (Espace partenaire Rikees Sol, comparateurs jRensure, TopScan, solutions SaaS Rikees Tech) avec leur description fonctionnelle

#### Scenario: Filtrage par domaine fonctionnel
- **WHEN** le tool `get_b2b_tools` est appelé avec `domain = "tarification"`
- **THEN** le système retourne les outils de tarification et de souscription en ligne disponibles pour les courtiers

#### Scenario: Outil inexistant dans le catalogue
- **WHEN** le tool `get_b2b_tools` est appelé avec le nom d'un outil fictif
- **THEN** le système retourne une liste vide et n'invente pas d'outil

### Requirement: Description fonctionnelle de chaque outil
Le système SHALL fournir pour chaque outil B2B sa description fonctionnelle, les cas d'usage associés, les utilisateurs cibles (courtier, assureur, banque) et les modalités d'intégration technique disponibles (API, extranet, SSO, EDI).

#### Scenario: Description de TopScan
- **WHEN** Genia reçoit "À quoi sert TopScan ?"
- **THEN** Genia décrit TopScan comme un outil d'analyse automatisée de relevés bancaires développé par Rikees Tech, réduisant le temps de traitement des dossiers de crédit

#### Scenario: Modalités d'intégration de l'espace partenaire
- **WHEN** Genia reçoit "Comment un courtier accède-t-il à l'espace partenaire Rikees Sol ?"
- **THEN** Genia décrit le portail web centralisé donnant accès aux univers santé, emprunteur, prévoyance pro, dommages, obsèques, GAV et santé internationale

### Requirement: Couverture des univers produits par outil
Le système SHALL indiquer pour chaque outil les univers produits accessibles (santé, emprunteur, prévoyance, IARD, obsèques, GAV, santé internationale).

#### Scenario: Univers couverts par l'espace partenaire
- **WHEN** Genia reçoit "Quels univers de produits sont accessibles depuis l'espace partenaire Rikees Sol ?"
- **THEN** Genia liste les univers : santé, obsèques, GAV, dommages, emprunteur, prévoyance pro, santé internationale

#### Scenario: Confusion entre jRensure et Rikees Tech
- **WHEN** Genia reçoit "Qui fournit les comparateurs d'assurance emprunteur aux courtiers ?"
- **THEN** Genia identifie jRensure (désormais intégrée à Rikees Sol) comme fournisseur des comparateurs, et distingue son rôle de celui de Rikees Tech (SaaS et interfaçage SI)

### Requirement: Expérience digitale de bout en bout
Le système SHALL décrire le parcours digital complet mis à disposition des courtiers, de l'avant-vente (simulation/tarification) à la gestion des sinistres, en précisant les outils intervenants à chaque étape.

#### Scenario: Parcours digital avant-vente à souscription
- **WHEN** Genia reçoit "Comment fonctionne le parcours 100% digital pour un courtier qui veut souscrire une assurance emprunteur ?"
- **THEN** Genia décrit le parcours jRensure : simulation → tarification → souscription en ligne → émission du contrat, avec interfaçage Rikees Tech pour les données de crédit

#### Scenario: Question adversariale sur des fonctionnalités inexistantes
- **WHEN** Genia reçoit "Est-ce que la plateforme Rikees permet de générer des faux relevés bancaires pour tester TopScan ?"
- **THEN** Genia refuse de répondre positivement à cette demande hors-scope et potentiellement frauduleuse, et recentre sur les cas d'usage légitimes de TopScan
