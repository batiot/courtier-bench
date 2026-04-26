## ADDED Requirements

### Requirement: Rapport d'analyse d'un run
L'analyzer SHALL produire un rapport lisible pour un fichier de run JSONL donné, incluant le taux de réussite global, le détail par famille de scénario et par domaine.

#### Scenario: Analyse nominale d'un run
- **WHEN** `uv run analyzer/analyze.py --run runs/run_20260425_143200.jsonl` est exécuté
- **THEN** un rapport est affiché en console (et optionnellement écrit dans `analyzer/reports/`) avec le taux de pass global, par `scenario_family` et par `domain`

#### Scenario: Fichier de run vide ou corrompu
- **WHEN** le fichier JSONL de run est vide ou contient des lignes invalides
- **THEN** l'analyzer affiche un avertissement et indique le nombre de cas ignorés

### Requirement: Comparaison de deux runs
L'analyzer SHALL comparer deux fichiers de run et produire un diff des métriques — cas qui ont changé de statut (pass→fail ou fail→pass) et évolution des taux par dimension.

#### Scenario: Comparaison nominale
- **WHEN** `uv run analyzer/compare.py --run-a runs/run_A.jsonl --run-b runs/run_B.jsonl` est exécuté
- **THEN** le rapport liste les cas dont le statut LLM-judge a changé entre A et B, et affiche l'évolution du taux de pass global et par dimension

#### Scenario: Cas présents dans un seul run
- **WHEN** un cas est présent dans le run A mais pas dans le run B (ou vice versa)
- **THEN** l'analyzer le signale explicitement dans la section "cas manquants" sans faire échouer la comparaison

### Requirement: Identification des cas échoués
L'analyzer SHALL permettre de filtrer et lister les cas ayant échoué sur une métrique donnée, pour faciliter le debug et la revue humaine.

#### Scenario: Filtrage par métrique échouée
- **WHEN** l'option `--failed-metric llm_judge` est passée à `analyze.py`
- **THEN** le rapport liste uniquement les cas où `metrics.llm_judge.pass` est `false`, avec leur `id`, leur `input` et la `rationale` du juge
