"""
query.py

Complete RAG Query Pipeline

1. Accept a user's question.
2. Generate an embedding.
3. Search ChromaDB.
4. Build context from retrieved chunks.
5. Send context to Phi-3.
6. Display the final answer.
"""

from rag.embeddings import generate_embedding
from rag.vectordb import VectorDatabase
from rag.llm import generate_answer
from rag.config import SIMILARITY_THRESHOLD, TOP_K_RESULTS


def search_documents(
    question: str,
    top_k: int = TOP_K_RESULTS,
    similarity_threshold: float | None = SIMILARITY_THRESHOLD,
):
    """
    Search ChromaDB using a natural language question.
    """

    db = VectorDatabase()

    question_embedding = generate_embedding(question)

    return db.search(
        embedding=question_embedding,
        top_k=top_k,
        similarity_threshold=similarity_threshold,
    )


def build_context(results) -> str:
    """
    Combine retrieved chunks into clearly formatted context.
    """

    documents = results.get("documents", [[]])[0]
    metadatas = results.get("metadatas", [[]])[0]

    context_parts = []

    for index, (document, metadata) in enumerate(zip(documents, metadatas), start=1):
        context_parts.append(
            "\n".join(
                [
                    f"Citation: [{index}] {metadata.get('source', 'Unknown source')}",
                    f"Chunk: {metadata.get('chunk_index', 'Unknown')}",
                    "Content:",
                    document.strip(),
                ]
            )
        )

    if not context_parts:
        return "No relevant context was found."

    return f"\n\n{'-' * 70}\n\n".join(context_parts)


def build_prompt(context: str, question: str) -> str:
    """
        Create a concise and precise prompt for the language model.
    """

    return f"""
You are a professional document-question-answering assistant.

Answer the question using only the supplied context.

Follow these rules:
- Use clear, natural, grammatically correct English.
- Give a direct answer in one or two sentences.
- Include only information relevant to the question.
- Do not repeat the question.
- Do not add assumptions or unsupported information.
- Do not mention unrelated personal information, IDs, passwords,
    tokens, recovery codes, or verification codes.
    - Cite supporting context with [1], [2], or [3] when appropriate.
    - If the answer is not clearly stated in the context, respond exactly:
    "I could not find the answer in the provided documents."

==================== CONTEXT ====================

{context.strip()}

===================================================

Question:

{question.strip()}

Answer:
""".strip()


def main():

    print("=" * 70)
    print("LOCAL RAG ASSISTANT")
    print("=" * 70)

    question = input("\nEnter your question:\n> ").strip()

    if not question:
        print("\nQuestion cannot be empty.")
        return

    print("\nSearching ChromaDB...")

    results = search_documents(question)

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]
    distances = results["distances"][0]

    print("\n")
    print("=" * 70)
    print(f"Retrieved Top {len(documents)} Chunks")
    print("=" * 70)

    for i, (doc, meta, distance) in enumerate(
        zip(documents, metadatas, distances),
        start=1,
    ):

        print(f"\nChunk {i}")
        print("-" * 70)
        print(f"Source   : {meta['source']}")
        print(f"Chunk ID : {meta['chunk_index']}")
        print(f"Distance : {distance:.4f}")
        print()
        print(doc)

    context = build_context(results)

    prompt = build_prompt(
        context=context,
        question=question,
    )

    print("\n")
    print("=" * 70)
    print("Generating Answer with Phi-3...")
    print("=" * 70)

    answer = generate_answer(prompt).strip()

    print("\n")
    print("=" * 70)
    print("FINAL ANSWER")
    print("=" * 70)
    print(answer)


if __name__ == "__main__":
    main()