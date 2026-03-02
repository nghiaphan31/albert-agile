#!/usr/bin/env python3
"""Import d'une collection Chroma depuis JSON (spec III.8-L, S10)."""
import argparse
import json
import sys
from pathlib import Path


def get_chroma_path() -> Path:
    root = Path(__file__).resolve().parent.parent
    env_path = __import__("os").environ.get("AGILE_CHROMA_PATH")
    if env_path:
        return Path(env_path)
    return root / "chroma_db"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--project-id", required=True)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()

    if not args.input.exists():
        print(f"Fichier introuvable: {args.input}")
        return 1

    try:
        from langchain_chroma import Chroma
        from langchain_ollama import OllamaEmbeddings
    except ImportError:
        print("pip install langchain-chroma langchain-ollama")
        return 1

    data = json.loads(args.input.read_text(encoding="utf-8"))
    chroma_path = get_chroma_path()
    collection_name = f"albert_{args.project_id}"
    emb = OllamaEmbeddings(model="nomic-embed-text")
    client = Chroma(
        collection_name=collection_name,
        embedding_function=emb,
        persist_directory=str(chroma_path),
    )
    client.add_texts(
        texts=data.get("documents", []),
        metadatas=data.get("metadatas", []),
        ids=data.get("ids", []),
    )
    print(f"Importé {len(data.get('ids', []))} documents depuis {args.input}")
    return 0

