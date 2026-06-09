
import os

from dotenv import load_dotenv
from langchain_anthropic import ChatAnthropic
from langchain_core.documents import Document
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import ChatPromptTemplate
from backend.services.retrieval import retrieve_documents

load_dotenv()

MODEL_NAME = os.environ.get("ANTHROPIC_MODEL", "claude-haiku-4-5")

NO_DOCS_MSG = {
    "es": "No se han encontrado documentos relacionados con tu pregunta.",
    "en": "There are no documents matching your question.",
}

NO_CONTEXT_MSG = {
    "es": "No tengo suficiente contexto sobre esto.",
    "en": "I don't have enough context on this.",
}

SYSTEM_PROMPT = {
    "es": (
        "Eres un especialista en normativa de prevención de riesgos laborales en España, "
        "con conocimiento exhaustivo de las NTP del INSST. "
        "Responde únicamente basándote en los documentos proporcionados. "
        "Si la respuesta no se encuentra en el contexto, di únicamente: '{no_context}'. "
        "No uses tu conocimiento general. "
        "Cita las fuentes con [1], [2], etc. siempre que estén disponibles. "
        "Responde siempre en español."
    ),
    "en": (
        "You are a specialist in Spanish workplace safety regulations, "
        "with exhaustive knowledge of the INSST NTPs. "
        "Respond only from the provided documents. "
        "If the answer is not found in the context, say only: '{no_context}'. "
        "Do not use your general knowledge. "
        "Cite sources with [1], [2], etc. whenever available. "
        "Always respond in English."
    ),
}


def _build_system_prompt(lang: str) -> str:
    template = SYSTEM_PROMPT.get(lang, SYSTEM_PROMPT["es"])
    return template.format(no_context=NO_CONTEXT_MSG.get(lang, NO_CONTEXT_MSG["es"]))


def build_context(docs: list[Document]) -> str:
    blocks = []
    for i, doc in enumerate(docs, start=1):
        metadata = doc.metadata if doc.metadata else {}
        page = metadata.get("page", "?")
        source = metadata.get("source", "unknown")
        blocks.append(f"[{i}] file: {source}, page: {page}\n{doc.page_content}")
    return "\n\n---\n\n".join(blocks)


def generate_answer(question, documents=None, candidates=20, top_k=8, lang="es"):
    if documents is None:
        documents = retrieve_documents(question, candidates=candidates, top_k=top_k)

    if len(documents) == 0:
        return {
            "answer": NO_DOCS_MSG.get(lang, NO_DOCS_MSG["es"]),
            "sources": [],
            "context": "",
        }

    context = build_context(documents)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _build_system_prompt(lang)),
        ("human", "Contexto:\n{context}\n\nPregunta:\n{question}"),
    ])

    llm = ChatAnthropic(model=MODEL_NAME, temperature=0.1, max_tokens=2048)
    chain = prompt | llm | StrOutputParser()
    answer = chain.invoke({"question": question, "context": context})

    sources = [
        f"[{i}] {(doc.metadata or {}).get('source', 'unknown')} — page {(doc.metadata or {}).get('page', '?')}"
        for i, doc in enumerate(documents, start=1)
    ]
    return {"answer": answer, "sources": sources, "context": context}


async def stream_answer(question: str, candidates: int = 20, top_k: int = 8, lang: str = "es"):
    documents = retrieve_documents(question, candidates=candidates, top_k=top_k)

    if not documents:
        yield {"type": "token", "content": NO_DOCS_MSG.get(lang, NO_DOCS_MSG["es"])}
        yield {"type": "sources", "sources": []}
        return

    context = build_context(documents)

    prompt = ChatPromptTemplate.from_messages([
        ("system", _build_system_prompt(lang)),
        ("human", "Contexto:\n{context}\n\nPregunta:\n{question}"),
    ])

    llm = ChatAnthropic(model=MODEL_NAME, temperature=0.1, max_tokens=2048)
    chain = prompt | llm | StrOutputParser()

    async for chunk in chain.astream({"question": question, "context": context}):
        yield {"type": "token", "content": chunk}

    sources = [
        f"[{i}] {(doc.metadata or {}).get('source', 'unknown')} — page {(doc.metadata or {}).get('page', '?')}"
        for i, doc in enumerate(documents, start=1)
    ]
    yield {"type": "sources", "sources": sources}
