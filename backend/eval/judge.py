import anthropic
import os

JUDGE_MODEL = os.environ.get("EVAL_JUDGE_MODEL", "claude-haiku-4-5-20251001")

GRADE_TOOL = {
    "name": "grade_answer",
    "description": "Grade the candidate answer and return structured evaluation results.",
    "input_schema": {
        "type": "object",
        "properties": {
            "faults": {
                "type": "array",
                "items": {"type": "string"},
                "description": (
                    "List of faults found. Prefix each with its category: "
                    "NOT_SUPPORTED, CONTRADICTS_REFERENCE, or MISSING_FACT. "
                    "Empty list if none."
                ),
            },
            "faithfulness": {
                "type": "integer",
                "description": "Faithfulness score 1–5.",
                "minimum": 1,
                "maximum": 5,
            },
            "relevance": {
                "type": "integer",
                "description": "Relevance score 1–5.",
                "minimum": 1,
                "maximum": 5,
            },
            "completeness": {
                "type": "integer",
                "description": "Completeness score 1–5.",
                "minimum": 1,
                "maximum": 5,
            },
            "verdict": {
                "type": "string",
                "enum": ["pass", "fail"],
                "description": (
                    "pass iff the answer is consistent with the reference AND grounded in "
                    "the sources AND has no material errors or omissions. Otherwise fail. "
                    "This is a direct judgment — do not derive it from the numeric scores."
                ),
            },
            "rationale": {
                "type": "string",
                "description": "One or two sentences explaining the verdict.",
            },
        },
        "required": [
            "faults",
            "faithfulness",
            "relevance",
            "completeness",
            "verdict",
            "rationale",
        ],
    },
}

SYSTEM_PROMPT = """You are a strict evaluator of answers from a RAG system about Spanish construction safety regulations (NTP).

You receive: a QUESTION, the RETRIEVED SOURCES the system had access to, a REFERENCE ANSWER (ground truth), and a CANDIDATE ANSWER to grade.

## Step 1 — Fault analysis (mandatory, comes before any score)

List every fault under these categories:
- NOT_SUPPORTED: a claim in the candidate that cannot be traced to the retrieved sources
- CONTRADICTS_REFERENCE: a claim that directly contradicts the reference answer
- MISSING_FACT: a key fact present in the reference that is absent from the candidate

If the answer is perfect, return an empty list. Do not skip this step.

## Step 2 — Score on three dimensions (integer 1–5 each)

**faithfulness** (are all claims grounded in the retrieved sources?)
  1 = actively contradicts sources or invents facts not present in them
  2 = several claims unsupported by sources
  3 = mostly grounded but 1–2 unsupported claims slip through
  4 = one minor unsupported detail
  5 = every claim is directly traceable to the sources

**relevance** (does the answer address ALL aspects of the question?)
  1 = entirely off-topic or answers a different question
  2 = addresses only a minor part; the main ask is ignored
  3 = addresses part of the question but omits one key aspect
  4 = almost complete; one minor aspect not addressed
  5 = directly and fully addresses every aspect of the question

**completeness** (what fraction of the reference answer's key facts appear correctly?)
  Enumerate specific numbers, thresholds, distances, voltages, regulatory codes,
  named standards, conditions, and named items in the reference. Score by fraction covered:
  1 = fewer than 20% of key facts present
  2 = 20–39% of key facts present
  3 = 40–59% of key facts present
  4 = 60–79% of key facts present
  5 = 80%+ of key facts present
  Hard rule: if the reference contains ≥2 distinct required values and the candidate provides only one, completeness MUST be ≤ 2.

## Step 3 — Binary verdict

Decide **pass** iff all three are true:
  1. The candidate is consistent with the reference (no contradictions, no material omissions).
  2. The candidate is grounded in the retrieved sources (no invented facts).
  3. There are no material errors.
Otherwise decide **fail**. This is a direct judgment — do not derive it arithmetically from the scores.

## Few-shot examples

### Example A — bad answer, fail
QUESTION: What minimum distance must be maintained from overhead power lines when using a crane?
REFERENCE ANSWER: A minimum safety distance of 5 m must be maintained for lines up to 66 kV, and 7 m for lines above 66 kV, per NTP 072.
CANDIDATE ANSWER: You need to keep a safe distance from power lines when operating cranes near electrical hazards.

faults:
- MISSING_FACT: No distance specified (5 m / 7 m)
- MISSING_FACT: Voltage thresholds (66 kV) not mentioned
- MISSING_FACT: NTP 072 not cited
faithfulness: 4
relevance: 2
completeness: 1
verdict: fail
rationale: The candidate gives only a generic reminder. It omits all quantitative requirements from the reference and therefore provides no actionable guidance.

### Example B — bad answer, fail
QUESTION: What PPE is required when working at heights above 2 m?
REFERENCE ANSWER: Workers must use a full-body harness anchored to a certified anchor point, and a helmet, per NTP 124. The lanyard must limit the free fall to ≤ 1 m.
CANDIDATE ANSWER: A safety helmet is required when working at heights.

faults:
- MISSING_FACT: Full-body harness not mentioned
- MISSING_FACT: Anchor point requirement omitted
- MISSING_FACT: Lanyard / free-fall limit (≤ 1 m) omitted
- MISSING_FACT: NTP 124 not cited
faithfulness: 5
relevance: 3
completeness: 1
verdict: fail
rationale: Only the helmet is mentioned. Harness, anchor point, and fall-arrest limits are all absent, making the answer materially incomplete.

### Example C — good answer, pass
QUESTION: What minimum distance must be maintained from overhead power lines when using a crane?
REFERENCE ANSWER: A minimum safety distance of 5 m must be maintained for lines up to 66 kV, and 7 m for lines above 66 kV, per NTP 072.
CANDIDATE ANSWER: According to NTP 072, crane operators must keep at least 5 m from power lines up to 66 kV and at least 7 m from lines exceeding 66 kV.

faults: []
faithfulness: 5
relevance: 5
completeness: 5
verdict: pass
rationale: The candidate correctly states both distance thresholds and cites the correct NTP standard."""

