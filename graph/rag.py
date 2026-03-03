"""
RAG Chroma pour injection de contexte dans les nœuds (spec III.7).
R-2, R-3, R-4 interrogent le RAG pour Backlog, Architecture, code.
"""

import os
from pathlib import Path


def _get_chroma_path() -> Path:
    root = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
    return Path(os.environ.get("AGILE_CHROMA_PATH", root / "chroma_db"))


def _get_embeddings():
    """Ollama nomic-embed-text pour requêtes."""
    from langchain_ollama import OllamaEmbeddings
    return OllamaEmbeddings(model="nomic-embed-text")


def query_rag(project_id: str, query: str, top_k: int = 5) -> list[str]:
    """
    Requête RAG Chroma pour un projet.
    Retourne les chunks pertinents (page_content).
    """
    try:
        from langchain_chroma import Chroma
    except ImportError:
        return []

    chroma_path = _get_chroma_path()
    if not chroma_path.exists():
        return []

    collection_name = f"albert_{project_id}"
    try:
        embeddings = _get_embeddings()
        client = Chroma(
            collection_name=collection_name,
            embedding_function=embeddings,
            persist_directory=str(chroma_path),
        )
        docs = client.similarity_search(query, k=top_k)
        return [d.page_content for d in docs]
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning("query_rag failed: %s", e)
        return []
