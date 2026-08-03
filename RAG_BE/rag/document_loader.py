"""
document_loader.py

Responsible for loading supported document types and returning their text.

Supported formats:
- .txt
- .md
- .pdf
- .docx
"""

from pathlib import Path

from pypdf import PdfReader
from docx import Document


def read_txt(file_path: str) -> str:
    """Read a plain text file."""
    return Path(file_path).read_text(encoding="utf-8")


def read_markdown(file_path: str) -> str:
    """Read a Markdown file."""
    return Path(file_path).read_text(encoding="utf-8")


def read_pdf(file_path: str) -> str:
    """Extract text from a PDF."""
    reader = PdfReader(file_path)

    text = ""

    for page in reader.pages:
        page_text = page.extract_text()

        if page_text:
            text += page_text + "\n"

    return text


def read_docx(file_path: str) -> str:
    """Extract text from a Word document."""
    document = Document(file_path)

    paragraphs = []

    for paragraph in document.paragraphs:
        if paragraph.text.strip():
            paragraphs.append(paragraph.text)

    return "\n".join(paragraphs)


def load_document(file_path: str) -> str:
    """
    Automatically load a document based on its extension.
    """

    extension = Path(file_path).suffix.lower()

    loaders = {
        ".txt": read_txt,
        ".md": read_markdown,
        ".pdf": read_pdf,
        ".docx": read_docx,
    }

    if extension not in loaders:
        raise ValueError(f"Unsupported file type: {extension}")

    return loaders[extension](file_path)