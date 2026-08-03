"""
llm.py

Handles communication with the local Phi-3 model using Ollama.
"""

import ollama

from rag.config import CHAT_MODEL


def generate_answer(prompt: str) -> str:
    """
    Send the prompt to the local language model
    and return its response.
    """

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    return response["message"]["content"]


def generate_answer_stream(prompt: str):
    """Yield answer text chunks from Ollama for optional streaming clients."""

    response = ollama.chat(
        model=CHAT_MODEL,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    for chunk in response:
        content = chunk.get("message", {}).get("content", "")
        if content:
            yield content