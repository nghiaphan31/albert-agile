"""
Routage sémantique + HITL anti-boucle pour Roo Code (LiteLLM pre-call hook).

Exécuté en premier dans la chaîne des callbacks (avant litellm_hooks).
- Bloc 1 — HITL : détecte boucle d'erreurs (messages tool/user uniquement)
- Bloc 2 — Routage sémantique : embeddings nomic-embed-text, similarité cosinus
- Fallback : si similarité max < seuil, data["model"] = "worker"

Prérequis : ollama pull nomic-embed-text, pip install numpy ollama
"""
import os
from litellm.integrations.custom_logger import CustomLogger

try:
    import numpy as np
    import ollama
except ImportError:
    np = ollama = None

SIMILARITY_THRESHOLD = float(os.environ.get("ROO_SIMILARITY_THRESHOLD", "0.4"))


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


class RooCodeHandler(CustomLogger):
    """Pre-call hook : HITL + routage sémantique par embeddings."""

    def __init__(self):
        self._vectors = None

    def _get_category_vectors(self):
        if self._vectors is not None:
            return self._vectors
        if np is None or ollama is None:
            return {}
        categories = {
            "architect": "System design, software architecture, test strategy, high-level planning, database schema",
            "ingest": "Scan whole repository, read all documentation files, analyze huge context, deep code search",
            "worker": "Fix bugs, refactor code, write functions, terminal commands, git operations, unit tests",
        }
        self._vectors = {
            name: np.array(ollama.embed(model="nomic-embed-text", input=text)["embeddings"][0])
            for name, text in categories.items()
        }
        return self._vectors

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        if not messages or call_type != "completion":
            return data

        # --- Bloc 1 : HITL (messages tool/user uniquement) ---
        last_5 = messages[-5:]
        tool_user_contents = [
            str(m.get("content", "")).lower()
            for m in last_5
            if m.get("role") in ("tool", "user")
        ]
        error_count = sum(
            1
            for msg in tool_user_contents
            if any(err in msg for err in ["error", "failed"])
        )
        if error_count >= 3:
            print("\a🚨 [HITL] BOUCLE D'ERREUR DÉTECTÉE")
            data["messages"] = [{"role": "user", "content": "STOP: Error loop. Use 'ask_user'."}]
            data["model"] = "worker"
            return data

        # --- Bloc 2 : Routage sémantique (message -1) ---
        if np is None or ollama is None:
            data["model"] = "worker"
            return data

        vectors = self._get_category_vectors()
        if not vectors:
            data["model"] = "worker"
            return data

        user_intent = str(messages[-1].get("content", ""))
        try:
            emb = ollama.embed(model="nomic-embed-text", input=user_intent)
            intent_vector = np.array(emb["embeddings"][0])
        except Exception:
            data["model"] = "worker"
            return data

        scores = {name: cosine_similarity(intent_vector, vec) for name, vec in vectors.items()}
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        if best_score < SIMILARITY_THRESHOLD:
            data["model"] = "worker"
            print(f"--- [ROUTAGE] Fallback worker (score max={best_score:.2f} < {SIMILARITY_THRESHOLD}) ---")
        else:
            data["model"] = best_category
            print(f"--- [ROUTAGE] : {best_category.upper()} (Score: {best_score:.2f}) ---")
        return data


proxy_handler_instance = RooCodeHandler()
