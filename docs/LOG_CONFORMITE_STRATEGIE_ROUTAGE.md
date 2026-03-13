# Log — Conformité Stratégie Routage Intelligent

**Plan source :** Conformité Stratégie Routage Intelligent  
**Spec :** [specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md](../specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md)  
*Dernière mise à jour : 06/03/2026*

---

## Phase 0 — Création du fichier de log (06/03/2026)

- [x] Création du fichier `docs/LOG_CONFORMITE_STRATEGIE_ROUTAGE.md`

---

## Phase 1 — router_settings et corrections (06/03/2026)

- [x] 1.1 router_settings ajoutés — `config/litellm_config.yaml` : routing_strategy, allowed_fails: 3, cooldown_time: 3600
- [x] 1.2 Chemins callbacks corrigés — `config.custom_roo_hook.proxy_handler_instance`, `config.litellm_hooks.proxy_handler_instance`
- [x] 1.3 STATUS mis à jour — router_settings déplacé en Implémenté

---

## Phase 2 — Cascade Vertex/DeepSeek (06/03/2026)

- [x] 2.1 Fichier .env étendu — `.env.example` avec GEMINI_FREE_KEY, GEMINI_PAYANT_KEY, VERTEX_PROJECT, DEEPSEEK_API_KEY
- [x] 2.2 model_list refondu — `config/litellm_config_cascade_complete.yaml` (architect: Gemini→Vertex→DeepSeek, ingest: Gemini→Vertex→Payant, worker: Local→Gemini→DeepSeek)
- [x] 2.3 Option A adoptée — config séparée, `LITELLM_CONFIG=cascade_complete` dans `scripts/run_litellm_proxy.sh`
- [x] 2.4 STATUS mis à jour — Cascade Coût Zéro et Fallbacks Worker passés en Implémenté

---

## Phase 3 — Presidio (06/03/2026)

- [x] 3.1 Infrastructure Presidio (Docker) — docker-compose: presidio-analyzer (5002), presidio-anonymizer (5001)
- [x] 3.2 Configuration LiteLLM — callback presidio dans litellm_config.yaml et cascade
- [x] 3.3 Documentation — docs/PRESIDIO_SETUP.md

---

## Phase 4 — SearXNG (06/03/2026)

- [x] 4.1 Infrastructure SearXNG (Docker) — docker-compose, config/searxng/settings.yml (formats html+json)
- [x] 4.2 Tool LangChain search_web — create_search_web_tool(), SearxSearchWrapper
- [x] 4.3 Intégration graphe — search_web ajouté à create_tools_r4
- [x] 4.4 Documentation — docs/SEARXNG_SETUP.md

---

## Phase 5 — Sandboxing (06/03/2026)

- [x] 5.1 Conception image Docker — docker/sandbox/Dockerfile, image albert-sandbox
- [x] 5.2 Intégration run_shell sandboxed — graph/sandbox.py, run_shell utilise sandbox si AGILE_SANDBOX_RUN_SHELL et pytest
- [x] 5.3 Sécurité — --network none, volume limité, timeout

---

## Phase 6 — HITL WhatsApp (optionnel, 06/03/2026)

- [x] 6.1 Architecture Gateway — décrite dans docs/HITL_WHATSAPP_ROADMAP.md
- [x] 6.2 Composants — Baileys / API Business, mapping thread_id
- [x] 6.3 Documentation — roadmap, non implémenté (optionnel)

---

## Post-déploiement — dépendances (06/03/2026)

- [x] Installation `langchain-community` — requis pour SearxSearchWrapper (Phase 4)
  - Création venv `.venv` (environnement externe géré par l’OS)
  - `pip install langchain-community` dans `.venv`
- [x] Build image sandbox — `docker build -t albert-sandbox docker/sandbox` (utiliser si docker compose absent)
- [x] Script démarrage unifié — `scripts/start_services.sh` : lance Presidio + SearXNG (Docker) puis proxy LiteLLM en une commande (Roo / LangGraph)
- [x] Tâche VS Code auto — `.vscode/tasks.json` : tâche « Start services » avec runOn: folderOpen
- [x] Permission tâches auto — Ctrl+Shift+P → Tasks: Manage Automatic Tasks in Folder → Allow Automatic Tasks in Folder (une fois par workspace, pas à refaire à chaque démarrage)
- [x] Vérification run_graph — `run_graph.py` : si AGILE_USE_LITELLM_PROXY et proxy inaccessible, message clair + indication de lancer start_services.sh
