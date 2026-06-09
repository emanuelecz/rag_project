import json
import os
import asyncio

import anthropic
from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from backend.services.generate import stream_answer

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

REGULATIONS_PATH = os.environ.get("REGULATIONS_PATH", "ntp_regulations")

_suggestions_cache: dict | None = None


def _generate_suggestions() -> dict:
    from backend.services.chunking import get_vectorstore

    vs = get_vectorstore()
    result = vs.get(include=["documents", "metadatas"])

    if not result["documents"]:
        return {"es": [], "en": []}

    seen: dict[str, str] = {}
    for doc, meta in zip(result["documents"], result["metadatas"]):
        src = meta.get("source", "unknown")
        if src not in seen:
            seen[src] = doc[:400]

    excerpts = "\n\n".join(
        f"Document: {src}\nExcerpt: {text}"
        for src, text in list(seen.items())[:8]
    )

    prompt = f"""You are helping build a RAG chatbot about workplace safety regulations.
Based on the documents below, generate exactly 4 suggested questions a user might ask.

{excerpts}

Return ONLY a JSON object — no explanation, no markdown fences — with this exact structure:
{{
  "es": [
    {{"icon": "<icon>", "q": "<question in Spanish>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in Spanish>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in Spanish>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in Spanish>", "tag": "<short document ref>"}}
  ],
  "en": [
    {{"icon": "<icon>", "q": "<question in English>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in English>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in English>", "tag": "<short document ref>"}},
    {{"icon": "<icon>", "q": "<question in English>", "tag": "<short document ref>"}}
  ]
}}

Icon must be one of: hardhat, scaffold, excavation, crane, book
- hardhat: PPE, personal protective equipment, safety gear
- scaffold: scaffolding, platforms, work at height
- excavation: excavations, trenches, earthwork
- crane: lifting, cranes, hoisting
- book: general regulations, procedures, rules

The "tag" should be a short reference like "NTP 670 · Andamios" or "RD 1627/1997"."""

    client = anthropic.Anthropic()
    message = client.messages.create(
        model=os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = message.content[0].text.strip()
    return json.loads(raw)


class QuestionRequest(BaseModel):
    question: str
    candidates: int = 20
    top_k: int = 8
    lang: str = "es"


@app.post("/ask")
async def ask(req: QuestionRequest):
    async def event_stream():
        async for event in stream_answer(req.question, req.candidates, req.top_k, req.lang):
            yield f"data: {json.dumps(event)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    return StreamingResponse(event_stream(), media_type="text/event-stream")


@app.get("/suggestions")
async def suggestions():
    global _suggestions_cache
    if _suggestions_cache is not None:
        return _suggestions_cache
    try:
        data = await asyncio.to_thread(_generate_suggestions)
        _suggestions_cache = data
        return data
    except Exception:
        return {"es": [], "en": []}


@app.post("/ingest")
async def ingest():
    global _suggestions_cache
    from backend.services.ingestion import ingest_folder
    from backend.services.chunking import chunk_and_ingest_docs

    docs = await asyncio.to_thread(ingest_folder, REGULATIONS_PATH)
    n    = await asyncio.to_thread(chunk_and_ingest_docs, docs)
    _suggestions_cache = None  # invalidate so next /suggestions call regenerates
    return {"status": "ok", "chunks_stored": n}


@app.get("/health")
async def health():
    return {"status": "ok"}
