"""
embeddings.py

Generate text embeddings using Ollama.
"""

import ollama

from rag.config import EMBEDDING_MODEL


def generate_embedding(text: str) -> list[float]:
    """
    Generate an embedding vector for the given text.

    Parameters
    ----------
    text : str
        The text to embed.

    Returns
    -------
    list[float]
        Embedding vector.
    """

    if not text.strip():
        raise ValueError("Input text cannot be empty.")

    response = ollama.embed(
        model=EMBEDDING_MODEL,
        input=text,
    )

    return response["embeddings"][0]