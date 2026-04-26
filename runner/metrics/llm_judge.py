"""LLM-as-a-judge metric — calls the local llama.cpp server."""
from __future__ import annotations

import httpx


SYSTEM_PROMPT = """\
Tu es un évaluateur de réponses pour un chatbot d'assurance.

Ta tâche : vérifier si une réponse générée contient des omissions ou des contradictions par rapport à une réponse de référence.

Règles :
- Réponds uniquement par "PASS" ou "FAIL" suivi d'une courte explication (1-2 phrases).
- PASS : la réponse générée couvre les points factuels essentiels sans contradiction.
- FAIL : la réponse générée omet un point factuel important ou contredit la référence.
- Ignore les différences de style, de formulation ou d'ordre des informations.
- Ignore les informations supplémentaires correctes dans la réponse générée.

Format de réponse :
PASS|FAIL: <explication courte>\
"""

USER_TEMPLATE = """\
Réponse de référence :
{expected}

Réponse générée :
{generated}

Évalue la réponse générée.\
"""


def judge(
    expected: str,
    generated: str,
    judge_api_url: str,
    timeout_s: float = 30.0,
    inference: dict | None = None,
) -> dict:
    """Call the LLM judge and return a verdict dict.

    Returns:
        {"pass": bool, "rationale": str, "raw": str}
    """
    inf = inference or {}
    payload = {
        "model": "judge",
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": USER_TEMPLATE.format(expected=expected, generated=generated)},
        ],
        "temperature": inf.get("temperature", 1.0),
        "top_p": inf.get("top_p", 0.95),
        "top_k": inf.get("top_k", 64),
        "max_tokens": inf.get("max_tokens", 256),
    }

    with httpx.Client(timeout=timeout_s) as client:
        resp = client.post(f"{judge_api_url}/v1/chat/completions", json=payload)
        resp.raise_for_status()

    raw = resp.json()["choices"][0]["message"]["content"].strip()
    passed = raw.upper().startswith("PASS")
    # Extract rationale after the colon
    rationale = raw.split(":", 1)[1].strip() if ":" in raw else raw

    return {"pass": passed, "rationale": rationale, "raw": raw}
