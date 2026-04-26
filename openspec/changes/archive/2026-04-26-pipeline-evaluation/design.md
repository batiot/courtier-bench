## Context

Le projet courtier-bench vise à évaluer le chatbot Genia sur des scénarios métier du courtage en assurance. L'évaluation nécessite trois composants distincts : un serveur LLM local jouant le rôle de juge, un runner qui orchestre les appels et collecte les résultats, et un analyzer qui exploite les fichiers de runs.

Les datasets (inputs + expected outputs) sont générés par GitHub Copilot dans ce dépôt et versionnés en YAML/JSONL. Le chatbot Genia réel tourne sur une infrastructure externe et est appelé par le runner via son API. Le LLM local n'est utilisé que comme juge — il ne simule pas Genia et ne génère pas les scénarios.

Contrainte matérielle : CPU uniquement, 16 Go RAM.

## Goals / Non-Goals

**Goals:**
- Serveur LLM local reproductible, démarrable en une commande (`docker compose up`)
- Runner qui produit des fichiers de runs structurés et reproductibles (JSONL)
- Analyzer qui produit un rapport par run et compare deux runs entre eux
- Stack Python entièrement gérée via `uv`

**Non-Goals:**
- Génération automatique de datasets par le LLM local (Copilot s'en charge)
- Fine-tuning ou modification du modèle Gemma
- Interface graphique ou dashboard temps-réel
- Intégration CI/CD dans cette phase

## Decisions

### D1 — llama.cpp Docker officiel plutôt que llama-cpp-python

**Choix** : `ghcr.io/ggerganov/llama.cpp:server`

**Pourquoi** : L'image officielle compile llama.cpp avec les flags CPU optimaux (AVX2/AVX512) automatiquement, ce qui est critique pour la performance sur CPU pur. llama-cpp-python requiert une compilation manuelle avec `CMAKE_ARGS` pour obtenir le même résultat — source d'erreurs et de variabilité entre machines.

L'API exposée est OpenAI-compatible (`/v1/chat/completions`), ce qui rend le runner agnostique au backend.

**Alternative écartée** : llama-cpp-python server — plus d'intégration Python native mais compilation CPU sous-optimale par défaut.

### D2 — Gemma-4-E2B-it Q4_K_M comme juge

**Choix** : `gemma-4-E2B-it` quantisé Q4_K_M (~3.5 Go GGUF)

**Pourquoi** : Le juge a une tâche simple (4 étapes vs 10 pour le LLM de prod, cf. `docs/reference/eval.md`). La vitesse prime sur la qualité absolue. E2B = 2.3B paramètres effectifs, ~8-15 tok/s sur CPU — acceptable pour des centaines d'évaluations. E4B (~5-5.5 Go) serait plus lent sans gain justifié pour cette tâche.

Le "E" dans E2B = "Effective parameters" (Per-Layer Embeddings). Le modèle est conçu pour l'on-device, ce qui correspond exactement au contexte CPU.

**Alternative écartée** : E4B — meilleure qualité mais ~50% plus lent sur CPU pour une tâche de jugement simple.

### D3 — Thinking mode désactivé pour le juge

**Choix** : `enable_thinking=False` dans les appels au juge

**Pourquoi** : Les modèles E2B/E4B n'émettent pas de bloc thinking vide quand thinking=OFF (comportement différent des grands modèles Gemma-4). La réponse est directement parseable sans post-traitement. Le thinking ajouterait de la latence sans valeur pour une décision binaire (pass/fail).

### D4 — Format JSONL pour les runs

**Choix** : Un fichier JSONL par run, nommé `run_YYYYMMDD_HHMMSS.jsonl`

**Pourquoi** : JSONL permet le streaming (écriture ligne par ligne pendant le run), la lecture partielle, et la concaténation de fichiers. Chaque ligne = un cas d'évaluation complet avec ses métriques. Compatible avec les outils de traitement standard (jq, pandas).

**Structure d'une ligne** :
```json
{
  "id": "offre/ideal/q001",
  "scenario_family": "ideal",
  "domain": "offre",
  "input": "...",
  "expected": "...",
  "generated": "...",
  "metrics": {
    "llm_judge": {"pass": true, "rationale": "..."},
    "string_match": {"pass": true, "matches": ["..."]}
  },
  "latency_ms": 1240
}
```

### D5 — Modèle GGUF stocké localement hors git

**Choix** : `llm/models/` dans `.gitignore`, téléchargé via `llm/download.sh`

**Pourquoi** : Les GGUF font 3-5 Go, incompatibles avec git. Le script `download.sh` utilise `huggingface-cli` (ou `wget`) pour récupérer le fichier depuis un dépôt communautaire HF (ex: `bartowski/gemma-4-E2B-it-GGUF`). Le modèle est référencé par son hash SHA256 dans `llm/config.yml` pour garantir la reproductibilité.

## Risks / Trade-offs

**[Risque] Latence CPU élevée → runs lents sur de grands datasets**
Mitigation : Parallélisme limité au niveau du runner (N workers configurables), test du throughput réel avant de dimensionner les datasets.

**[Risque] Qualité du juge E2B insuffisante pour les cas nuancés**
Mitigation : Spike de validation — comparer jugements E2B vs jugements humains sur 50 cas avant de généraliser. Possibilité de basculer sur E4B si nécessaire (même config Docker, GGUF différent).

**[Risque] API Genia inaccessible / instable pendant les runs**
Mitigation : Le runner intègre retry + timeout configurables. Les résultats partiels sont écrits en JSONL au fil de l'eau, pas à la fin.

**[Risque] Modèle GGUF non disponible (lien HF rompu)**
Mitigation : `download.sh` référence le fichier par SHA256 et supporte un miroir de fallback configurable.

## Open Questions

- Quel est le format exact de l'API Genia (endpoint, auth, format de réponse) ? → À documenter dans `runner/config.yml.example`
- Quel nombre de workers parallèles est optimal sur la machine cible ? → À mesurer lors du spike performance
- Les fichiers de runs doivent-ils inclure le prompt exact envoyé au juge ? → Utile pour le debug, à décider avant l'implémentation du runner
