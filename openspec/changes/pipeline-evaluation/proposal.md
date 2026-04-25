## Why

Le projet dispose de datasets de scénarios et d'un chatbot Genia à évaluer, mais ne dispose d'aucun outillage pour exécuter les évaluations de façon reproductible. Il faut un pipeline d'évaluation automatisé qui permet de mesurer la qualité des réponses du chatbot sur l'ensemble des scénarios, de comparer des runs entre eux, et de détecter les régressions.

## What Changes

- Ajout d'un serveur LLM local (`llm/`) basé sur llama.cpp (Docker officiel) avec Gemma-4-E2B-it en tant que juge LLM-as-a-judge
- Ajout d'un runner d'évaluation (`runner/`) qui charge les datasets, appelle le chatbot Genia réel, puis soumet les paires (réponse attendue, réponse générée) au juge LLM
- Ajout d'un analyzer (`analyzer/`) qui analyse les résultats d'un run et permet la comparaison entre plusieurs runs

## Capabilities

### New Capabilities

- `llm-judge-server`: Serveur LLM local (llama.cpp Docker + Gemma-4-E2B-it Q4_K_M) exposant une API OpenAI-compatible sur le port 8080, utilisé exclusivement comme juge LLM-as-a-judge
- `evaluation-runner`: Pipeline d'évaluation qui charge les datasets de scénarios, appelle le chatbot Genia, collecte les outputs, applique les métriques (string match, LLM-as-a-judge) et produit un fichier de run structuré (JSONL)
- `results-analyzer`: Outil d'analyse des fichiers de run produits par le runner — rapport par run, comparaison entre deux runs (diff de métriques par domaine et famille de scénario)

### Modified Capabilities

## Impact

- Nouveau répertoire `llm/` : Docker Compose, script de téléchargement du modèle GGUF (~3.5 Go), `.gitignore` pour `models/`
- Nouveau répertoire `runner/` : structure Python (uv), config YAML pointant vers l'API Genia et l'API juge
- Nouveau répertoire `analyzer/` : structure Python (uv), lecture des fichiers JSONL de runs
- Aucun impact sur les specs existantes (offre, couverture, interactions, catalogue B2B)
- Dépendance externe : image Docker `ghcr.io/ggerganov/llama.cpp:server`, modèle GGUF depuis Hugging Face
