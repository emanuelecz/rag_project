import json, sys
from pathlib import Path

RESULTS_PATH = Path(__file__).parent / "data" / "results.json"

GATES = [
    ("retrieval.hit_rate",       lambda r: r["retrieval"]["hit_rate"],      0.90),
    ("retrieval.mrr",            lambda r: r["retrieval"]["mrr"],            0.85),
    ("generation.pass_rate",     lambda r: r["generation"]["pass_rate"],     0.80),
    ("generation.overall",       lambda r: r["generation"]["overall"],       4.50),
    ("generation.faithfulness",  lambda r: r["generation"]["faithfulness"],  4.50),
    ("generation.relevance",     lambda r: r["generation"]["relevance"],     4.50),
    ("generation.completeness",  lambda r: r["generation"]["completeness"],  4.25),
]


def main():
    if not RESULTS_PATH.exists():
        print("ERROR: results.json not found — run `python -m backend.eval.run_eval` before pushing.")
        sys.exit(1)

    results = json.loads(RESULTS_PATH.read_text(encoding="utf-8"))
    all_passed = True

    print("── Eval Quality Gates ──────────────────────────────────────────")
    for name, getter, threshold in GATES:
        value = getter(results)
        ok = value >= threshold
        status = "PASS" if ok else "FAIL"
        print(f"  {status}  {name:<35}  {value:.3f}  (min {threshold})")
        if not ok:
            all_passed = False

    print()
    if all_passed:
        print("All gates passed.")
    else:
        print("One or more gates failed — run eval and update results.json.")

    sys.exit(0 if all_passed else 1)


if __name__ == "__main__":
    main()
