import json
from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent / ".env")

from backend.services.retrieval import retrieve_documents
from backend.services.generate import generate_answer

DATASET_PATH = Path(__file__).parent / "dataset.json"
LABELS_PATH  = Path(__file__).parent / "human_labels.json"


def save(labels_doc: dict):
    LABELS_PATH.write_text(json.dumps(labels_doc, indent=2, ensure_ascii=False), encoding="utf-8")


def run():
    dataset    = json.loads(DATASET_PATH.read_text(encoding="utf-8"))
    labels_doc = json.loads(LABELS_PATH.read_text(encoding="utf-8"))
    labels     = labels_doc["labels"]

    pending = [item for item in dataset if labels.get(item["id"]) is None]

    if not pending:
        print("All questions are already labeled.")
        return

    total   = len(labels)
    done    = total - len(pending)
    print(f"Progress: {done}/{total} labeled — {len(pending)} remaining.")
    print("Answer 1 = good  |  0 = bad  |  s = skip  |  q = quit\n")

    for item in pending:
        qid = item["id"]
        print(f"\n{'─' * 60}")
        print(f"[{qid}]  {item['question']}\n")

        print("  retrieving…")
        docs   = retrieve_documents(item["question"], candidates=20, top_k=8)
        result = generate_answer(item["question"], documents=docs)

        print(f"\n{result['answer']}\n")
        print("Sources: " + " | ".join(result["sources"]))

        while True:
            raw = input("\nGrade (1/0/s/q): ").strip().lower()
            if raw in ("1", "0"):
                labels[qid] = int(raw)
                save(labels_doc)
                break
            if raw == "s":
                break
            if raw == "q":
                print("Saved. Resuming next time from where you left off.")
                return
            print("  type 1, 0, s, or q")

    labeled = sum(1 for v in labels.values() if v is not None)
    print(f"\nDone — {labeled}/{total} labeled.")


if __name__ == "__main__":
    run()
