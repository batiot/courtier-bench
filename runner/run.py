"""Evaluation runner — loads a JSONL dataset, calls Genia, judges with LLM-as-a-judge."""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from datetime import datetime
from pathlib import Path

import httpx
import yaml

from metrics.llm_judge import judge


def load_config(config_path: Path) -> dict:
    if not config_path.exists():
        print(
            f"ERROR: config.yml not found at {config_path}\n"
            f"Copy config.yml.example to config.yml and fill in your values.",
            file=sys.stderr,
        )
        sys.exit(1)
    with open(config_path) as f:
        return yaml.safe_load(f)


def call_genia(input_text: str, cfg: dict) -> tuple[str, float]:
    """Call the Genia API and return (response_text, latency_ms)."""
    t0 = time.monotonic()
    with httpx.Client(timeout=cfg["timeout_s"]) as client:
        headers = {}
        if cfg.get("genia_api_key"):
            headers["Authorization"] = f"Bearer {cfg['genia_api_key']}"
        resp = client.post(
            cfg["genia_api_url"],
            json={"message": input_text},
            headers=headers,
        )
        resp.raise_for_status()
    latency_ms = round((time.monotonic() - t0) * 1000)
    data = resp.json()
    # Adapt to your actual Genia API response shape
    generated = data.get("response") or data.get("content") or data.get("message") or str(data)
    return generated, latency_ms


def run(dataset_path: Path, cfg: dict, runs_dir: Path) -> Path:
    runs_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    run_file = runs_dir / f"run_{timestamp}.jsonl"

    cases = []
    with open(dataset_path) as f:
        for line in f:
            line = line.strip()
            if line:
                cases.append(json.loads(line))

    print(f"Dataset: {dataset_path} ({len(cases)} cases)")
    print(f"Output:  {run_file}")
    print()

    inference_cfg = cfg.get("inference", {})

    with open(run_file, "w") as out:
        for i, case in enumerate(cases, 1):
            case_id = case.get("id", f"case_{i:04d}")
            print(f"[{i}/{len(cases)}] {case_id}", end=" ", flush=True)

            try:
                generated, latency_ms = call_genia(case["input"], cfg)
            except Exception as e:
                print(f"ERROR (genia): {e}")
                result = {
                    "id": case_id,
                    "scenario_family": case.get("scenario_family", ""),
                    "domain": case.get("domain", ""),
                    "input": case["input"],
                    "expected": case.get("expected", ""),
                    "generated": None,
                    "metrics": {"llm_judge": {"pass": None, "rationale": f"Genia error: {e}"}},
                    "latency_ms": None,
                    "error": str(e),
                }
                out.write(json.dumps(result, ensure_ascii=False) + "\n")
                out.flush()
                continue

            try:
                verdict = judge(
                    expected=case.get("expected", ""),
                    generated=generated,
                    judge_api_url=cfg["judge_api_url"],
                    timeout_s=cfg["timeout_s"],
                    inference=inference_cfg,
                )
            except Exception as e:
                print(f"ERROR (judge): {e}")
                verdict = {"pass": None, "rationale": f"Judge error: {e}", "raw": ""}

            result = {
                "id": case_id,
                "scenario_family": case.get("scenario_family", ""),
                "domain": case.get("domain", ""),
                "input": case["input"],
                "expected": case.get("expected", ""),
                "generated": generated,
                "metrics": {"llm_judge": {"pass": verdict["pass"], "rationale": verdict["rationale"]}},
                "latency_ms": latency_ms,
            }

            status = "✓" if verdict["pass"] else ("?" if verdict["pass"] is None else "✗")
            print(f"{status} ({latency_ms}ms)")

            out.write(json.dumps(result, ensure_ascii=False) + "\n")
            out.flush()

    passed = sum(1 for _ in open(run_file) for r in [json.loads(_)] if r["metrics"]["llm_judge"]["pass"] is True)
    total = len(cases)
    print(f"\nDone — {passed}/{total} passed ({100*passed//total if total else 0}%)")
    print(f"Run saved: {run_file}")
    return run_file


def main() -> None:
    parser = argparse.ArgumentParser(description="Run evaluation against Genia chatbot")
    parser.add_argument("--dataset", required=True, help="Path to JSONL dataset file")
    parser.add_argument("--config", default=Path(__file__).parent / "config.yml", help="Path to config.yml")
    args = parser.parse_args()

    cfg = load_config(Path(args.config))
    runs_dir = Path(cfg.get("runs_dir", "../runs"))
    run(Path(args.dataset), cfg, runs_dir)


if __name__ == "__main__":
    main()
