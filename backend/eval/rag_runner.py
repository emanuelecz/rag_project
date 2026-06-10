import json
import os
from backend.services.generate import generate_answer
from backend.services.retrieval import retrieve_documents

_DIR = os.path.join(os.path.dirname(__file__), "data")

def build_results(dataset_path=os.path.join(_DIR, "dataset.json"), out_path=os.path.join(_DIR, "dataset.json")):
    with open(dataset_path, encoding="utf-8") as f:
        dataset = json.load(f)
        
        results = []
        for row in dataset:
            chunks = retrieve_documents(row["question"])
            answer = generate_answer(row["question"], chunks)

            results.append({
                **row,
                "retrieved_context": "\n\n".join(c.page_content for c in chunks),
                "retrieved_sources": [c.metadata.get("source") for c in chunks],
                "generated_answer": answer
            })
            print(f" built {row['id']}")
            
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
        print(f" wrote {len(results)} rows to {out_path}")
        
if __name__ == "__main__":
    build_results()