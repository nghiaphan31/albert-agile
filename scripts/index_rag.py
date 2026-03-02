#!/usr/bin/env python3
"""
Pipeline d'indexation Chroma RAG pour l'écosystème Albert.
Indexe codebase, Architecture.md, Backlog, DoD, ADRs selon --sources.
"""

import argparse
import hashlib
import json
import logging
import os
import sys
from datetime import datetime
from pathlib import Path

import fnmatch

# Extensions et patterns pour chaque type de source
BACKLOG_PATTERNS = ["*Backlog*", "*backlog*", "*DoD*", "*dod*"]
ARCHITECTURE_PATTERNS = ["Architecture.md", "*ADR*", "*adr*"]
CODE_EXTENSIONS = {".py", ".js", ".ts", ".tsx", ".jsx", ".json", ".yaml", ".yml", ".toml", ".sh"}
DOC_EXTENSIONS = {".md", ".rst", ".txt"}
INCLUDE_DIRS = {"src", "scripts", "config", "specs", "docs"}
EXCLUDE_DIRS = {".git", "__pycache__", "node_modules", ".venv", "venv", "chroma_db"}
EXCLUDE_FILES = {".gitignore", ".agile-project-id", ".agile-env"}
MANIFEST_FILE = ".agile-rag-manifest.json"
CHUNK_SIZE = 1000
CHUNK_OVERLAP = 200


def get_orchestration_root() -> Path:
    """Racine du projet orchestration (parent de scripts/)."""
    return Path(__file__).resolve().parent.parent


def get_chroma_path() -> Path:
    """Chemin persistant pour Chroma."""
    root = get_orchestration_root()
    env_path = os.environ.get("AGILE_CHROMA_PATH")
    if env_path:
        return Path(env_path)
    return root / "chroma_db"


def get_files_for_source(project_root: Path, source: str) -> list[Path]:
    """Retourne la liste des fichiers à indexer selon la source."""
    project_root = project_root.resolve()
    files = set()

    def matches_patterns(path: Path, patterns: list[str]) -> bool:
        name = path.name
        for p in patterns:
            if "*" in p:
                if fnmatch.fnmatch(name, p):
                    return True
            elif p.lower() in name.lower():
                return True
        return False

    def should_include(path: Path) -> bool:
        if path.name in EXCLUDE_FILES:
            return False
        if any(ex in path.parts for ex in EXCLUDE_DIRS):
            return False
        return True

    if source == "backlog":
        for p in project_root.rglob("*"):
            if p.is_file() and should_include(p) and matches_patterns(p, BACKLOG_PATTERNS):
                files.add(p)
        # Fichiers backlog typiques
        for name in ["Besoins - Product Backlog.md", "Product Backlog.md", "Backlog.md"]:
            candidate = project_root / name
            if candidate.exists():
                files.add(candidate)

    elif source == "architecture":
        for p in project_root.rglob("*"):
            if p.is_file() and should_include(p):
                if matches_patterns(p, ARCHITECTURE_PATTERNS):
                    files.add(p)
                elif p.suffix in DOC_EXTENSIONS and any(d in p.parts for d in ("specs", "docs")):
                    files.add(p)
        arch = project_root / "Architecture.md"
        if arch.exists():
            files.add(arch)

    elif source == "code":
        for p in project_root.rglob("*"):
            if p.is_file() and should_include(p):
                if p.suffix in CODE_EXTENSIONS:
                    files.add(p)
                elif p.suffix in DOC_EXTENSIONS and any(d in p.parts for d in INCLUDE_DIRS):
                    files.add(p)

    elif source == "all":
        for p in project_root.rglob("*"):
            if p.is_file() and should_include(p):
                if p.suffix in CODE_EXTENSIONS | DOC_EXTENSIONS or p.name.endswith("json"):
                    files.add(p)

    return sorted(files)


def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP) -> list[str]:
    """Découpe le texte en chunks avec overlap."""
    if len(text) <= chunk_size:
        return [text] if text.strip() else []
    chunks = []
    start = 0
    while start < len(text):
        end = start + chunk_size
        chunk = text[start:end]
        if end < len(text):
            last_newline = chunk.rfind("\n")
            if last_newline > chunk_size // 2:
                end = start + last_newline + 1
                chunk = text[start:end]
        chunks.append(chunk)
        start = end - overlap
    return chunks


def get_file_hash(path: Path) -> str:
    """Hash du fichier pour détection des modifications (mtime pour rapidité)."""
    try:
        stat = path.stat()
        return f"{path}_{stat.st_mtime}_{stat.st_size}"
    except OSError:
        return ""


def _get_embeddings():
    """Retourne le modèle d'embeddings (Ollama prioritaire, sentence-transformers en fallback)."""
    try:
        from langchain_ollama import OllamaEmbeddings

        emb = OllamaEmbeddings(model="nomic-embed-text")
        emb.embed_documents(["test"])
        return emb
    except Exception as e:
        logging.warning("Ollama indisponible (%s), fallback sentence-transformers", e)
    try:
        from langchain_huggingface import HuggingFaceEmbeddings

        return HuggingFaceEmbeddings(
            model_name="sentence-transformers/all-MiniLM-L6-v2",
            model_kwargs={"device": "cpu"},
        )
    except ImportError:
        pass
    raise SystemExit(
        "Aucun backend d'embeddings. Options:\n"
        "  1. Démarrer Ollama: ollama serve && ollama pull nomic-embed-text\n"
        "  2. pip install langchain-huggingface sentence-transformers"
    )


