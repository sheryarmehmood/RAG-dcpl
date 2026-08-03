"""
ingest.py

Reads documents from the data folder,
splits them into chunks,
generates embeddings,
and stores them in ChromaDB.
"""

from tqdm import tqdm

from rag.config import DATA_DIR
from rag.document_loader import load_document
from rag.chunker import chunk_text
from rag.embeddings import generate_embedding
from rag.vectordb import VectorDatabase


SUPPORTED_EXTENSIONS = {
    ".txt",
    ".pdf",
    ".docx",
    ".md",
}


def ingest_documents(files=None):

    db = VectorDatabase()

    if files is None:
        files = sorted(
            [
                file
                for file in DATA_DIR.iterdir()
                if file.suffix.lower() in SUPPORTED_EXTENSIONS
            ]
        )
    else:
        files = [file for file in files if file.suffix.lower() in SUPPORTED_EXTENSIONS]

    if not files:
        print("No supported documents found.")
        return {
            "files_processed": 0,
            "chunks_found": 0,
            "chunks_stored": 0,
            "chunks_skipped": 0,
            "database_total": db.count(),
        }

    print("=" * 70)
    print(f"Found {len(files)} document(s)")
    print("=" * 70)

    total_chunks = 0
    stored_chunks = 0
    skipped_chunks = 0

    for file in files:

        print(f"\nReading: {file.name}")

        try:

            text = load_document(str(file))

            chunks = chunk_text(text)

            print(f"Chunks Created: {len(chunks)}")

            for index, chunk in enumerate(
                tqdm(chunks, desc=file.name)
            ):

                embedding = generate_embedding(chunk)

                chunk_id = (
                    f"{file.stem}_"
                    f"{file.suffix[1:]}_"
                    f"chunk_{index}"
                )

                metadata = {
                    "source": file.name,
                    "file_type": file.suffix.lower(),
                    "chunk_index": index,
                }

                stored = db.add_document(
                    doc_id=chunk_id,
                    text=chunk,
                    embedding=embedding,
                    metadata=metadata,
                )

                total_chunks += 1

                if stored:
                    stored_chunks += 1
                else:
                    skipped_chunks += 1

        except Exception as error:

            print(f"Error processing {file.name}")

            print(error)

    print("\n")
    print("=" * 70)
    print("INGESTION COMPLETE")
    print("=" * 70)

    print(f"Files Processed : {len(files)}")
    print(f"Chunks Found    : {total_chunks}")
    print(f"Chunks Stored   : {stored_chunks}")
    print(f"Chunks Skipped  : {skipped_chunks}")
    print(f"Database Total  : {db.count()}")

    return {
        "files_processed": len(files),
        "chunks_found": total_chunks,
        "chunks_stored": stored_chunks,
        "chunks_skipped": skipped_chunks,
        "database_total": db.count(),
    }


if __name__ == "__main__":
    ingest_documents()