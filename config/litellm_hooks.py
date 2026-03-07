"""
LiteLLM pre-call hook — injecte un rappel strict sur les paramètres obligatoires
des tool calls pour les modèles Ollama (qui ont tendance à omettre des required fields).

Chargé via litellm_config.yaml :
  litellm_settings:
    callbacks: ["litellm_hooks.proxy_handler_instance"]
"""
from litellm.integrations.custom_logger import CustomLogger

TOOL_SCHEMA_PROMPT = """TOOL CALLING RULES — MANDATORY:
1. You MUST call exactly one tool per response.
2. You MUST provide ALL required parameters — never omit one.
3. Check the type of each parameter:
   - "array": must be a JSON list [ ] with at least 2 string elements
   - "string": must be a plain string
4. For "follow_up" (array of strings): always provide 2-4 suggested answers.
   CORRECT:   "follow_up": ["Yes, proceed", "No, cancel", "Give me more details"]
   INCORRECT: "follow_up": "Yes"  or omitting follow_up entirely
5. If the task is complete, use attempt_completion(result="...").
6. If you need clarification, use ask_followup_question(question="...", follow_up=[...]).
"""


class ToolSchemaEnforcer(CustomLogger):
    """Injecte TOOL_SCHEMA_PROMPT dans le system message quand des tools sont présents."""

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


proxy_handler_instance = ToolSchemaEnforcer()
