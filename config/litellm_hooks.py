"""
LiteLLM hooks — deux stratégies pour fiabiliser le tool calling des LLMs locaux :

1. Pre-call  : injecte un rappel strict dans le system prompt (aide les modèles capables)
2. Post-call : répare les tool calls invalides dans la réponse (filet de sécurité)
              - ask_followup_question sans follow_up → on ajoute des suggestions génériques
              - follow_up non-array → on le convertit en array
              - Option A : si réparation impossible, supprime le tool_call (réponse texte safe)
3. Post-call streaming : injecte la signature du modèle sur le dernier chunk (visible par Roo)

Chargé via litellm_config.yaml (en 2e après custom_roo_hook) :
  litellm_settings:
    callbacks:
      - custom_roo_hook.proxy_handler_instance   # 1. HITL + routage
      - litellm_hooks.proxy_handler_instance     # 2. TOOL_SCHEMA_PROMPT (si model worker-*)
"""
import json
import logging
from collections import deque
from typing import AsyncGenerator, Any, List, Tuple

from litellm.integrations.custom_logger import CustomLogger

_logger = logging.getLogger(__name__)

# Chaînes de fallback (même structure que litellm_config.yaml) pour reconstruire le chemin
FALLBACK_CHAINS = {
    "architect-free-gemini-2.5-pro": ["architect-vertex-gemini-2.5-pro", "architect-pay-deepseek-chat"],
    "architect-vertex-gemini-2.5-pro": ["architect-pay-deepseek-chat"],
    "ingest-free-gemini-2.5-flash": ["ingest-vertex-gemini-2.0-flash", "ingest-pay-gemini-2.5-flash"],
    "ingest-vertex-gemini-2.0-flash": ["ingest-pay-gemini-2.5-flash"],
    "qwen3": ["worker-free-gemini-2.5-flash", "worker-pay-deepseek-chat"],
    "worker-local-qwen2.5-coder:14b": ["worker-free-gemini-2.5-flash", "worker-pay-deepseek-chat"],
    "worker-free-gemini-2.5-flash": ["worker-pay-deepseek-chat"],
    "langgraph-conception-qwen2.5:14b": ["fallback-gemini-2.5-flash", "fallback-claude-opus-4-6"],
    "langgraph-code-qwen2.5-coder:14b": ["fallback-gemini-2.5-flash", "fallback-claude-sonnet-4-6"],
    "fallback-gemini-2.5-flash": ["fallback-claude-sonnet-4-6", "local-qwen3:14b"],
    "local-qwen3:14b": ["fallback-gemini-2.5-flash", "fallback-claude-sonnet-4-6"],
    "local-qwen2.5-coder:14b": ["fallback-gemini-2.5-flash", "fallback-claude-sonnet-4-6"],
    "local-qwen2.5:14b": ["fallback-gemini-2.5-flash", "fallback-claude-sonnet-4-6"],
}

TOOL_SCHEMA_PROMPT = """TOOL CALLING RULES — MANDATORY:
1. You MUST call exactly one tool per response.
2. You MUST provide ALL required parameters — never omit one.
3. For "follow_up" (array of strings): always provide 2-4 suggested answers as a list.
   CORRECT:   "follow_up": ["Yes, proceed", "No, cancel", "Tell me more"]
   INCORRECT: omitting follow_up, or "follow_up": "Yes"
4. If the task is complete: use attempt_completion(result="...").
5. If you need clarification: use ask_followup_question(question="...", follow_up=[...]).
"""

DEFAULT_FOLLOW_UP = ["Yes, please continue", "No, stop here", "Give me more details"]
SAFE_QUESTION = "Erreur de format interne. Souhaitez-vous que je réessaie ?"


