# AGENTS.md

Ce projet est piloté par **openspec**. Avant toute intervention, lire les instructions détaillées dans :

```
openspec/config.yaml
```

Ce fichier contient le contexte du projet, les conventions, les règles de proposal/tâches/specs, et les références documentaires.

## Skills disponibles

Des skills spécialisés sont présents dans `.agents/skills/` :

| Skill | Description |
|---|---|
| `agentic-eval` | Patterns d'évaluation itérative, self-critique, evaluator-optimizer pipelines |
| `deepeval` | Travail avec le framework DeepEval (évaluation de LLMs en Python) |
| `documentation-writer` | Rédaction de documentation technique (Diátaxis) |
| `mcp-builder` | Création de serveurs MCP (FastMCP / MCP SDK) |
| `pdf` | Manipulation de fichiers PDF |
| `prompt-engineer` | Conception de prompts pour applications LLM |

Charger le skill pertinent avec `read_file` **avant** toute génération ou implémentation dans le domaine concerné.
