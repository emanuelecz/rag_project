from pathlib import Path

import pypdfium2 as pdfium
from pypdf import PdfReader


def _ocr_page(pdf_path: str, page_index: int) -> str:
    try:
        import pytesseract
        doc = pdfium.PdfDocument(pdf_path)
        bitmap = doc[page_index].render(scale=3)
        text = pytesseract.image_to_string(bitmap.to_pil(), lang="spa+eng")
        doc.close()
        return text.strip()
    except Exception:
        return ""


def _extract_pdf(file_path: str) -> list[dict]:
    name = Path(file_path).name
    docs = []

    reader = PdfReader(file_path)
    for i, page in enumerate(reader.pages, start=1):
        text = (page.extract_text() or "").strip()

        if len(text) < 30:
            text = _ocr_page(file_path, i - 1)

        if len(text) > 15:
            docs.append({"text": text, "type": "NarrativeText", "source": name, "page": i})

    return docs


def _extract_other(file_path: str) -> list[dict]:
    from unstructured.partition.auto import partition

    name = Path(file_path).name
    docs = []
    for el in partition(filename=file_path, strategy="fast"):
        if len(el) > 15:
            docs.append({
                "text": el.text,
                "type": el.category,
                "source": name,
                "page": el.metadata.page_number,
            })
    return docs


def ingest_folder(file_path: str) -> list[dict]:
    path = Path(file_path)
    supported = {".pdf", ".md", ".pptx", ".txt", ".docx"}
    docs = []

    for file in path.iterdir():
        if not file.is_file() or file.suffix.lower() not in supported:
            continue
        if file.suffix.lower() == ".pdf":
            docs.extend(_extract_pdf(str(file)))
        else:
            docs.extend(_extract_other(str(file)))

    return docs
