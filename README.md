# NTP Safety Assistant — RAG over Spanish Workplace Safety Regulations

A production-style **Retrieval-Augmented Generation** system that answers questions about Spanish occupational safety regulations (INSST *Notas Técnicas de Prevención*), with grounded citations, streaming responses, and a full **LLM-as-judge evaluation suite** — including a meta-evaluation that validates the judge itself against human labels.

![Python](https://img.shields.io/badge/Python-3.11-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-009688)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![TypeScript](https://img.shields.io/badge/TypeScript-3178C6)
![Docker](https://img.shields.io/badge/Docker-2496ED)
![License](https://img.shields.io/badge/License-MIT-green)

## How it works

```
PDFs (16 NTP regulations)
   │  ingestion + OCR (poppler / tesseract)
   ▼
Chunking ──► Voyage AI embeddings ──► ChromaDB
                                         │
User question ──► Hybrid retrieval (vector + BM25) ──► Voyage rerank-2.5
                                         │
                              Claude (Anthropic) ──► streamed answer + [1][2] citations
```

- **Hybrid retrieval**: dense vector search and BM25 keyword search combined in a 50/50 ensemble, then reranked with Voyage `rerank-2.5` to select the top-k chunks.
- **Grounded generation**: Claude answers strictly from retrieved context, cites sources inline, and refuses when the context is insufficient.
- **Streaming API**: answers stream token-by-token over Server-Sent Events.
- **Bilingual**: Spanish and English prompts and UI.

## Evaluation (the part most RAG demos skip)

The system is evaluated end-to-end on a 50-question dataset with human-verified reference answers ([backend/eval/](backend/eval/)):

| Metric | Result |
|---|---|
| Retrieval hit rate @8 | **0.98** |
| Retrieval MRR | **0.955** |
| Generation pass rate (LLM judge) | **0.88** |
| Faithfulness / Relevance / Completeness | 4.8 / 4.86 / 4.58 (out of 5) |

Two evaluation layers:

1. **Pipeline eval** (`run_eval.py`) — retrieval metrics (hit@k, precision@k, MRR) plus a Claude judge that scores every answer on faithfulness, relevance, and completeness with structured fault reporting (`NOT_SUPPORTED`, `CONTRADICTS_REFERENCE`, `MISSING_FACT`).
2. **Meta-eval** (`meta_eval.py`) — validates the judge itself: a second, independent GPT-4o judge is compared against human labels (including **adversarial negatives** — deliberately corrupted answers) and gated on TPR/TNR ≥ 85%, so hallucinations can't slip past an over-lenient judge. Exits non-zero on failure to block CI.

Full results: [backend/eval/data/results.json](backend/eval/data/results.json)

## Tech stack

| Layer | Technology |
|---|---|
| Backend | FastAPI, LangChain, Python 3.11 |
| LLM | Claude (Anthropic API) |
| Embeddings + reranking | Voyage AI |
| Vector store | ChromaDB |
| Eval judges | Claude + GPT-4o (structured outputs) |
| Frontend | Next.js 14, React 18, TypeScript, Tailwind CSS |
| Infra | Docker, Docker Compose |

## Quick start

```bash
# 1. Configure API keys
cp backend/.env.example backend/.env   # then fill in your keys

# 2. Build and run
docker compose up --build

# 3. Index the regulations (first run only)
curl -X POST http://localhost:8000/ingest
```

Open **http://localhost:3000** and ask away.

### Environment variables (`backend/.env`)

| Variable | Purpose |
|---|---|
| `ANTHROPIC_API_KEY` | Answer generation + suggestions (Claude) |
| `VOYAGE_API_KEY` | Embeddings + reranking |
| `OPENAI_API_KEY` | Meta-evaluation judge only (GPT-4o) |

## API

| Endpoint | Description |
|---|---|
| `POST /ask` | Ask a question — streams the answer and sources via SSE |
| `GET /suggestions` | LLM-generated suggested questions based on the indexed corpus |
| `POST /ingest` | Parse, chunk, embed and store the PDF corpus |
| `GET /health` | Health check |

## Project structure

```
├── backend/
│   ├── main.py              # FastAPI app (ask / suggestions / ingest / health)
│   ├── ingest.py            # CLI ingestion entry point
│   ├── services/
│   │   ├── ingestion.py     # PDF parsing + OCR
│   │   ├── chunking.py      # Chunking + ChromaDB vector store
│   │   ├── retrieval.py     # Hybrid search (vector + BM25) + reranking
│   │   └── generate.py      # Claude generation with citations + streaming
│   └── eval/
│       ├── run_eval.py      # Full pipeline eval: retrieval + LLM judge
│       ├── retrieval_eval.py# hit@k, precision@k, MRR
│       ├── judge.py         # Claude judge (1–5 rubric, fault categories)
│       ├── meta_eval.py     # Judge-vs-human validation (TPR/TNR gates)
│       ├── meta_judge.py    # Independent GPT-4o binary judge
│       ├── rag_runner.py    # Builds the eval dataset answers
│       ├── grade.py         # Interactive human labeling CLI
│       └── data/            # Datasets, human labels, results
├── frontend/                # Next.js chat UI (streaming, bilingual)
├── ntp_regulations/         # Source PDF corpus (INSST NTPs)
└── docker-compose.yml
```

## Running the evaluations

```bash
python -m backend.eval.run_eval    # retrieval + generation eval → data/results.json
python -m backend.eval.meta_eval   # validate the judge against human labels
python -m backend.eval.grade       # label answers interactively
```

## License

[MIT](LICENSE)
