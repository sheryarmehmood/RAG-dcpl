"""
config.py

Central configuration for the RAG project.
"""

from pathlib import Path
import os

# ----------------------------
# Project Directories
# ----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent

DATA_DIR = PROJECT_ROOT / "data"

CHROMA_DB_DIR = PROJECT_ROOT / "chroma_db"

# ----------------------------
# Ollama Models
# ----------------------------

CHAT_MODEL = "phi3"

EMBEDDING_MODEL = "nomic-embed-text"

# ----------------------------
# Chunking
# ----------------------------

CHUNK_SIZE = 500

CHUNK_OVERLAP = 100

# ----------------------------
# ChromaDB
# ----------------------------

COLLECTION_NAME = "documents"

TOP_K_RESULTS = int(os.getenv("RAG_TOP_K_RESULTS", "3"))

SIMILARITY_THRESHOLD = float(os.getenv("RAG_SIMILARITY_THRESHOLD", "0.9"))