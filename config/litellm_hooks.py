"""
LiteLLM hooks — deux stratégies pour fiabiliser le tool calling des LLMs locaux :

1. Pre-call  : injecte un rappel strict dans le system prompt (aide les modèles capables)
2. Post-call : répare les tool calls invalides dans la réponse (filet de sécurité)
              - ask_followup_question sans follow_up → on ajoute des suggestions génériques
              - follow_up non-array → on le convertit en array

Chargé via litellm_config.yaml :
  litellm_settings:
    callbacks: ["litellm_hooks.proxy_handler_instance"]
"""
import json
import copy
from litellm.integrations.custom_logger import CustomLogger

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


def _fix_tool_calls(response_obj):
    """Corrige les tool calls invalides dans la réponse (modifie en place)."""
    try:
        choices = getattr(response_obj, "choices", None) or []
        for choice in choices:
            msg = getattr(choice, "message", None)
            if msg is None:
                continue
            tool_calls = getattr(msg, "tool_calls", None) or []
            for tc in tool_calls:
                fn = getattr(tc, "function", None)
                if fn is None:
                    continue
                name = getattr(fn, "name", "")
                if name != "ask_followup_question":
                    continue

                # Récupérer et parser les arguments
                raw_args = getattr(fn, "arguments", None) or "{}"
                if isinstance(raw_args, str):
                    try:
                        args = json.loads(raw_args)
                    except json.JSONDecodeError:
                        args = {}
                else:
                    args = raw_args if isinstance(raw_args, dict) else {}

                # Réparer follow_up si absent ou mauvais type
                follow_up = args.get("follow_up")
                if not isinstance(follow_up, list) or len(follow_up) == 0:
                    args["follow_up"] = DEFAULT_FOLLOW_UP
                    fn.arguments = json.dumps(args)
    except Exception:
        pass  # Ne jamais bloquer la réponse à cause du hook
    return response_obj


class ToolSchemaEnforcer(CustomLogger):
    """
    Pre-call  : injecte TOOL_SCHEMA_PROMPT dans le system message.
    Post-call : répare les tool calls invalides (follow_up manquant/invalide).
    """

    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        if not data.get("tools"):
            return data
        messages = data.get("messages", [])
        if not messages:
            return data
        if messages[0]["role"] == "system":
            messages[0] = {
                "role": "system",
                "content": TOOL_SCHEMA_PROMPT + "\n\n" + messages[0]["content"],
            }
        else:
            data["messages"] = [{"role": "system", "content": TOOL_SCHEMA_PROMPT}] + messages
        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        """Répare les tool calls invalides avant que la réponse soit renvoyée au client."""
        _fix_tool_calls(response)
        return response


proxy_handler_instance = ToolSchemaEnforcer()
