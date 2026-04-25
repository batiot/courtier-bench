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
├── data/
│   ├── raw/               Collecte brute (PDFs, notes, web)
│   ├── knowledge/         Knowledge base structurée par domaine
│   ├── conversations/     Conversations générées (ideal / court / adversarial)
│   └── datasets/          Datasets d'évaluation finaux (.jsonl)
├── mcp_server/            Serveur MCP de bouchon (segmenté par domaine)
│   ├── domains/
│   └── personas/
├── eval/                  Harness d'évaluation
│   ├── graders/
│   ├── tasks/
│   └── runner.py
├── docs/
│   └── reference/
│       └── eval.md        Référence méthodologique (Devoxx France 2026)
├── openspec/
│   └── config.yaml        Configuration openspec du projet
├── AGENTS.md              Instructions pour les agents IA
└── README.md
```

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

```bash
# Installer uv si besoin
curl -LsSf https://astral.sh/uv/install.sh | sh

# Initialiser le projet
uv sync

# Lancer le serveur MCP de bouchon (à venir)
uv run python mcp_server/server.py

# Lancer un run d'évaluation (à venir)
uv run python eval/runner.py --dataset data/datasets/eval_ideal.jsonl
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
