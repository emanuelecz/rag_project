import sys, json
from real_evals.judge import judge_completeness, judge_faithfulness, judge_relevance

TARGET = 0.85
DIMENSIONS = ["faithfulness", "relevance", "completeness"]

def confusion(pairs):
    tp = sum(1 for h,j in pairs if h == 1 and j == 1)
    tn = sum(1 for h,j in pairs if h == 0 and j == 0)
    fp = sum(1 for h,j in pairs if h == 0 and j == 1)
    fn = sum(1 for h,j in pairs if h == 1 and j == 0)
    has_pos = (tp + fn) > 0
    has_neg = (tn + fp) > 0
    return {
        "tp": tp, "tn": tn, "fp": fp, "fn": fn,
        "tpr": tp / (tp + fn) if has_pos else None,
        "tnr": tn / (tn + fp) if has_neg else None,
        "has_pos": has_pos, "has_neg": has_neg
    }
    
def gate(name, m):
    print(f"\n📊 {name.upper()}")
    print(f"  TP {m['tp']}  TN {m['tn']}  FP {m['fp']}  FN {m['fn']}")
    tpr_str = f"{m['tpr']*100:.1f}%" if m['tpr'] is not None else "N/A (no positives)"
    tnr_str = f"{m['tnr']*100:.1f}%" if m['tnr'] is not None else "N/A (no negatives)"
    print(f"  TPR: {tpr_str}")
    print(f"  TNR: {tnr_str}")

    passed = True
    if not m["has_pos"]:
        print("  ⚠️ GAP: no positive examples — add some."); passed = False
    elif m["tpr"] < TARGET:
        print(f"  ⚠️ Low TPR — judge too harsh."); passed = False
    if not m["has_neg"]:
        print("  ⚠️ GAP: no negative examples — add some."); passed = False
    elif m["tnr"] < TARGET:
        print(f"  ⚠️ Low TNR — judge too lenient (misses hallucinations)."); passed = False
    if passed:
        print(f"  🚀 PASS (≥{TARGET*100:.0f}%)")
    return passed

def _judge(r):
    return {
        "faithfulness": judge_faithfulness(r["retrieved_context"], r["generated_answer"]),
        "relevance":    judge_relevance(r["question"], r["generated_answer"]),
        "completeness": judge_completeness(r["reference_answer"], r["generated_answer"]),
    }

def run_meta_eval():
    import os
    results = {r["id"]: r for r in json.load(open("real_evals/dataset.json", encoding="utf-8"))}
    labels  = json.load(open("real_evals/human_labels.json", encoding="utf-8"))

    adv_path = "real_evals/adversarial_negatives.json"
    adv_rows = {}
    if os.path.exists(adv_path):
        adv_rows = {r["id"]: r for r in json.load(open(adv_path, encoding="utf-8"))}

    n_real = sum(1 for lab in labels if lab["id"] not in adv_rows)
    n_adv  = sum(1 for lab in labels if lab["id"] in adv_rows)
    print(f"Loaded {n_real} real labels, {n_adv} adversarial labels ({len(labels)} total)")

    pairs = {d: [] for d in DIMENSIONS}

    for i, lab in enumerate(labels, 1):
        is_adv = lab["id"] in adv_rows
        r = adv_rows[lab["id"]] if is_adv else results[lab["id"]]
        tag = " [adv]" if is_adv else ""
        print(f"  [{i}/{len(labels)}] judging {lab['id']}{tag} ...", end=" ", flush=True)
        verdicts = _judge(r)
        scores = {d: verdicts[d].score for d in DIMENSIONS if lab.get(d) is not None}
        print("  ".join(f"{d[0].upper()}:{s}" for d, s in scores.items()))
        for d in DIMENSIONS:
            if lab.get(d) is not None:
                pairs[d].append((lab[d], verdicts[d].score))
        with open("real_evals/meta_traces.jsonl", "a", encoding="utf-8") as f:
            f.write(json.dumps({
                "id": lab["id"],
                **{d: {"human": lab.get(d), "judge": verdicts[d].score,
                       "cot": verdicts[d].chain_of_thought} for d in DIMENSIONS}
            }, ensure_ascii=False) + "\n")

    print("\n--- Results ---")
    results = [gate(d, confusion(pairs[d])) for d in DIMENSIONS]
    all_passed = all(results)
    return all_passed

if __name__ == "__main__":
    open("real_evals/meta_traces.jsonl", "w").close()
    ok = run_meta_eval()
    sys.exit(0 if ok else 1)   # nonzero exit → blocks CI if judge isn't trustworthy