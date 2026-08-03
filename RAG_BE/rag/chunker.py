"""
chunker.py

Splits large text into overlapping chunks.
"""

from typing import List


def chunk_text(
    text: str,
    chunk_size: int = 500,
    overlap: int = 100,
) -> List[str]:
    """
    Split text into overlapping chunks.

    Parameters
    ----------
    text : str
        Input text.

    chunk_size : int
        Maximum characters per chunk.

    overlap : int
        Number of overlapping characters.

    Returns
    -------
    List[str]
        List of text chunks.
    """

    if chunk_size <= overlap:
        raise ValueError(
            "chunk_size must be greater than overlap."
        )

    text = text.strip()

    if not text:
        return []

    chunks = []

    start = 0

    while start < len(text):

        end = start + chunk_size

        chunk = text[start:end].strip()

        if chunk:
            chunks.append(chunk)

        start += chunk_size - overlap

    return chunks