def _repair_ask_followup_tc(tc) -> bool:
    """
    Répare un tool_call ask_followup_question. Retourne True si réparable, False si à supprimer.
    Modifie tc en place.
    """
    fn = getattr(tc, "function", None)
    if fn is None:
        return False
    name = getattr(fn, "name", "")
    if name != "ask_followup_question":
        return True  # on ne touche pas aux autres tools

    raw_args = getattr(fn, "arguments", None) or "{}"
    try:
        args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
        if not isinstance(args, dict):
            args = {}
    except json.JSONDecodeError:
        # Structure irrécupérable : forcer une structure valide
        args = {"question": SAFE_QUESTION, "follow_up": DEFAULT_FOLLOW_UP}
        fn.arguments = json.dumps(args)
        return True

    follow_up = args.get("follow_up")
    if not isinstance(follow_up, list) or len(follow_up) == 0:
        args["follow_up"] = DEFAULT_FOLLOW_UP
        fn.arguments = json.dumps(args)
    return True


def _get_routing_path(routed: str, actual: str) -> List[Tuple[str, bool]]:
    """
    Reconstruit le chemin de routage (modèles demandés puis échoués → modèle qui a répondu).
    BFS sur FALLBACK_CHAINS. Si actual hors chaîne (ex. provider ID normalisé), on l'ajoute à la fin.
    """
    if not routed and not actual:
        return []
    routed = (routed or "").strip()
    actual = (actual or routed).strip()
    if routed == actual:
        return [(routed, True)]  # pas de fallback
    if not routed:
        return [(actual, True)]
    if not actual:
        return [(routed, False)]

    # BFS : routed → ... → actual
    parent = {routed: None}
    queue = deque([routed])
    found = False
    while queue:
        cur = queue.popleft()
        for fb in FALLBACK_CHAINS.get(cur, []):
            if fb not in parent:
                parent[fb] = cur
                if fb == actual:
                    found = True
                    break
                queue.append(fb)
        if found:
            break

    if found:
        path_models = []
        node = actual
        while node is not None:
            path_models.insert(0, node)
            node = parent.get(node)
        return [(m, m == actual) for m in path_models]

    # actual hors chaîne (ex. fallback-gemini quand worker-free a répondu)
    return [(routed, False), (actual, True)]


def _format_routing_path(path: List[Tuple[str, bool]]) -> str:
    """Formate le chemin pour la signature : A (échec) → B (échec) → C (réponse générée)."""
    if not path:
        return ""
    parts = []
    for model, success in path:
        if success:
            parts.append(f"{model} (réponse générée)")
        else:
            parts.append(f"{model} (échec)")
    return " → ".join(parts)


MODEL_SIGNATURE = "\n\n— *Chemin de routage : {path}*"

# Préfixes convention model_name (architect-, ingest-, worker-, local-, fallback-, langgraph-)
CONVENTION_PREFIXES = ("architect-", "ingest-", "worker-", "local-", "fallback-", "langgraph-")

# Mapping provider_id → model_name (convention) quand LiteLLM retourne un ID fournisseur
PROVIDER_TO_MODEL_NAME = {
    "ollama_chat/qwen3:14b": "local-qwen3:14b",
    "ollama_chat/qwen2.5-coder:14b": "local-qwen2.5-coder:14b",
    "ollama_chat/qwen2.5:14b": "local-qwen2.5:14b",
    "gemini/gemini-2.5-pro": "architect-free-gemini-2.5-pro",
    "gemini/gemini-2.5-flash": "fallback-gemini-2.5-flash",
    "vertex_ai/gemini-2.5-pro": "architect-vertex-gemini-2.5-pro",
    "vertex_ai/gemini-2.0-flash": "ingest-vertex-gemini-2.0-flash",
    "deepseek/deepseek-chat": "architect-pay-deepseek-chat",
    "anthropic/claude-sonnet-4-6": "fallback-claude-sonnet-4-6",
    "anthropic/claude-opus-4-6": "fallback-claude-opus-4-6",
}


def _is_convention_model_name(s: str) -> bool:
    """Vérifie si la chaîne respecte notre convention model_name."""
    s = (s or "").strip()
    return any(s.startswith(p) for p in CONVENTION_PREFIXES) if s else False


