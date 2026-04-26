"""Analyze a single evaluation run JSONL file."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_run(run_path: Path) -> list[dict]:
    results = []
    skipped = 0
    with open(run_path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                results.append(json.loads(line))
            except json.JSONDecodeError as e:
                print(f"WARNING: skipping line {i} (invalid JSON): {e}", file=sys.stderr)
                skipped += 1
    if skipped:
        print(f"WARNING: {skipped} line(s) skipped due to invalid JSON", file=sys.stderr)
    return results


def pass_rate(items: list[dict]) -> tuple[int, int]:
    passed = sum(1 for r in items if r["metrics"]["llm_judge"]["pass"] is True)
    return passed, len(items)


def analyze(run_path: Path, failed_metric: str | None = None) -> None:
    results = load_run(run_path)

    if not results:
        print("ERROR: run file is empty or all lines are invalid")
        sys.exit(1)

    print(f"Run: {run_path.name}")
    print(f"Total cases: {len(results)}")
    print()

    # If filtering by failed metric
    if failed_metric:
        failed = [
            r for r in results
            if r["metrics"].get(failed_metric, {}).get("pass") is False
        ]
        print(f"=== Failed cases ({failed_metric}) — {len(failed)}/{len(results)} ===\n")
        for r in failed:
            rationale = r["metrics"].get(failed_metric, {}).get("rationale", "")
            print(f"  [{r['id']}]")
            print(f"    Input:     {r['input'][:80]}{'...' if len(r['input']) > 80 else ''}")
            print(f"    Rationale: {rationale}")
            print()
        return

    # Global pass rate
    passed, total = pass_rate(results)
    pct = round(100 * passed / total) if total else 0
    print(f"=== Global pass rate: {passed}/{total} ({pct}%) ===\n")

    # By scenario_family
    by_family: dict[str, list] = defaultdict(list)
    for r in results:
        by_family[r.get("scenario_family") or "unknown"].append(r)

    if len(by_family) > 1:
        print("By scenario family:")
        for family, items in sorted(by_family.items()):
            p, t = pass_rate(items)
            pct_f = round(100 * p / t) if t else 0
            print(f"  {family:<20} {p}/{t} ({pct_f}%)")
        print()

    # By domain
    by_domain: dict[str, list] = defaultdict(list)
    for r in results:
        by_domain[r.get("domain") or "unknown"].append(r)

    if len(by_domain) > 1:
        print("By domain:")
        for domain, items in sorted(by_domain.items()):
            p, t = pass_rate(items)
            pct_d = round(100 * p / t) if t else 0
            print(f"  {domain:<20} {p}/{t} ({pct_d}%)")
        print()

    # Failed cases summary
    failed_cases = [r for r in results if r["metrics"]["llm_judge"]["pass"] is False]
    if failed_cases:
        print(f"Failed cases ({len(failed_cases)}):")
        for r in failed_cases:
            rationale = r["metrics"]["llm_judge"].get("rationale", "")
            print(f"  [{r['id']}] {rationale[:100]}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Analyze an evaluation run")
    parser.add_argument("--run", required=True, help="Path to run JSONL file")
    parser.add_argument(
        "--failed-metric",
        metavar="METRIC",
        help="Show only cases where this metric failed (e.g. llm_judge)",
    )
    args = parser.parse_args()

    analyze(Path(args.run), failed_metric=args.failed_metric)


if __name__ == "__main__":
    main()
