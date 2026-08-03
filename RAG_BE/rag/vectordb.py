"""
vectordb.py

Handles storing and retrieving embeddings using ChromaDB.
"""

import chromadb

from rag.config import CHROMA_DB_DIR, COLLECTION_NAME


class VectorDatabase:
    """
    Wrapper around ChromaDB.
    """

    def __init__(self):

        self.client = chromadb.PersistentClient(
            path=str(CHROMA_DB_DIR)
        )

        self.collection = self.client.get_or_create_collection(
            name=COLLECTION_NAME
        )

    def add_document(
        self,
        doc_id: str,
        text: str,
        embedding: list[float],
        metadata: dict,
    ) -> bool:
        """
        Store a document chunk.

        Returns True if stored.
        Returns False if the chunk already exists.
        """

        existing = self.collection.get(ids=[doc_id])

        if existing["ids"]:
            return False

        self.collection.add(
            ids=[doc_id],
            documents=[text],
            embeddings=[embedding],
            metadatas=[metadata],
        )

        return True

    #def search(
     #   self,
      #  embedding: list[float],
       # top_k: int = 3,
    #):
        """
        Search for similar vectors.
        """

     #   return self.collection.query(
      #      query_embeddings=[embedding],
       #     n_results=top_k,
        #)


    def search(
    self,
    embedding: list[float],
    top_k: int = 3,
    similarity_threshold: float | None = None,
    ):
        """
        Search for similar vectors.
        """

        if self.count() == 0:
            return {"documents": [[]], "metadatas": [[]], "distances": [[]]}

        results = self.collection.query(
            query_embeddings=[embedding],
            n_results=min(top_k, self.count()),
            include=[
                "documents",
                "metadatas",
                "distances",
            ],
        )

        if similarity_threshold is None:
            return results

        documents = results["documents"][0]
        metadatas = results["metadatas"][0]
        distances = results["distances"][0]
        matches = [
            (document, metadata, distance)
            for document, metadata, distance in zip(documents, metadatas, distances)
            if distance <= similarity_threshold
        ]

        return {
            "documents": [[match[0] for match in matches]],
            "metadatas": [[match[1] for match in matches]],
            "distances": [[match[2] for match in matches]],
        }



    def get_all(self):
        """
        Return all stored records.
        """

        return self.collection.get(
            include=[
                "documents",
                "metadatas",
            ]
        )

    def count(self):
        """
        Return total number of stored chunks.
        """

        return self.collection.count()

    def get_source_documents(self):
        """Return indexed source names and their chunk counts."""

        records = self.collection.get(include=["metadatas"])
        counts = {}

        for metadata in records.get("metadatas") or []:
            source = metadata.get("source") if metadata else None
            if source:
                counts[source] = counts.get(source, 0) + 1

        return [
            {"source": source, "chunks": chunk_count}
            for source, chunk_count in sorted(counts.items())
        ]

    def delete_source(self, source: str) -> int:
        """Delete all indexed chunks belonging to a source."""

        records = self.collection.get(
            where={"source": source},
            include=["metadatas"],
        )
        ids = records.get("ids") or []

        if ids:
            self.collection.delete(ids=ids)

        return len(ids)