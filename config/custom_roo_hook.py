"""
Routage sémantique + HITL anti-boucle pour Roo Code (LiteLLM pre-call hook).

Debug:
  ROO_DEBUG_LOG=/path/to/roo_debug.log — trace model_in → model_out (1 ligne)
  ROO_ROUTING_LOG=/path/to/routing.jsonl — fenêtre détaillée pour affiner l'algo (JSON lines)

Exécuté en premier dans la chaîne des callbacks (avant litellm_hooks).
- Bloc 1 — HITL : détecte boucle d'erreurs (messages tool/user uniquement)
- Bloc 2 — Routage sémantique : embeddings nomic-embed-text, similarité cosinus
- Fallback : si similarité max < seuil, data["model"] = modèle primaire worker

Routage : architect → architect-free-gemini-2.5-pro, ingest → ingest-free-gemini-2.5-flash,
worker → worker-local-qwen2.5-coder:14b (convention role-tier-modele).

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
# Force worker-local (bypass sémantique) pour debug : ROO_FORCE_WORKER_LOCAL=1
FORCE_WORKER_LOCAL = os.environ.get("ROO_FORCE_WORKER_LOCAL", "").lower() in ("1", "true", "yes")

# Modèles primaires par rôle (convention role-tier-modele)
ROO_PRIMARY_MODEL = {
    "architect": "architect-free-gemini-2.5-pro",
    "ingest": "ingest-free-gemini-2.5-flash",
    "worker": "worker-free-gemini-2.5-flash",
}


def cosine_similarity(a, b):
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b) + 1e-9))


def _log_routing_decision(
    model_in: str,
    model_out: str,
    source: str,
    messages: list,
    user_intent: str = "",
    score: float | str | None = None,
    scores: dict | None = None,
    has_tools: bool = False,
) -> None:
    """
    Log une décision de routage (JSON lines) pour analyse et affinage de l'algo.
    Activé via ROO_ROUTING_LOG=/path/to/routing.jsonl
    ROO_ROUTING_WINDOW=12 (défaut) : nb de messages dans la fenêtre.
    """
    import json
    from datetime import datetime
    path = os.environ.get("ROO_ROUTING_LOG")
    if not path:
        return
    window = int(os.environ.get("ROO_ROUTING_WINDOW", "12"))
    try:
        window_msgs = [
            {
                "role": m.get("role", ""),
                "len": len(str(m.get("content", ""))),
                "preview": str(m.get("content", ""))[:200],
            }
            for m in messages[-window:]
        ]
        entry = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "model_in": model_in,
            "model_out": model_out,
            "source": source,
            "n_messages": len(messages),
            "window": window_msgs,
            "user_intent_preview": (user_intent or "")[:500],
            "user_intent_len": len(user_intent or ""),
            "has_tools": has_tools,
        }
        if score is not None:
            entry["score"] = score
        if scores:
            entry["scores"] = {k: round(v, 4) for k, v in scores.items()}
        with open(path, "a") as f:
            f.write(json.dumps(entry, ensure_ascii=False) + "\n")
    except OSError:
        pass


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
            "architect": "System design, software architecture, authentication module, RBAC, authorization, design patterns, high-level planning, database schema, component design, API design",
            "ingest": "Scan whole repository, read all documentation files, analyze huge context, deep code search",
            "worker": "Fix bugs, refactor code, write functions, terminal commands, git operations, unit tests",
        }
        self._vectors = {
            name: np.array(ollama.embed(model="nomic-embed-text", input=text)["embeddings"][0])
            for name, text in categories.items()
        }
        return self._vectors

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        model_in = data.get("model", "")
        # Log inconditionnel pour vérifier que le hook est appelé
        _log_path = os.environ.get("ROO_HOOK_DEBUG") or (os.environ.get("TMPDIR", "/tmp") + "/roo_hook.log" if FORCE_WORKER_LOCAL else None)
        if _log_path:
            try:
                with open(_log_path, "a") as f:
                    f.write(f"pre_call: call_type={call_type!r} model_in={model_in!r} has_messages={bool(data.get('messages'))}\n")
            except OSError:
                pass

        messages = data.get("messages", [])
        # "completion" = sync, "acompletion" = async (proxy)
        if not messages or call_type not in ("completion", "acompletion"):
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
        def _debug_log(model_out: str) -> None:
            if os.environ.get("ROO_DEBUG_LOG"):
                try:
                    with open(os.environ["ROO_DEBUG_LOG"], "a") as f:
                        f.write(f"model_in={model_in} → model_out={model_out}\n")
                except OSError:
                    pass

        has_tools = bool(data.get("tools"))
        if FORCE_WORKER_LOCAL:
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            _log_routing_decision(model_in, data["model"], "force_worker", messages, has_tools=has_tools)
            print(f"--- [ROUTAGE] model_in={model_in!r} → worker-local (FORCE) ---", flush=True)
            _debug_log(data["model"])
            return data

        if error_count >= 3:
            print("\a🚨 [HITL] BOUCLE D'ERREUR DÉTECTÉE", flush=True)
            data["messages"] = [{"role": "user", "content": "STOP: Error loop. Use 'ask_user'."}]
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            _log_routing_decision(model_in, data["model"], "hitl", messages, has_tools=has_tools)
            _debug_log(data["model"])
            return data

        # --- Bloc 2 : Routage sémantique ---
        # Pré-check ingest: si dernier message user demande analyse/scan (pas le 1er, qui peut être une ancienne tâche)
        _user_msgs = [str(m.get("content", "")).lower() for m in messages if m.get("role") == "user"]
        _last_user = (_user_msgs[-1] if _user_msgs else "")[:500]
        if any(k in _last_user for k in ("analyze", "analyse", "scan", "read all", "examine", "specs/", "documentation", "recursively")):
            data["model"] = ROO_PRIMARY_MODEL["ingest"]
            data["_roo_routing_score"] = "keywords"
            _log_routing_decision(model_in, data["model"], "keywords_ingest", messages, _last_user, score="keywords", has_tools=has_tools)
            print(f"--- [ROUTAGE] model_in={model_in!r} → ingest (keywords user) ---", flush=True)
            _debug_log(data["model"])
            return data

        # Pré-check architect
        # Pré-check: si le contexte récent évoque architect (réponses courtes type "internes"/"aucun"),
        # forcer architect quand assistant/user mentionnent architecture, conception, module
        _architect_keywords = ("architecture", "concevoir", "conception", "architect", "module d'", "module d’")
        _recent_text = " ".join(
            str(m.get("content", "")).lower() for m in messages[-8:]
            if m.get("role") in ("user", "assistant")
        )[:2000]
        if any(kw in _recent_text for kw in _architect_keywords):
            data["model"] = ROO_PRIMARY_MODEL["architect"]
            data["_roo_routing_score"] = "keywords"
            _log_routing_decision(model_in, data["model"], "keywords_architect", messages, _recent_text[:500], score="keywords", has_tools=has_tools)
            print(f"--- [ROUTAGE] model_in={model_in!r} → architect (keywords dans contexte) ---", flush=True)
            _debug_log(data["model"])
            return data

        if np is None or ollama is None:
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            _log_routing_decision(model_in, data["model"], "no_embeddings", messages, has_tools=has_tools)
            _debug_log(data["model"])
            return data

        vectors = self._get_category_vectors()
        if not vectors:
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            _log_routing_decision(model_in, data["model"], "no_vectors", messages, has_tools=has_tools)
            _debug_log(data["model"])
            return data

        # Construire l'intent pour l'embedding
        user_msgs = [str(m.get("content", "")) for m in messages if m.get("role") == "user"]
        user_intent = (user_msgs[-1] if user_msgs else "") or str(messages[-1].get("content", ""))
        # Si dernier message court (<80 chars), enrichir avec l'historique récent pour un meilleur embedding
        if len(user_intent) < 80:
            recent = [
                f"{m.get('role','')}: {str(m.get('content',''))}"
                for m in messages[-6:]
                if m.get("role") in ("user", "assistant") and m.get("content")
            ]
            user_intent = " | ".join(recent)[:1500]  # limite pour nomic-embed-text
        try:
            emb = ollama.embed(model="nomic-embed-text", input=user_intent)
            intent_vector = np.array(emb["embeddings"][0])
        except Exception:
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            _log_routing_decision(model_in, data["model"], "embedding_error", messages, user_intent, has_tools=has_tools)
            _debug_log(data["model"])
            return data

        scores = {name: cosine_similarity(intent_vector, vec) for name, vec in vectors.items()}
        best_category = max(scores, key=scores.get)
        best_score = scores[best_category]

        if best_score < SIMILARITY_THRESHOLD:
            data["model"] = ROO_PRIMARY_MODEL["worker"]
            data["_roo_routing_score"] = round(best_score, 2)
            _log_routing_decision(model_in, data["model"], "embedding_fallback", messages, user_intent, score=round(best_score, 4), scores=scores, has_tools=has_tools)
            print(f"--- [ROUTAGE] Fallback worker (score max={best_score:.2f} < {SIMILARITY_THRESHOLD}) ---", flush=True)
        else:
            data["model"] = ROO_PRIMARY_MODEL[best_category]
            data["_roo_routing_score"] = round(best_score, 2)
            _log_routing_decision(model_in, data["model"], "embedding", messages, user_intent, score=round(best_score, 4), scores=scores, has_tools=has_tools)
            print(f"--- [ROUTAGE] model_in={model_in!r} → {data['model']} ({best_category}, score={best_score:.2f}) ---", flush=True)

        _debug_log(data["model"])
        return data


proxy_handler_instance = RooCodeHandler()
