from langchain_community.retrievers import BM25Retriever
from langchain.retrievers import EnsembleRetriever
from langchain_core.documents import Document
import voyageai

from backend.services.chunking import get_vectorstore

RERANK_MODEL = "rerank-2.5"
voyageai_client = voyageai.Client()


_cached_merged = None
_cached_candidates = None

def _hybrid_search(query:str, candidates:int):
    global _cached_candidates , _cached_merged 
    if _cached_merged is not None and _cached_candidates == candidates:
        return _cached_merged.invoke(query)
    
    
    vector_store = get_vectorstore()
    vector_retriever = vector_store.as_retriever(
        search_type = "similarity",
        search_kwargs = {"k": candidates}
    )
    
    corpus = []
    
    batch = vector_store.get(include=["documents", "metadatas"])
    texts = batch.get("documents")
    metadatas = batch.get("metadatas")
    for i, text in enumerate(texts):
        if not text:
            continue
        meta = dict(metadatas[i]) if metadatas[i] else {}
        corpus.append(Document(
            page_content=text,
            metadata=meta
        ))
    
    if len(corpus) == 0:
        return EnsembleRetriever(retrievers=[vector_retriever], weights=[1.0]).invoke(query)
        
    keyword_retriever = BM25Retriever.from_documents(corpus)
    keyword_retriever.k = candidates
    
    merged = EnsembleRetriever(retrievers=[vector_retriever, keyword_retriever], weights=[0.5, 0.5])
    
    _cached_merged = merged
    _cached_candidates = candidates
    
    return merged.invoke(query)
    
    
def _rerank(query:str, top_k:int, docs:list[Document])-> list[Document]:
    if not docs:
        return docs
    
    top_k = min(top_k, len(docs))
    
    results = voyageai_client.rerank(
        model=RERANK_MODEL,
        documents=[d.page_content for d in docs],
        top_k=top_k,
        query=query
    )
    
    return [docs[item.index] for item in results.results]

def search(query:str, candidates:int = 20, top_k:int= 8)-> list[Document]:
    
    pool = _hybrid_search(query, candidates)
    return _rerank(query, top_k, pool)

def retrieve_documents(query:str, candidates:int = 20, top_k:int= 8):
    return search(query, candidates , top_k)