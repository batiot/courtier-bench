## Context

Le projet courtier-bench construit un benchmark d'évaluation pour le chatbot Genia dans le domaine du courtage en assurance. Pour répondre correctement aux questions d'un courtier sur ce qu'il peut faire depuis l'**Espace partenaire Rikees Sol**, Genia doit s'appuyer sur une knowledge base structurée couvrant les univers produits accessibles, les périmètres de couverture et les interactions fonctionnelles disponibles sur cette plateforme.

La documentation source existante (`docs/offre-Rikees.md`, `docs/relation-b2b-courtierr.md`) est narrative. Cette change vise uniquement à consolider et structurer ces informations sous forme de documentation exploitable — sans développement MCP ni génération de datasets dans cette phase.

## Goals / Non-Goals

**Goals:**
- Documenter la taxonomie des univers produits accessibles depuis l'Espace partenaire Rikees Sol.
- Documenter les périmètres de couverture par ligne de produit (garanties, profils, dispositifs réglementaires).
- Cartographier les interactions fonctionnelles réalisables par un courtier depuis l'Espace partenaire.

**Non-Goals:**
- Développement de tools MCP (phase ultérieure).
- Génération de datasets d'évaluation (phase ultérieure).
- Documenter les outils hors Espace partenaire (TopScan standalone, SaaS Rikees Tech, jRensure en dehors du portail).
- Modéliser les flux financiers, sinistres ou CRM.

## Decisions

### Décision 1 : Documentation Markdown dans `docs/`

La consolidation se fait sous forme de fichiers Markdown structurés dans `docs/`, en cohérence avec la documentation existante (`docs/offre-Rikees.md`).

**Rationale** : format immédiatement lisible, versionné dans le repo, réutilisable comme source pour la knowledge base et les futurs datasets.

**Alternatives considérées** :
- YAML structuré : utile pour les fixtures MCP mais pas optimal pour la lecture humaine à ce stade.

### Décision 2 : Organisation par capability

Trois documents distincts : taxonomie des offres, périmètres de couverture, interactions Espace partenaire. Chaque document correspond à une capability définie dans la proposal.

**Rationale** : séparation claire facilitant la navigation et la réutilisation partielle lors des phases MCP et évaluation.

## Risks / Trade-offs

- **[Risque] Informations Rikees partielles** → La documentation est basée sur les sources disponibles dans `docs/` ; elle sera annotée comme référence d'exemple, non contractuelle.
- **[Risque] Évolution des offres** → Les documents sont versionnés ; une mise à jour manuelle est nécessaire si le périmètre de la plateforme évolue.
- **[Trade-off] Documentation statique** → Pas de validation automatique de la complétude ; la qualité dépend de la qualité des sources.