def _normalize_to_convention(raw: str) -> str:
    """
    Normalise un identifiant modèle vers notre convention model_name.
    Retourne la chaîne telle quelle si déjà en convention, sinon mappe via PROVIDER_TO_MODEL_NAME.
    """
    raw = (raw or "").strip()
    if not raw:
        return ""
    if _is_convention_model_name(raw):
        return raw
    return PROVIDER_TO_MODEL_NAME.get(raw, raw)  # garder raw si pas de mapping (lisible)


def _get_model_for_signature(response, data: dict) -> str:
    """
    Extrait le modèle réel utilisé pour la signature, fiable selon notre convention.

    Ordre de priorité :
    1. data["model"] si déjà en convention (routage custom_roo_hook)
    2. response.model, _hidden_params (modèle effectivement appelé)
    3. data.litellm_params.model
    Puis normalisation provider_id → model_name via PROVIDER_TO_MODEL_NAME.
    """
    candidates = []

    # response = modèle effectivement utilisé (inclut fallback)
    model = getattr(response, "model", None)
    if model and str(model).strip():
        candidates.append(str(model).strip())

    hidden = getattr(response, "_hidden_params", None) or {}
    if isinstance(hidden, dict):
        for key in ("model", "litellm_actual_model", "litellm_params"):
            val = hidden.get(key)
            if isinstance(val, dict) and "model" in val:
                v = val.get("model")
                if v and str(v).strip():
                    candidates.append(str(v).strip())
            elif val and str(val).strip():
                candidates.append(str(val).strip())

    lp = (data or {}).get("litellm_params") or {}
    if isinstance(lp, dict):
        val = lp.get("model")
        if val and str(val).strip():
            candidates.append(str(val).strip())

    # data["model"] = modèle routé (fallback si response vide)
    dm = (data or {}).get("model") or ""
    if dm and str(dm).strip():
        candidates.append(str(dm).strip())

    for c in candidates:
        normalized = _normalize_to_convention(c)
        if normalized:
            _store_actual_model(response, normalized)
            return normalized

    return ""


def _store_actual_model(response, model: str) -> None:
    """Stocke le modèle réel dans _hidden_params pour traçabilité."""
    try:
        hidden = getattr(response, "_hidden_params", None)
        if hidden is None:
            return
        if not isinstance(hidden, dict):
            return
        hidden["_actual_model_used"] = model
    except Exception:
        pass


def _get_model_from_request_data(request_data: dict) -> str:
    """Extrait et normalise le nom du modèle depuis request_data (routage custom_roo_hook)."""
    raw = (request_data or {}).get("model") or ""
    return _normalize_to_convention(str(raw).strip())


def _append_model_signature(response_obj, routed_model: str, actual_model: str):
    """Ajoute la signature (chemin de routage détaillé) à la fin du content."""
    path = _get_routing_path(routed_model or "", actual_model or "")
    if not path:
        return
    path_str = _format_routing_path(path)
    try:
        choices = getattr(response_obj, "choices", None) or []
        for choice in choices:
            msg = getattr(choice, "message", None)
            if msg is None:
                continue
            content = getattr(msg, "content", None)
            if content and isinstance(content, str):
                setattr(msg, "content", content + MODEL_SIGNATURE.format(path=path_str))
    except Exception as e:
        _logger.warning("Signature modèle non ajoutée: %s", e)


def _append_signature_to_stream_chunk(
    chunk: Any, routed_model: str, actual_model: str
) -> None:
    """
    Ajoute la signature (chemin de routage détaillé) au dernier chunk streaming.
    En streaming, actual = routed si pas d'info de fallback.
    """
    path = _get_routing_path(routed_model or "", actual_model or "")
    if not path:
        return
    path_str = _format_routing_path(path)
    try:
        choices = getattr(chunk, "choices", None) or []
        if not choices:
            return
        choice = choices[0]
        delta = getattr(choice, "delta", None)
        if delta is None:
            return
        content = getattr(delta, "content", None) or ""
        if not isinstance(content, str):
            content = str(content) if content else ""
        new_content = content + MODEL_SIGNATURE.format(path=path_str)
        setattr(delta, "content", new_content)
    except Exception as e:
        _logger.warning("Signature streaming non ajoutée: %s", e)


