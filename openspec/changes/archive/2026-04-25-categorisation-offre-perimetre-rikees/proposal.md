## Why

Le chatbot Genia doit couvrir le périmètre fonctionnel de l'**Espace partenaire Rikees Sol**, la plateforme centrale par laquelle les courtiers accèdent aux offres, réalisent leurs tarifications et pilotent leur activité. Pour qu'il puisse répondre précisément aux questions d'un courtier sur ce qui est faisable depuis cette plateforme, il faut d'abord consolider et structurer la documentation des interactions disponibles, des univers produits accessibles et des périmètres de couverture associés.

## What Changes

- Introduire une capability `offer-categorization` qui documente la taxonomie des lignes de produits accessibles depuis l'Espace partenaire Rikees Sol (emprunteur, santé, prévoyance, IARD, obsèques, GAV, santé internationale) et les entités associées.
- Introduire une capability `coverage-scope` qui documente les périmètres de couverture par ligne de produit accessible sur la plateforme (garanties, profils éligibles, conditions d'âge, dispositifs réglementaires, exclusions).
- Introduire une capability `espace-partenaire-interactions` qui documente l'ensemble des interactions réalisables par un courtier depuis l'Espace partenaire Rikees Sol (tarification, souscription, suivi dossiers, gestion portefeuille).

## Capabilities

### New Capabilities

- `offer-categorization`: Taxonomie des lignes de produits accessibles depuis l'Espace partenaire (emprunteur, santé individuelle/collective, prévoyance individuelle/professionnelle, IARD, obsèques, GAV, santé internationale) avec les entités distributrices associées.
- `coverage-scope`: Périmètre de couverture par ligne de produit — garanties, profils éligibles, conditions d'âge, dispositifs réglementaires (Lemoine, DDA), plafonds et exclusions.
- `espace-partenaire-interactions`: Cartographie des interactions fonctionnelles réalisables depuis l'Espace partenaire Rikees Sol — univers accessibles, actions disponibles par univers (tarification, devis, souscription, suivi, pilotage).

### Modified Capabilities

## Impact

- Création de trois fichiers de documentation sous `docs/` (consolidation des connaissances métier).
- Périmètre limité à l'Espace partenaire Rikees Sol — les autres plateformes (TopScan, SaaS Rikees Tech hors espace partenaire) sont hors scope.
- Ni intégration MCP ni dataset d'évaluation dans cette phase : documentation uniquement.