def run_index(
    project_root: Path,
    project_id: str,
    sources: list[str],
    strict: bool = False,
    incremental: bool = False,
) -> tuple[int, int]:
    """Exécute l'indexation. Retourne (indexed_count, error_count)."""
    try:
        from langchain_chroma import Chroma
        from langchain_core.documents import Document
    except ImportError as e:
        logging.error("Dépendances manquantes: pip install langchain-chroma chromadb langchain-core")
        raise SystemExit(1) from e

    chroma_path = get_chroma_path()
    chroma_path.mkdir(parents=True, exist_ok=True)

    embeddings = _get_embeddings()
    collection_name = f"albert_{project_id}"

    client = Chroma(
        collection_name=collection_name,
        embedding_function=embeddings,
        persist_directory=str(chroma_path),
    )

    if not incremental:
        try:
            client._collection.delete(where={"project": project_id})
        except Exception as e:
            logging.debug("Clear collection (nouvelle ou vide): %s", e)

    all_files = set()
    for src in sources:
        all_files.update(get_files_for_source(project_root, src.strip()))

    if not all_files:
        logging.warning("Aucun fichier à indexer pour sources=%s", sources)
        return 0, 0

    indexed = 0
    errors = 0
    manifest_path = project_root / MANIFEST_FILE
    indexed_hashes = {}
    if incremental and manifest_path.exists():
        try:
            indexed_hashes = json.loads(manifest_path.read_text(encoding="utf-8"))
        except Exception:
            pass

    documents = []
    new_hashes = {}

    for filepath in all_files:
        try:
            rel_path = filepath.relative_to(project_root)
            rel_str = str(rel_path).replace("\\", "/")
            content = filepath.read_text(encoding="utf-8", errors="replace")

            if not content.strip():
                continue

            file_hash = hashlib.sha256(content.encode()).hexdigest()
            if incremental and indexed_hashes.get(rel_str) == file_hash:
                continue

            if incremental and rel_str in indexed_hashes:
                try:
                    client._collection.delete(where={"source": rel_str})
                except Exception:
                    pass

            doc_type = "doc" if filepath.suffix in DOC_EXTENSIONS else "code"

            chunks = chunk_text(content)
            for i, chunk in enumerate(chunks):
                if not chunk.strip():
                    continue
                documents.append(
                    Document(
                        page_content=chunk,
                        metadata={
                            "source": rel_str,
                            "type": doc_type,
                            "project": project_id,
                            "file_hash": file_hash,
                            "chunk_index": i,
                        },
                    )
                )
                indexed += 1
            new_hashes[rel_str] = file_hash

        except Exception as e:
            errors += 1
            logging.warning("Skip %s: %s", filepath, e)

    if documents:
        texts = [d.page_content for d in documents]
        meta_list = [d.metadata for d in documents]
        client.add_texts(texts=texts, metadatas=meta_list)

    if incremental and new_hashes:
        updated = {**indexed_hashes, **new_hashes}
        manifest_path.write_text(json.dumps(updated, indent=2), encoding="utf-8")

    total = len(all_files)
    if errors > 0 and total > 0 and (errors / total) > 0.1:
        logging.warning("> 10%% de fichiers en erreur: %d/%d", errors, total)

    if strict and indexed == 0 and all_files:
        logging.error("--strict: aucun fichier indexé avec succès")
        raise SystemExit(1)

    return indexed, errors


def main() -> int:
    parser = argparse.ArgumentParser(description="Indexation RAG Chroma pour Albert")
    parser.add_argument("--project-root", required=True, type=Path, help="Racine du projet à indexer")
    parser.add_argument("--project-id", required=True, help="Identifiant projet (collection Chroma)")
    parser.add_argument(
        "--sources",
        default="all",
        help="Sources: backlog|architecture|code|all (séparés par des virgules)",
    )
    parser.add_argument("--strict", action="store_true", help="Exit 1 si 0 fichier indexé")
    parser.add_argument("--incremental", action="store_true", help="Indexation incrémentale")
    args = parser.parse_args()

    project_root = args.project_root.resolve()
    if not project_root.is_dir():
        logging.error("project-root invalide: %s", project_root)
        return 2

    sources = [s.strip() for s in args.sources.split(",") if s.strip()]
    if not sources:
        sources = ["all"]

    log_dir = get_orchestration_root() / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    log_file = log_dir / f"index_rag_{timestamp}.log"
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        handlers=[
            logging.FileHandler(log_file, encoding="utf-8"),
            logging.StreamHandler(sys.stdout),
        ],
    )

    try:
        indexed, errors = run_index(
            project_root=project_root,
            project_id=args.project_id,
            sources=sources,
            strict=args.strict,
            incremental=args.incremental,
        )
        logging.info("Indexation terminée: %d chunks indexés, %d erreurs. Rapport: %s", indexed, errors, log_file)
        return 0
    except SystemExit as e:
        return e.code if isinstance(e.code, int) else 1
    except Exception as e:
        logging.exception("Échec indexation: %s", e)
        if args.strict:
            return 1
        raise


if __name__ == "__main__":
    sys.exit(main())
