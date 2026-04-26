## 1. LLM Judge Server — Infrastructure Docker

- [x] 1.1 Créer `llm/config.yml` avec les paramètres du modèle (nom, SHA256, URL HF, port 8080, threads)
- [x] 1.2 Créer `llm/docker-compose.yml` avec le service `llama-server` basé sur `ghcr.io/ggerganov/llama.cpp:server`
- [x] 1.3 Créer `llm/download.sh` — télécharge le GGUF depuis HF et vérifie le SHA256
- [x] 1.4 Créer `llm/models/.gitkeep` et ajouter `llm/models/*.gguf` au `.gitignore` racine
- [x] 1.5 Vérifier que `docker compose up` démarre le serveur et que `GET /health` retourne 200 — mettre à jour README.md

## 2. LLM Judge Server — Validation du juge

- [ ] 2.1 Spike : envoyer 5 paires (expected, generated) manuelles au juge et valider la cohérence des verdicts
- [ ] 2.2 Mesurer la latence moyenne par jugement sur CPU (tok/s effectif) — documenter dans `llm/config.yml`
- [x] 2.3 Définir et documenter le prompt système du juge dans `llm/judge-prompt.md`

## 3. Evaluation Runner — Structure du projet

- [x] 3.1 Initialiser `runner/` avec `uv init` et créer `runner/pyproject.toml`
- [x] 3.2 Créer `runner/config.yml.example` avec les clés : `genia_api_url`, `judge_api_url`, `workers`, `timeout_s`
- [x] 3.3 Créer `runner/datasets/` avec un dataset exemple `offre/ideal.jsonl` (5 cas minimum)
- [x] 3.4 Créer `runs/` avec `.gitkeep` et ajouter `runs/*.jsonl` au `.gitignore` — mettre à jour README.md

## 4. Evaluation Runner — Implémentation

- [x] 4.1 Implémenter `runner/run.py` — chargement dataset JSONL, appel API Genia, écriture run JSONL ligne par ligne
- [x] 4.2 Implémenter `runner/metrics/llm_judge.py` — appel `/v1/chat/completions` du juge, parsing du verdict
- [ ] 4.3 Tester un run complet sur le dataset exemple — vérifier la structure JSONL produite

## 5. Results Analyzer — Structure du projet

- [x] 5.1 Initialiser `analyzer/` avec `uv init` et créer `analyzer/pyproject.toml`
- [x] 5.2 Créer `analyzer/reports/` avec `.gitkeep`

## 6. Results Analyzer — Implémentation

- [x] 6.1 Implémenter `analyzer/analyze.py` — taux de pass global, par `scenario_family`, par `domain`, avec option `--failed-metric`
- [x] 6.2 Implémenter `analyzer/compare.py` — diff de deux runs, cas dont le statut a changé, évolution des taux
- [ ] 6.3 Tester `analyze.py` sur le run exemple produit à l'étape 4.4
- [ ] 6.4 Tester `compare.py` sur deux runs synthétiques avec des statuts différents

## 7. Documentation et finalisation

- [x] 7.1 Mettre à jour README.md avec la procédure complète : download modèle → démarrer llm/ → lancer un run → analyser
- [x] 7.2 Mettre à jour `openspec/config.yaml` si des conventions nouvelles émergent (format runs, structure datasets)
