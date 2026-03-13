# Alignement Spec vs Code — Strategie Routage Intelligent

*Dernière mise à jour : 2026-03-08*

**Spec source :** [specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md](../specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md)

---

## Implémenté


| Élément Spec                                | Référence        | Implémentation                                                                                  |
| ------------------------------------------- | ---------------- | ----------------------------------------------------------------------------------------------- |
| Worker = qwen2.5-coder:14b                  | §1, §5.1         | `config/litellm_config.yaml` : worker → ollama/qwen2.5-coder:14b                                |
| HITL anti-boucle                            | §2               | `config/custom_roo_hook.py` : 3+ "error"/"failed" dans messages tool/user → STOP, alerte sonore |
| Routage sémantique                          | §5.2             | `config/custom_roo_hook.py` : nomic-embed-text, similarité cosinus, messages[-1]                |
| Fallback si score < seuil                   | Plan remédiation | `SIMILARITY_THRESHOLD = 0.4`, env `ROO_SIMILARITY_THRESHOLD`                                    |
| Catégories architect/ingest/worker          | §5.2             | Mêmes descriptions que dans la spec                                                             |
| HITL limité à tool/user                     | Plan remédiation | Filtrage `role in ("tool", "user")`                                                             |
| Ordre callbacks                             | §5.1             | 1. config.custom_roo_hook 2. config.litellm_hooks                                                |
| Injection conditionnelle TOOL_SCHEMA_PROMPT | §3.5, plan       | Uniquement si `model == "worker"`                                                               |
| Post-call (fake_stream + réparation)        | §3.5             | `config/litellm_hooks.py` : réparation follow_up, Option A (suppression si irréparable)         |
| fake_stream sur Ollama                      | §3.5             | `config/litellm_config.yaml` : fake_stream: true sur modèles Ollama                             |
| model_list architect/ingest/worker          | §5.1, §5.1b      | architect: Gemini→Vertex→DeepSeek ; ingest: Gemini→Vertex→Payant ; worker: Local→Gemini→DeepSeek |
| Risque Chroma                               | §C.9             | Documenté (Specs + Strategie)                                                                   |
| LangGraph via LiteLLM                       | Phase 3          | `graph/llm_factory`, `graph/cascade`, `docs/LANGGRAPH_VIA_LITELLM.md`                           |
| router_settings (model_cooldown_time, allowed_fails)   | §5.1b, §1.1      | `config/litellm_config.yaml` : model_cooldown_time: 61, allowed_fails: 3, cooldown_time: 3600  |
| Cascade Coût Zéro (Vertex, DeepSeek)                   | §5.1b            | `config/litellm_config.yaml` : architect/ingest/worker avec fallbacks Vertex et DeepSeek       |
| Fallbacks Worker (crash → Gemini, 429 → DeepSeek)      | §5.1b            | `config/litellm_config.yaml` : worker → worker-gemini → worker-deepseek                        |
| Presidio (anonymisation LiteLLM)                       | §10.1            | docker-compose, callback presidio, docs/PRESIDIO_SETUP.md                                      |
| SearXNG (recherche web)                               | §9               | docker-compose, create_search_web_tool, create_tools_r4, docs/SEARXNG_SETUP.md                  |


---

## Partiellement implémenté / Adapté


*Aucun élément en cours — voir Implémenté.*


---

## Non implémenté (hors périmètre actuel)


| Élément Spec                           | Section     |
| -------------------------------------- | ----------- |
| Vertex AI, DeepSeek, GEMINI_PAYANT_KEY | Optionnel : définir VERTEX_PROJECT, DEEPSEEK_API_KEY, GEMINI_PAYANT_KEY pour activer ces paliers |
| Sandboxing conteneurs (pytest)         | Implémenté  | graph/sandbox.py, docker/sandbox, docs/SANDBOXING_SETUP.md |
| HITL WhatsApp (Gateway)                | §7.2        | Optionnel, roadmap |


