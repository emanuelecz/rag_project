from pathlib import Path
from dotenv import load_dotenv

load_dotenv(Path(__file__).parent / ".env")

from backend.services.ingestion import ingest_folder
from backend.services.chunking import chunk_and_ingest_docs

REGULATIONS_PATH = Path(__file__).parent.parent / "ntp_regulations"


def run():
    print(f"Reading from {REGULATIONS_PATH} ...")
    docs = ingest_folder(str(REGULATIONS_PATH))
    print(f"Parsed {len(docs)} elements")

    n = chunk_and_ingest_docs(docs)
    print(f"Done — {n} chunks stored in Chroma")


if __name__ == "__main__":
    run()
