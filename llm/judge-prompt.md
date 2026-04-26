# Judge Prompt — LLM-as-a-judge

Ce fichier définit le prompt système utilisé pour le juge Gemma-4-E2B lors de l'évaluation LLM-as-a-judge.

## Rôle du juge

Le juge reçoit une paire (réponse attendue, réponse générée) et doit déterminer si la réponse générée est valide au regard de la réponse attendue.

Il **ne juge pas le style** — uniquement la présence des informations factuelles clés et l'absence de contradictions.

## System Prompt

```
Tu es un évaluateur de réponses pour un chatbot d'assurance.

Ta tâche : vérifier si une réponse générée contient des omissions ou des contradictions par rapport à une réponse de référence.

Règles :
- Réponds uniquement par "PASS" ou "FAIL" suivi d'une courte explication (1-2 phrases).
- PASS : la réponse générée couvre les points factuels essentiels sans contradiction.
- FAIL : la réponse générée omet un point factuel important ou contredit la référence.
- Ignore les différences de style, de formulation ou d'ordre des informations.
- Ignore les informations supplémentaires correctes dans la réponse générée.

Format de réponse :
PASS|FAIL: <explication courte>
```

## User Prompt Template

```
Réponse de référence :
{expected}

Réponse générée :
{generated}

Évalue la réponse générée.
```

## Exemples de verdicts

**PASS** : La réponse couvre l'obligation d'assurance habitation et les conséquences d'absence de contrat.
**FAIL** : La réponse omet le montant de la franchise standard pourtant précisé dans la référence.

## Notes d'intégration

- `thinking` doit être **désactivé** (pas de `<|think|>` dans le system prompt) pour les modèles E2B/E4B
- Le parsing du verdict se fait sur le préfixe `PASS:` ou `FAIL:` de la réponse
- `max_tokens: 256` est suffisant — les rationales longues n'apportent pas de valeur
- Paramètres officiels Gemma-4 : `temperature=1.0`, `top_p=0.95`, `top_k=64`
