"""
LiteLLM hooks — deux stratégies pour fiabiliser le tool calling des LLMs locaux :

1. Pre-call  : injecte un rappel strict dans le system prompt (aide les modèles capables)
2. Post-call : répare les tool calls invalides dans la réponse (filet de sécurité)
              - ask_followup_question sans follow_up → on ajoute des suggestions génériques
              - follow_up non-array → on le convertit en array
              - Option A : si réparation impossible, supprime le tool_call (réponse texte safe)

Chargé via litellm_config.yaml (en 2e après custom_roo_hook) :
  litellm_settings:
    callbacks:
      - custom_roo_hook.proxy_handler_instance   # 1. HITL + routage
      - litellm_hooks.proxy_handler_instance     # 2. TOOL_SCHEMA_PROMPT (si model==worker)
"""
import json
import logging
from litellm.integrations.custom_logger import CustomLogger

_logger = logging.getLogger(__name__)

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
        # Injection conditionnelle : uniquement si model==worker et tools présents
        if not data.get("tools"):
            return data
        if data.get("model") != "worker":
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
        """Répare les tool calls invalides avant que la réponse soit renvoyée au client."""
        _fix_tool_calls(response)
        return response


proxy_handler_instance = ToolSchemaEnforcer()