def _fix_tool_calls(response_obj):
    """
    Corrige les tool calls invalides dans la réponse (modifie en place).
    Option A : si un tool_call est irrécupérable, on le supprime pour éviter la boucle Roo.
    """
    try:
        choices = getattr(response_obj, "choices", None) or []
        for choice in choices:
            msg = getattr(choice, "message", None)
            if msg is None:
                continue
            tool_calls = getattr(msg, "tool_calls", None) or []
            if not tool_calls:
                continue

            valid_tcs = []
            for tc in tool_calls:
                try:
                    if _repair_ask_followup_tc(tc):
                        valid_tcs.append(tc)
                    # Si False (tc invalide) : on ne l'ajoute pas -> suppression
                except Exception as e:
                    _logger.warning("Post-call hook: tool_call non réparable, suppression: %s", e)
                    # Ne pas ajouter à valid_tcs

            msg.tool_calls = valid_tcs
    except Exception as e:
        _logger.error("Critical failure in post-call hook: %s", e)
        # Dernier recours : vider les tool_calls pour réponse texte
        try:
            for choice in getattr(response_obj, "choices", None) or []:
                msg = getattr(choice, "message", None)
                if msg is not None and getattr(msg, "tool_calls", None):
                    msg.tool_calls = []
        except Exception:
            pass
    return response_obj


class ToolSchemaEnforcer(CustomLogger):
    """
    Pre-call  : injecte TOOL_SCHEMA_PROMPT dans le system message.
    Post-call : répare les tool calls invalides (follow_up manquant/invalide).
    """

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        # Injection conditionnelle : uniquement si model worker-* et tools présents
        if not data.get("tools"):
            return data
        model = data.get("model") or ""
        if not model.startswith("worker-"):
            return data  # Architect, Ingest : pas de contrainte tool obligatoire
        messages = data.get("messages", [])
        if not messages:
            return data
        if messages[0].get("role") == "system":
            messages[0] = {
                "role": "system",
                "content": TOOL_SCHEMA_PROMPT + "\n\n" + (messages[0].get("content") or ""),
            }
        else:
            data["messages"] = [{"role": "system", "content": TOOL_SCHEMA_PROMPT}] + list(messages)
        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        """Répare les tool calls, signe avec modèle routé + modèle réel (non-streaming)."""
        _fix_tool_calls(response)
        data_dict = data or {}
        routed = _get_model_from_request_data(data_dict)
        actual = _get_model_for_signature(response, data_dict)
        if routed or actual:
            _append_model_signature(response, routed, actual)
        return response

    async def async_post_call_streaming_iterator_hook(
        self, user_api_key_dict, response, request_data
    ) -> AsyncGenerator[Any, None]:
        """
        Injecte la signature (modèle routé + modèle réel) sur le dernier chunk.
        En streaming, LiteLLM ne fournit pas le modèle réel en cas de fallback :
        on utilise le modèle routé pour les deux (identique si pas de fallback).
        """
        routed = _get_model_from_request_data(request_data or {})
        actual = routed  # fallback info non dispo dans le flux streaming
        async for chunk in response:
            try:
                choices = getattr(chunk, "choices", None) or []
                if choices:
                    finish_reason = getattr(choices[0], "finish_reason", None)
                    if finish_reason is not None and str(finish_reason).strip():
                        _append_signature_to_stream_chunk(chunk, routed, actual)
            except Exception as e:
                _logger.debug("Stream chunk skip signature: %s", e)
            yield chunk


proxy_handler_instance = ToolSchemaEnforcer()
