import os

def get_filename(path:str):
    if not path:
        return ""
    return os.path.basename(path)
    
def evaluate_one_question(retrieved_docs, k, question_item):
    top_k_docs = retrieved_docs[:k]
    
    relevant_sources = set()
    for filename in question_item.get("relevant_sources", []):
        relevant_sources.add(get_filename(filename))

    relevant_filenames = []
    is_relevant_list = []
    for doc in top_k_docs:
        source = ""
        if doc.metadata:
            source = doc.metadata.get("source", "")
        filename = get_filename(source)
        relevant_filenames.append(filename)
        is_relevant_list.append(filename in relevant_sources)
        
    hit = 0
    if any(is_relevant_list):
        hit = 1

    relevant_count = sum(is_relevant_list)
    precision_at_k = 0.0
    if k > 0: 
        precision_at_k = relevant_count / k
    
    reciprocal_rank = 0
    position = 1
    for is_rel in is_relevant_list:
        if is_rel:
            reciprocal_rank = 1.0 / position
            break
        position = position + 1
        
    return {
        "question_id": question_item["id"],
        "question": question_item["question"],
        "k": k,
        "hit": hit,
        "precision_at_k": precision_at_k,
        "reciprocal_rank": reciprocal_rank,
        "retrieved_sources": relevant_filenames,
        "relevant_sources": sorted(relevant_sources),
    }
    


def aggregate_results(per_question_results):
    
    n = len(per_question_results)
    
    if n == 0:
        return {
            "k": 0,
            "n_questions": 0,
            "hit_rate": 0.0,
            "mean_precision": 0.0,
            "mrr": 0.0,
        }
        
    total_hits = 0.0
    total_precision = 0.0
    total_rr = 0.0
    for row in per_question_results:
        total_hits = total_hits + row["hit"]
        total_precision = total_precision + row["precision_at_k"]
        total_rr = total_rr + row["reciprocal_rank"]
        
    return {
        "k": per_question_results[0]["k"],
        "n_questions": n,
        "hit_rate": total_hits / n,        
        "mean_precision": total_precision / n,
        "mrr": total_rr / n,
    }