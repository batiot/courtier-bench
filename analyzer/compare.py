"""Compare two evaluation run JSONL files."""
from __future__ import annotations

import argparse
import json
import sys
from collections import defaultdict
from pathlib import Path


def load_run(run_path: Path) -> dict[str, dict]:
    """Load a run file into a dict keyed by case id."""
    cases: dict[str, dict] = {}
    skipped = 0
    with open(run_path) as f:
        for i, line in enumerate(f, 1):
            line = line.strip()
            if not line:
                continue
            try:
                r = json.loads(line)
                cases[r["id"]] = r
            except (json.JSONDecodeError, KeyError) as e:
                print(f"WARNING: skipping line {i} in {run_path.name}: {e}", file=sys.stderr)
                skipped += 1
    if skipped:
        print(f"WARNING: {skipped} line(s) skipped in {run_path.name}", file=sys.stderr)
    return cases


def get_pass(case: dict) -> bool | None:
    return case["metrics"]["llm_judge"]["pass"]


def pass_rate(cases: list[dict]) -> tuple[int, int]:
    passed = sum(1 for r in cases if get_pass(r) is True)
    return passed, len(cases)


def compare(run_a_path: Path, run_b_path: Path) -> None:
    run_a = load_run(run_a_path)
    run_b = load_run(run_b_path)

    ids_a = set(run_a)
    ids_b = set(run_b)
    common = ids_a & ids_b
    only_in_a = ids_a - ids_b
    only_in_b = ids_b - ids_a

    print(f"Run A: {run_a_path.name} ({len(run_a)} cases)")
    print(f"Run B: {run_b_path.name} ({len(run_b)} cases)")
    print()

    if only_in_a:
        print(f"Cases only in A ({len(only_in_a)}): {', '.join(sorted(only_in_a))}")
    if only_in_b:
        print(f"Cases only in B ({len(only_in_b)}): {', '.join(sorted(only_in_b))}")
    if only_in_a or only_in_b:
        print()

    # Global pass rates
    p_a, t_a = pass_rate(list(run_a.values()))
    p_b, t_b = pass_rate(list(run_b.values()))
    pct_a = round(100 * p_a / t_a) if t_a else 0
    pct_b = round(100 * p_b / t_b) if t_b else 0
    delta = pct_b - pct_a
    delta_str = f"+{delta}%" if delta > 0 else f"{delta}%"
    print(f"=== Global pass rate ===")
    print(f"  A: {p_a}/{t_a} ({pct_a}%)")
    print(f"  B: {p_b}/{t_b} ({pct_b}%)  [{delta_str}]")
    print()

    # Status changes on common cases
    pass_to_fail = []
    fail_to_pass = []
    for case_id in sorted(common):
        pa = get_pass(run_a[case_id])
        pb = get_pass(run_b[case_id])
        if pa is True and pb is False:
            pass_to_fail.append(case_id)
        elif pa is False and pb is True:
            fail_to_pass.append(case_id)

    print(f"=== Status changes (on {len(common)} common cases) ===")
    if not pass_to_fail and not fail_to_pass:
        print("  No changes in verdict")
    if fail_to_pass:
        print(f"\n  FAIL → PASS ({len(fail_to_pass)} cases) ✓")
        for cid in fail_to_pass:
            r_b = run_b[cid]["metrics"]["llm_judge"].get("rationale", "")
            print(f"    [{cid}] {r_b[:100]}")
    if pass_to_fail:
        print(f"\n  PASS → FAIL ({len(pass_to_fail)} cases) ✗")
        for cid in pass_to_fail:
            r_b = run_b[cid]["metrics"]["llm_judge"].get("rationale", "")
            print(f"    [{cid}] {r_b[:100]}")

    # By dimension breakdown
    print()
    print("=== By scenario family ===")
    families = sorted({r.get("scenario_family") or "unknown" for r in list(run_a.values()) + list(run_b.values())})
    for fam in families:
        cases_a = [r for r in run_a.values() if (r.get("scenario_family") or "unknown") == fam]
        cases_b = [r for r in run_b.values() if (r.get("scenario_family") or "unknown") == fam]
        if not cases_a and not cases_b:
            continue
        pa, ta = pass_rate(cases_a)
        pb, tb = pass_rate(cases_b)
        pct_fa = round(100 * pa / ta) if ta else 0
        pct_fb = round(100 * pb / tb) if tb else 0
        d = pct_fb - pct_fa
        d_str = f"+{d}%" if d > 0 else f"{d}%"
        print(f"  {fam:<20} A:{pct_fa}%  B:{pct_fb}%  [{d_str}]")


def main() -> None:
    parser = argparse.ArgumentParser(description="Compare two evaluation runs")
    parser.add_argument("--run-a", required=True, help="Path to run A JSONL file")
    parser.add_argument("--run-b", required=True, help="Path to run B JSONL file")
    args = parser.parse_args()

    compare(Path(args.run_a), Path(args.run_b))


if __name__ == "__main__":
    main()
