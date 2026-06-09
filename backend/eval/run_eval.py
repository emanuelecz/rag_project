import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from backend.services.retrieval import retrieve_documents
from backend.services.generate import generate_answer
from backend.eval.retrieval_eval import evaluate_one_question, aggregate_results
from backend.eval.judge import judge_answer, aggregate_judgments, compute_classifier_metrics

DATASET_PATH      = Path(__file__).parent / "dataset.json"
HUMAN_LABELS_PATH = Path(__file__).parent / "human_labels.json"
RESULTS_PATH      = Path(__file__).parent / "results.json"
K = 8


def run():
    dataset      = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    labels_doc   = json.loads(HUMAN_LABELS_PATH.read_text(encoding="utf-8"))
    human_labels = {k: v for k, v in labels_doc["labels"].items() if v is not None}
    threshold    = labels_doc.get("threshold", 3.5)
    total        = len(dataset)

    retrieval_rows = []
    judge_rows     = []

    for i, item in enumerate(dataset, 1):
        print(f"[{i}/{total}] {item['id']} — {item['question'][:70]}")

        docs   = retrieve_documents(item["question"], candidates=20, top_k=K)
        result = generate_answer(item["question"], documents=docs)

        retrieval_rows.append(evaluate_one_question(docs, K, item))
        judge_rows.append(judge_answer(
            question_id=item["id"],
            question=item["question"],
            context=result["context"],
            reference_answer=item["reference_answer"],
            candidate_answer=result["answer"],
        ))

    retrieval_summary  = aggregate_results(retrieval_rows)
    judge_summary      = aggregate_judgments(judge_rows)
    classifier_metrics = compute_classifier_metrics(judge_rows, human_labels, threshold)

    per_question = []
    for r, j in zip(retrieval_rows, judge_rows):
        merged = dict(r)
        merged.update({
            "faithfulness": j["faithfulness"],
            "relevance":    j["relevance"],
            "completeness": j["completeness"],
            "overall":      j["overall"],
            "verdict":      j["verdict"],
            "faults":       j["faults"],
            "rationale":    j["rationale"],
        })
        per_question.append(merged)

    print(f"\n── Retrieval (k={K}) {'─' * 35}")
    print(f"  hit@{K}:          {retrieval_summary['hit_rate']:.3f}")
    print(f"  precision@{K}:    {retrieval_summary['mean_precision']:.3f}")
    print(f"  MRR:             {retrieval_summary['mrr']:.3f}")

    print(f"\n── Generation (LLM Judge) {'─' * 27}")
    print(f"  faithfulness:    {judge_summary['faithfulness']:.2f} / 5")
    print(f"  relevance:       {judge_summary['relevance']:.2f} / 5")
    print(f"  completeness:    {judge_summary['completeness']:.2f} / 5")
    print(f"  overall:         {judge_summary['overall']:.2f} / 5")
    print(f"  pass rate:       {judge_summary['pass_rate']:.2f}")

    if classifier_metrics:
        cm = classifier_metrics
        tpr = f"{cm['tpr']:.2f}" if cm["tpr"] is not None else "n/a"
        tnr = f"{cm['tnr']:.2f}" if cm["tnr"] is not None else "n/a"
        print(f"\n── Judge vs Human (verdict-based) {'─' * 19}")
        print(f"  accuracy:        {cm['accuracy']:.2f}")
        print(f"  TPR:             {tpr}")
        print(f"  TNR:             {tnr}")
        print(f"  TP/TN/FP/FN:     {cm['tp']} / {cm['tn']} / {cm['fp']} / {cm['fn']}")
        print(f"  (threshold={threshold} kept in detail for secondary diagnostics)")

    output = {
        "retrieval":    retrieval_summary,
        "generation":   judge_summary,
        "classifier":   classifier_metrics,
        "per_question": per_question,
    }
    RESULTS_PATH.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\nSaved → {RESULTS_PATH}")


if __name__ == "__main__":
    run()
