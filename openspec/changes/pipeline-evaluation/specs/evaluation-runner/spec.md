## ADDED Requirements

### Requirement: Exécution d'un run d'évaluation complet
Le runner SHALL charger un ou plusieurs fichiers de dataset, appeler le chatbot Genia pour chaque input, soumettre la paire (expected, generated) au juge LLM, et écrire les résultats en JSONL au fil de l'eau.

#### Scenario: Run nominal sur un dataset
- **WHEN** `uv run runner/run.py --dataset datasets/offre/ideal.jsonl` est exécuté
- **THEN** un fichier `runs/run_YYYYMMDD_HHMMSS.jsonl` est créé, chaque ligne correspondant à un cas d'évaluation avec ses métriques

#### Scenario: Interruption en cours de run
- **WHEN** le runner est interrompu (SIGINT) après avoir traité N cas sur M
- **THEN** le fichier JSONL de run contient les N cas déjà traités, exploitables par l'analyzer

### Requirement: Format de run structuré
Chaque ligne du fichier JSONL de run SHALL contenir les champs : `id`, `scenario_family`, `domain`, `input`, `expected`, `generated`, `metrics`, `latency_ms`.

#### Scenario: Structure d'une ligne de run
- **WHEN** un cas d'évaluation est traité
- **THEN** la ligne JSONL contient au minimum les champs `id`, `input`, `expected`, `generated`, et `metrics.llm_judge.pass`

### Requirement: Métriques LLM-as-a-judge
Le runner SHALL soumettre chaque paire (expected, generated) au serveur LLM local (`llm/`) via l'API OpenAI-compatible et enregistrer le verdict (`pass`/`fail`) et la rationale.

#### Scenario: Jugement pass
- **WHEN** la réponse générée est factuellement correcte et complète par rapport à la réponse attendue
- **THEN** `metrics.llm_judge.pass` est `true` et `metrics.llm_judge.rationale` contient une explication non vide

#### Scenario: Jugement fail
- **WHEN** la réponse générée contient une omission ou une contradiction par rapport à la réponse attendue
- **THEN** `metrics.llm_judge.pass` est `false` et `metrics.llm_judge.rationale` identifie l'omission ou la contradiction

### Requirement: Configuration externalisée
Le runner SHALL lire sa configuration depuis `runner/config.yml` (URL de l'API Genia, URL du juge LLM, nombre de workers, timeouts).

#### Scenario: Configuration valide
- **WHEN** `runner/config.yml` est présent et valide
- **THEN** le runner utilise les paramètres de configuration sans nécessiter d'arguments en ligne de commande

#### Scenario: Configuration manquante
- **WHEN** `runner/config.yml` est absent
- **THEN** le runner échoue avec un message d'erreur explicite listant les paramètres requis
