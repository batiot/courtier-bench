# courtier-bench

Projet de construction d'un benchmark d'évaluation pour le chatbot **Genia** dans le domaine du **courtage en assurance**.

---

## Objectif

Identifier et construire un dataset permettant d'évaluer le chatbot Genia selon trois types de scénarios :

- **Idéal** — questions claires, bien formulées, dans le scope
- **Court / Réaliste** — langage naturel, fautes, formulations vagues
- **Adversarial** — prompt injection, hors-scope, tentatives de contournement

Le projet couvre également l'identification des **tools métier** et de la **knowledge base** du courtier, exposés sous forme de tools MCP.

---

## Phases

```
Phase 1 — Collecte        Recherche et organisation des connaissances métier
Phase 2 — Génération      Conversations types par scénario et domaine
Phase 3 — Dataset         Questions/réponses structurées pour l'évaluation
Phase 4 — MCP bouchon     Serveur MCP simulant les tools métier du courtier
Phase 5 — Évaluation      Harness d'évaluation et runs automatisés
```

---

## Structure du projet

```
courtier-bench/
├── llm/                   Serveur LLM juge local (llama.cpp Docker + Gemma-4-E2B)
│   ├── docker-compose.yml
│   ├── config.yml         Paramètres modèle et serveur
│   ├── download.sh        Téléchargement du modèle GGUF
│   ├── judge-prompt.md    Prompt système du juge LLM-as-a-judge
│   └── models/            Modèles GGUF (gitignorés, ~3.5 Go)
├── runner/                Pipeline d'évaluation (Python/uv)
│   ├── run.py             Point d'entrée — appelle Genia + juge
│   ├── metrics/
│   │   └── llm_judge.py   Métrique LLM-as-a-judge
│   ├── datasets/          Datasets de scénarios générés par Copilot
│   │   └── offre/
│   │       └── ideal.jsonl
│   └── config.yml.example Configuration à copier
├── analyzer/              Analyse des résultats (Python/uv)
│   ├── analyze.py         Rapport par run
│   ├── compare.py         Comparaison de deux runs
│   └── reports/           Rapports générés
├── runs/                  Fichiers de runs JSONL (gitignorés)
├── docs/
│   └── reference/
│       └── eval.md        Référence méthodologique (Devoxx France 2026)
├── openspec/              Spécifications et changes du projet
└── README.md
```

---

## Documentation métier

La knowledge base structurée est disponible dans le dossier `docs/` :

| Document | Description |
|---|---|
| [docs/offre-Rikees.md](docs/offre-Rikees.md) | Vue d'ensemble du positionnement Rikees, entités clés et gamme de produits B2B |
| [docs/relation-b2b-courtierr.md](docs/relation-b2b-courtierr.md) | Interactions SI d'un courtier avec les grossistes, assureurs et solutions B2B |
| [docs/offer-categorization.md](docs/offer-categorization.md) | Taxonomie des 7 univers produits de l'Espace partenaire Rikees Sol, entités distributrices et rôles B2B |
| [docs/coverage-scope.md](docs/coverage-scope.md) | Périmètres de couverture par ligne de produit : garanties, profils éligibles, dispositifs réglementaires, exclusions, modularité |
| [docs/espace-partenaire-interactions.md](docs/espace-partenaire-interactions.md) | Cartographie des interactions fonctionnelles réalisables depuis l'Espace partenaire : tarification, souscription, suivi, pilotage |

---

## Domaines métier couverts

| Domaine | Tools MCP envisagés |
|---------|---------------------|
...

---

## Stack technique

- **Python** — géré exclusivement avec [`uv`](https://docs.astral.sh/uv/)
- **MCP** — Model Context Protocol pour les bouchons de tools
- **YAML / JSONL** — format des datasets et des tâches d'évaluation
- **LLM-as-judge** — grading des outputs libres (rubrique)
- **Code-based graders** — string match, regex, vérification d'appels de tools

---

## Démarrage rapide

### 1. Serveur LLM juge (llm/)

```bash
# Télécharger le modèle GGUF (~3.5 Go, une seule fois)
cd llm && bash download.sh

# Démarrer le serveur LLM (port 8080)
docker compose up

# Vérifier que le serveur répond
curl http://localhost:8080/health
```

### 2. Lancer un run d'évaluation (runner/)

```bash
# Copier et adapter la configuration
cp runner/config.yml.example runner/config.yml

# Lancer un run sur un dataset
cd runner && uv run run.py --dataset datasets/offre/ideal.jsonl
# → Produit runs/run_YYYYMMDD_HHMMSS.jsonl
```

### 3. Analyser les résultats (analyzer/)

```bash
# Rapport sur un run
cd analyzer && uv run analyze.py --run ../runs/run_20260425_143200.jsonl

# Comparer deux runs
cd analyzer && uv run compare.py --run-a ../runs/run_A.jsonl --run-b ../runs/run_B.jsonl
```

### Autres commandes

```bash
# Installer uv si besoin
curl -LsSf https://astral.sh/uv/install.sh | sh
```

---

## Format des datasets

Chaque ligne du fichier JSONL représente un cas de test :

```json
{
  "id": "habitation_ideal_001",
  "input": "Quelle est la franchise pour un dégât des eaux ?",
  "expected_output": "La franchise standard pour un dégât des eaux est de 150€...",
  "scenario_type": "ideal",
  "domain": "habitation",
  "persona": "particulier_prudent",
  "grader": "llm_rubric"
}
```

---

## Approche d'évaluation

Inspirée du guide Anthropic [*Demystifying evals for AI agents*](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents) et du talk [*Mesurer l'immesurable*](docs/reference/eval.md) (Devoxx France 2026) :

| Type de grader | Usage |
|----------------|-------|
| **Code-based** | Outputs contraints (oui/non, routing, vérification de tool calls) |
| **LLM-as-judge** | Outputs libres (pertinence, justesse, empathie, ton) |
| **Human spot-check** | Calibration périodique des graders LLM |

Métriques suivies : `pass@1`, `pass^k`, nombre de turns, nombre de tool calls, latence.

---

## Références

- [docs/reference/eval.md](docs/reference/eval.md) — Devoxx France 2026, Erin Pacquetet (SCIAM)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
