#!/usr/bin/env python3
"""Export de la collection Chroma d'un projet vers JSON (spec III.8-L, S10)."""
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
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args()

    try:
        from langchain_chroma import Chroma
        from langchain_ollama import OllamaEmbeddings
    except ImportError:
        print("pip install langchain-chroma langchain-ollama")
        return 1

    chroma_path = get_chroma_path()
    collection_name = f"albert_{args.project_id}"
    emb = OllamaEmbeddings(model="nomic-embed-text")
    client = Chroma(
        collection_name=collection_name,
        embedding_function=emb,
        persist_directory=str(chroma_path),
    )
    data = client.get()
    out = {"ids": data["ids"], "metadatas": data["metadatas"], "documents": data.get("documents", [])}
    args.output.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"Exporté {len(data['ids'])} documents vers {args.output}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
