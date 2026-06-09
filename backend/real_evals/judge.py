from typing import Literal
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from openai import OpenAI

load_dotenv()
client = OpenAI()

class JudgeVerdict(BaseModel):
    chain_of_thought: str = Field(description="Step-by-step reasoning. MUST be written before the score.")
    score:Literal[0,1] = Field(description="1 = pass, 0 = fail")
    
def _run(prompt:str) -> JudgeVerdict:
    resp = client.beta.chat.completions.parse(
        model="gpt-4o",
        temperature=0.0,
        messages=[{"role": "user", "content": prompt}],
        response_format=JudgeVerdict
    )
    return resp.choices[0].message.parsed

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

    [Question]
    {question}

    [Answer]
    {answer}

    Rubric:
    1 (Pass): directly resolves the core intent of the Question.
    0 (Fail): off-topic, dodges the question, or just restates it.

    Write chain_of_thought BEFORE the score.
    """)
    

def judge_completeness(reference_answer: str, answer: str)-> JudgeVerdict:
    return _run(f"""
    You are an expert auditor. Compare the Answer to the Reference (gold) Answer.
    Judge whether the Answer covers the key points present in the Reference.

    [Reference Answer]
    {reference_answer}

    [Answer]
    {answer}

    Rubric:
    1 (Pass): covers all essential points of the Reference (extra detail is fine).
    0 (Fail): omits one or more essential points of the Reference.

    Write chain_of_thought BEFORE the score.
    """)