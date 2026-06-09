from importlib import metadata
from langchain_voyageai import VoyageAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document
from langchain_chroma import Chroma 
from dotenv import load_dotenv

load_dotenv()

voyage_encoder = VoyageAIEmbeddings(model="voyage-3")
splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
vector_store = Chroma(
    embedding_function=voyage_encoder,
    collection_name="construction_reg",
    persist_directory="./my_chroma_db",
    collection_metadata={"hnsw:space": "cosine"},
)

def chunk_and_ingest_docs(documents: list[dict]):
    raw_docs = [
        Document(
            page_content=doc["text"],
            metadata= {
                "type": doc["type"],
                "source": doc["source"],
                "page": doc["page"]
            }
        ) for doc in documents
    ]
    
    chunks = splitter.split_documents(raw_docs)
    vector_store.add_documents(chunks)
    
    return len(chunks)


def get_vectorstore()-> Chroma:
    return vector_store