HUMAN_TEMPLATE = """QUESTION:
{question}

RETRIEVED SOURCES (what the RAG system had access to):
{retrieved_context}

REFERENCE ANSWER (ground truth):
{reference_answer}

CANDIDATE ANSWER (the one being graded):
{ai_answer}

Analyse faults first, then score each dimension, then set the verdict."""


def clamp_score(value):
    v = int(value)
    return max(1, min(5, v))


def _invoke(client, model, question, ai_answer, reference_answer, retrieved_context):
    response = client.messages.create(
        model=model,
        temperature=0,
        max_tokens=1024,
        system=SYSTEM_PROMPT,
        tools=[GRADE_TOOL],
        tool_choice={"type": "tool", "name": "grade_answer"},
        messages=[
            {
                "role": "user",
                "content": HUMAN_TEMPLATE.format(
                    question=question,
                    retrieved_context=retrieved_context,
                    reference_answer=reference_answer,
                    ai_answer=ai_answer,
                ),
            }
        ],
    )
    for block in response.content:
        if block.type == "tool_use" and block.name == "grade_answer":
            return block.input
    raise ValueError(
        "Judge did not call grade_answer tool. Raw content: " + str(response.content)
    )


def judge_one(question, ai_answer, reference_answer, retrieved_context, client, model):
    """Grade a single answer.

    Returns a judge_row dict with fields: question, faithfulness, relevance,
    completeness, overall, verdict (1=pass / 0=fail), faults, rationale.
    """
    try:
        data = _invoke(client, model, question, ai_answer, reference_answer, retrieved_context)
    except Exception:
        data = _invoke(client, model, question, ai_answer, reference_answer, retrieved_context)

    faithfulness = clamp_score(data["faithfulness"])
    relevance = clamp_score(data["relevance"])
    completeness = clamp_score(data["completeness"])
    overall = (faithfulness + relevance + completeness) / 3.0

    verdict_str = data.get("verdict", "fail")
    if verdict_str not in ("pass", "fail"):
        verdict_str = "fail"
    verdict = 1 if verdict_str == "pass" else 0

    faults = data.get("faults", [])
    if not isinstance(faults, list):
        faults = []

    rationale = str(data.get("rationale", "")).strip()

    return {
        "question": question,
        "faithfulness": faithfulness,
        "relevance": relevance,
        "completeness": completeness,
        "overall": overall,
        "verdict": verdict,
        "faults": faults,
        "rationale": rationale,
    }


def judge_answer(question_id, question, context, reference_answer, candidate_answer):
    """Convenience wrapper that constructs an Anthropic client and delegates to judge_one."""
    client = anthropic.Anthropic()
    row = judge_one(
        question=question,
        ai_answer=candidate_answer,
        reference_answer=reference_answer,
        retrieved_context=context,
        client=client,
        model=JUDGE_MODEL,
    )
    row["question_id"] = question_id
    return row


def compute_classifier_metrics(judge_rows, human_labels, threshold=3.5):
    tp = tn = fp = fn = 0
    detail = []

    for row in judge_rows:
        qid = str(row["question_id"])
        human_label = human_labels.get(qid)
        if human_label is None:
            continue

        human_good = bool(human_label)
        judge_good = bool(row["verdict"])
        judge_good_threshold = row["overall"] >= threshold

        if human_good and judge_good:
            tp += 1
            outcome = "TP"
        elif not human_good and not judge_good:
            tn += 1
            outcome = "TN"
        elif not human_good and judge_good:
            fp += 1
            outcome = "FP"
        else:
            fn += 1
            outcome = "FN"

        detail.append({
            "question_id": qid,
            "question": row["question"],
            "overall": round(row["overall"], 2),
            "verdict": row["verdict"],
            "judge_good": judge_good,
            "judge_good_threshold": judge_good_threshold,
            "human_good": human_good,
            "outcome": outcome,
            "faults": row.get("faults", []),
        })

    n = tp + tn + fp + fn
    if n == 0:
        return None

    tpr = tp / (tp + fn) if (tp + fn) > 0 else None
    tnr = tn / (tn + fp) if (tn + fp) > 0 else None
    accuracy = (tp + tn) / n

    return {
        "threshold": threshold,
        "n_labeled": n,
        "tp": tp,
        "tn": tn,
        "fp": fp,
        "fn": fn,
        "tpr": tpr,
        "tnr": tnr,
        "accuracy": accuracy,
        "detail": detail,
    }


def aggregate_judgments(judge_results):
    n = len(judge_results)
    if n == 0:
        return {
            "n_questions": 0,
            "faithfulness": 0.0,
            "relevance": 0.0,
            "completeness": 0.0,
            "overall": 0.0,
            "pass_rate": 0.0,
        }

    total_f = total_r = total_c = total_o = 0.0
    total_verdict = 0
    for row in judge_results:
        total_f += row["faithfulness"]
        total_r += row["relevance"]
        total_c += row["completeness"]
        total_o += row["overall"]
        total_verdict += row["verdict"]

    return {
        "n_questions": n,
        "faithfulness": total_f / n,
        "relevance": total_r / n,
        "completeness": total_c / n,
        "overall": total_o / n,
        "pass_rate": total_verdict / n,
    }
