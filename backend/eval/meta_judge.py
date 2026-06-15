import time
from typing import Literal
from dotenv import load_dotenv
from openai import OpenAI, RateLimitError
from pydantic import BaseModel, Field

load_dotenv()
client = OpenAI()

class JudgeVerdict(BaseModel):
    chain_of_thought: str = Field(description="Step-by-step reasoning. MUST be written before the score.")
    score:Literal[0,1] = Field(description="1 = pass, 0 = fail")

def _run(prompt: str) -> JudgeVerdict:
    for attempt in range(5):
        try:
            resp = client.beta.chat.completions.parse(
                model="gpt-4o",
                temperature=0.0,
                messages=[{"role": "user", "content": prompt}],
                response_format=JudgeVerdict,
            )
            return resp.choices[0].message.parsed
        except RateLimitError:
            if attempt == 4:
                raise
            wait = 2 ** attempt * 5
            print(f" [rate limit, retrying in {wait}s]", end="", flush=True)
            time.sleep(wait)

def judge_faithfulness(context: str, answer: str) -> JudgeVerdict:
    return _run(f"""
    You are an expert auditor of Spanish construction-safety regulations (NTP).
    Judge ONLY whether every claim in the Answer is supported by the Context.
    Do NOT use outside knowledge.

    A claim FAILS if either:
    (a) it is ABSENT from the Context (added fact/number not present), OR
    (b) it CONTRADICTS the Context — including subtle changes to numbers,
        units, quantities, or qualifiers (e.g. "una simple maniobra" vs
        "varias maniobras", "6 meses" vs "12 meses", "2,50 m" vs "2,00 m").

    Method — do this BEFORE scoring:
    1. Break the Answer into individual atomic claims.
    2. For EACH claim, quote the exact supporting phrase from the Context,
       or state that no matching phrase exists / the phrase differs.
    3. If any claim has no exact match OR conflicts with its match, the
       overall score is 0.

    [Context]
    {context}

    [Answer]
    {answer}

    Rubric:
    1 (Pass): every claim — including every number, unit and qualifier —
              matches the Context exactly.
    0 (Fail): any claim is absent from or contradicts the Context.

    Write chain_of_thought BEFORE the score.
    """)
    
def judge_relevance(question: str, answer: str) -> JudgeVerdict:
    return _run(f"""
    You are an expert auditor. Judge ONLY whether the Answer addresses the Question.
    Ignore whether it is factually correct — only whether it is on-topic.

    Method — do this BEFORE scoring:
    1. Identify the SPECIFIC thing the Question is asking for (a number, a procedure, a list
       of named items, a definition, etc.).
    2. Check whether the Answer actually provides that specific thing.
    3. An answer that discusses a RELATED but DIFFERENT sub-topic (e.g. asks for distance X
       but answer gives distance Y for a different scenario) counts as 0 — it is not enough
       to be broadly on the same subject.

    [Question]
    {question}

    [Answer]
    {answer}

    Rubric:
    1 (Pass): directly and specifically resolves what the Question asks for.
    0 (Fail): off-topic, dodges the question, restates it, or answers a related but
              different sub-question.

    Write chain_of_thought BEFORE the score.
    """)
    

def judge_completeness(reference_answer: str, answer: str)-> JudgeVerdict:
    return _run(f"""
    You are an expert auditor. Compare the Answer to the Reference (gold) Answer.
    Judge ONLY whether every key fact from the Reference is PRESENT somewhere in the
    Answer. Do NOT penalise the Answer for also containing extra or wrong information —
    that is a separate faithfulness concern, not completeness.

    Method — do this BEFORE scoring:
    1. Extract every KEY FACT from the Reference: numeric thresholds, distances, forces,
       voltages, percentages, named items, named procedures, AND the regulatory codes
       it explicitly cites (RD, NTP, UNE numbers).
    2. For EACH key fact, check whether it appears ANYWHERE in the Answer with the
       correct value — including inside a quotation. If the correct value appears
       anywhere, that fact is covered, EVEN IF the Answer also states a different
       (wrong) value elsewhere.
    3. The Answer is complete only if EVERY reference key fact is present. If even one
       key fact (a number, named item, or cited regulatory code) is missing, it fails.

    [Reference Answer]
    {reference_answer}

    [Answer]
    {answer}

    Rubric:
    1 (Pass): every key fact from the Reference — including each cited regulatory code —
              appears somewhere in the Answer with the correct value.
    0 (Fail): one or more reference key facts are absent from the Answer (the correct
              value never appears anywhere).

    Write chain_of_thought BEFORE the score.
    """)