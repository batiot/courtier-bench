## Why

Le benchmark d'évaluation du chatbot Genia manque de scénarios concrets couvrant les deux périmètres fonctionnels les plus sollicités par les courtiers : la tarification/devis et le suivi des dossiers/portefeuille. Sans scénarios structurés par persona, il est impossible d'évaluer la pertinence des réponses du chatbot pour des profils d'usage réels et différenciés.

## What Changes

- Définition d'un catalogue de scénarios d'interaction chatbot pour 6 personas, restreint aux deux périmètres :
  - **Parcours de tarification et de devis**
  - **Suivi des dossiers et gestion du portefeuille**
- Chaque scénario précise : la persona concernée, le(s) périmètre(s) impliqués, la complexité (simple / complexe), et les grandes lignes (sans contenu détaillé des échanges)
- Les scénarios couvrent les trois familles : idéal, court (réaliste), adversarial
- Structure organisationnelle du catalogue documentée dans deux specs dédiées (une par périmètre), agrégeant tous les scénarios par persona

## Capabilities

### New Capabilities

- `scenarios-tarification-devis` : Catalogue structuré des scénarios d'interaction chatbot sur le périmètre « Parcours de tarification et de devis » — organisation par persona, classification simple/complexe, grandes lignes de chaque scénario
- `scenarios-suivi-portefeuille` : Catalogue structuré des scénarios d'interaction chatbot sur le périmètre « Suivi des dossiers et gestion du portefeuille » — organisation par persona, classification simple/complexe, grandes lignes de chaque scénario

### Modified Capabilities

<!-- Aucune spec existante ne couvre ces périmètres de scénarios. -->

## Impact

- Alimente directement la phase de génération de conversations (étape 2 du projet)
- Référence pour la construction des datasets JSONL d'évaluation
- Base pour l'identification des tools MCP à implémenter (moteur de tarification, vue portefeuille, suivi dossiers)
- Aucun impact sur le code existant (phase de spécification documentaire uniquement)
