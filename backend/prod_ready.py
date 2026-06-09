import os
from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()
client = OpenAI()

# ==========================================
# 1. THE STRUCTURED SCHEMAS 
# ==========================================
class FaithfulnessEval(BaseModel):
    chain_of_thought: str = Field(description="Step-by-step reasoning assessing if the answer contains any information NOT present in the context.")
    score: Literal[0, 1] = Field(description="Score 1 if completely faithful to context. Score 0 if hallucinated.")
    
class AnswerRelevanceEval(BaseModel):
    chain_of_thought: str = Field(description="Step-by-step reasoning assessing if the answer directly addresses the user's question.")
    score: Literal[0, 1] = Field(description="Score 1 if it directly answers the question. Score 0 if it avoids the question or is pure fluff.")

# ==========================================
# 2. THE JUDGE FUNCTIONS
# ==========================================
def judge_faithfulness(context: str, answer: str) -> FaithfulnessEval:
    prompt = f"""
    You are an expert legal auditor for Spanish construction laws.
    Evaluate the Faithfulness of the Assistant's Answer based ONLY on the Retrieved Context.
    
    [Retrieved Context]
    {context}
    
    [Assistant Answer]
    {answer}
    
    Rubric:
    1 (Pass): The answer is strictly derived from the context.
    0 (Fail): The answer contains claims, numbers, or facts not present in the context.
    
    You MUST output your chain_of_thought reasoning BEFORE outputting the score.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        response_format=FaithfulnessEval,
    )
    return response.choices[0].message.parsed

def judge_answer_relevance(question: str, answer: str) -> AnswerRelevanceEval:
    prompt = f"""
    You are an expert legal auditor. Evaluate the Answer Relevance.
    
    [User Question]
    {question}
    
    [Assistant Answer]
    {answer}
    
    Rubric:
    1 (Pass): The answer directly and clearly resolves the user's question.
    0 (Fail): The answer is irrelevant, misses the core intent, or just repeats the question.
    
    You MUST output your chain_of_thought reasoning BEFORE outputting the score.
    """
    response = client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        response_format=AnswerRelevanceEval,
    )
    return response.choices[0].message.parsed 

# ==========================================
# 3. THE FIXTURES (Cleanly Separated)
# ==========================================

# FIXTURE A: THE SMOKE SET
# Purpose: To deliberately force disagreements to prove our TP/TN/FP/FN math counters actually work.
smoke_set = [
    {
        "id": "Smoke_001_Forced_FP",
        "question": "¿Es obligatorio el uso de arnés?",
        "retrieved_context": "El arnés es obligatorio a partir de 2 metros.",
        "generated_answer": "Sí, el arnés es obligatorio a más de 2 metros.", 
        # The AI generated a PERFECT answer. The Judge WILL score it a 1.
        # We deliberately mislabel it as 0 to force a False Positive in our math.
        "human_faithfulness_label": 0, 
        "human_relevance_label": 0     
    },
    {
        "id": "Smoke_002_Forced_FN",
        "question": "¿De qué material debe ser el andamio?",
        "retrieved_context": "Los andamios deben ser de aluminio o acero.",
        "generated_answer": "Los andamios deben ser de madera.", 
        # The AI hallucinated. The Judge WILL score it a 0.
        # We deliberately mislabel it as 1 to force a False Negative in our math.
        "human_faithfulness_label": 1, 
        "human_relevance_label": 1     
    }
]

# FIXTURE B: THE GOLDEN SET (Production Validation)
# Purpose: Clean, perfectly labeled data to evaluate the Judge's actual readiness.
golden_set = [
    {
        "id": "Test_001_Clean_TP",
        "question": "¿Cuál es la altura mínima de las barandillas según la NTP 202?",
        "retrieved_context": "La NTP 202 exige que las barandillas tengan 90 cm de altura.",
        "generated_answer": "La altura mínima es de 90 cm según la NTP 202.", 
        "human_faithfulness_label": 1, 
        "human_relevance_label": 1     
    },
    {
        "id": "Test_002_Clean_TN",
        "question": "¿Qué zapatos debo usar en el andamio?",
        "retrieved_context": "La NTP 202 exige que las barandillas tengan 90 cm de altura.",
        "generated_answer": "Debes usar botas con punta de acero.", 
        "human_faithfulness_label": 0, # Unfaithful (Hallucination - boots not in context)
        "human_relevance_label": 1     # Relevant! (It directly answers "what shoes")
    }
]

# ==========================================
# 4. THE ORCHESTRATOR & META-EVALUATOR
# ==========================================
def calculate_and_print_metrics(results_list, eval_name, is_smoke_test=False):
    print(f"\n📊 --- REPORT: {eval_name.upper()} ---")
    
    tp = sum(1 for r in results_list if r['human'] == 1 and r['judge'] == 1)
    tn = sum(1 for r in results_list if r['human'] == 0 and r['judge'] == 0)
    fp = sum(1 for r in results_list if r['human'] == 0 and r['judge'] == 1)
    fn = sum(1 for r in results_list if r['human'] == 1 and r['judge'] == 0)
    
    tpr = tp / (tp + fn) if (tp + fn) > 0 else 0
    tnr = tn / (tn + fp) if (tn + fp) > 0 else 0
    
    print(f"True Positives (Agreed Good) : {tp}")
    print(f"True Negatives (Caught Bad)  : {tn}")
    print(f"False Positives (Disagreed)  : {fp}")
    print(f"False Negatives (Disagreed)  : {fn}")
    
    print(f"\nRate: TPR (Recall)      : {tpr * 100:.1f}%")
    print(f"Rate: TNR (Specificity) : {tnr * 100:.1f}%")
    
    # If we are just smoke testing the harness, skip the production gates
    if is_smoke_test:
        print(f"🛠️  SMOKE TEST COMPLETE: Verify FP and FN counters incremented properly.")
        return

    # THE FIXED GATE: Dual threshold at 0.85 (85%)
    TARGET = 0.85
    if tpr >= TARGET and tnr >= TARGET:
        print(f"🚀 SUCCESS: {eval_name} Judge is production-ready! (Met >85% thresholds)")
    else:
        print(f"⚠️ WARNING: {eval_name} Judge failed the {TARGET*100}% threshold.")
        if tpr < TARGET:
            print("   -> Low TPR: Judge is too harsh (penalizing good answers).")
        if tnr < TARGET:
            print("   -> Low TNR: Judge is too lenient (letting hallucinations slip).")

def run_evaluation_ecosystem(dataset, is_smoke_test=False):
    mode = "SMOKE TEST" if is_smoke_test else "GOLDEN SET (PRODUCTION)"
    print(f"\n🚀 Running Harness on: {mode}...\n")
    
    faithfulness_results = []
    relevance_results = []
    
    for item in dataset:
        print(f"Evaluating {item['id']}...")
        
        f_eval = judge_faithfulness(item["retrieved_context"], item["generated_answer"])
        faithfulness_results.append({
            "human": item["human_faithfulness_label"],
            "judge": f_eval.score
        })
        
        r_eval = judge_answer_relevance(item["question"], item["generated_answer"])
        relevance_results.append({
            "human": item["human_relevance_label"],
            "judge": r_eval.score
        })

    calculate_and_print_metrics(faithfulness_results, "Faithfulness", is_smoke_test)
    calculate_and_print_metrics(relevance_results, "Answer Relevance", is_smoke_test)

if __name__ == "__main__":
    # 1. Run the smoke test first to prove the math/harness is bulletproof
    run_evaluation_ecosystem(smoke_set, is_smoke_test=True)
    
    print("\n" + "="*50 + "\n")
    
    # 2. Run the clean golden set to actually grade the LLM judges
    run_evaluation_ecosystem(golden_set, is_smoke_test=False)