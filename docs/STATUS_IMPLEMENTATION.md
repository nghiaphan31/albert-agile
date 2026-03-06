# État d'implémentation — Écosystème Agile Agent IA

*Dernière mise à jour : 2026-03-06*

*Nomenclature : [specs/NOMENCLATURE_R_H_E.md](../specs/NOMENCLATURE_R_H_E.md) — Rôles (R-x), Interrupts (H-x), Phases (E-x).*

## Plan Calypso — Phases exécutées

| Phase | Statut | Détail |
|-------|--------|--------|
| 0 | ✅ | Python 3.12, Git, Docker, GPU NVIDIA (Calypso : RTX 5060 Ti 16G installé), Ollama |
| 1 | ✅ | Ollama, qwen2.5-coder:14b, qwen2.5:14b, nomic-embed-text, profil GPU (voir docs/HARDWARE_GPU.md) |
| 2 | ✅ | venv, langgraph/langchain/chroma/etc., config/projects.json, AGILE_* dans .bashrc |
| 3 | ✅ | setup_project_hooks.sh, handle_interrupt, purge_checkpoints, export/import_chroma, notify_pending_interrupts, status, index_rag |
| 4 | ✅ | graph/, serve.py, run_graph.py, SqliteSaver, LangServe |
| 5 | ✅ | .env.example, .env, LANGCHAIN_ENDPOINT (EU), clés API |
| 6 | ✅ | gh installé, gh auth login (nghiaphan31) |
| 7 | ✅ | VS Code, Remote-SSH, Continue.dev, Roo Code (PC) |
| 8 | ✅ | setup_project_hooks exécuté, index RAG (recherche sémantique) (442 chunks) |
| 9 | ✅ | LangServe OK, run_graph OK, status.py OK |
| 10 | ✅ | Lois, BaseStore, LLM cascade, anonymisation, interrupts H1-H6, tools, RAG, Self-Healing, L18 |

## Graphe LangGraph

- **Structure** : load_context → r0 (R-0 Albert Business Analyst) → r2 → r3 → r4 → r5 → r6 → END
- **Checkpointer** : SqliteSaver (checkpoints.sqlite)
- **Exposition** : uvicorn serve:app, path /agile
- **CLI** : `python run_graph.py --project-id albert-agile --start-phase E1`

## Agents (nœuds) — Implémentation Phase 10

- **LLM cascade** : N0 (Ollama) → N1 (Gemini) → N2 (Claude), H5 avant N2
- **interrupt()** : H1 (Epic), H2 (Architecture), H3 (Sprint Backlog), H4 (Sprint Review), H5 (escalade), L18 (spec_contradiction)
- **Tools** : graph/tools.py (read_file, write_file, run_shell), create_tools_r4/r5
- **RAG** : query_rag() dans R-2, R-3, R-4
- **BaseStore** : graph/basestore.py, load_context complet
- **Self-Healing** : R-6→R-4 si tests échouent (max 3), puis H5

## Scripts

| Script | État |
|--------|------|
| index_rag.py | ✅ Complet (Ollama nomic-embed-text, Chroma) |
| setup_project_hooks.sh | ✅ Complet (post-commit, .agile-env) |
| status.py | ✅ Fonctionnel |
| sync_artifacts.py | ✅ Complet |
| handle_interrupt.py | Stub (LangServe non branché) |
| purge_checkpoints.py | Stub |
| export_chroma.py | ✅ Fonctionnel |
| import_chroma.py | ✅ Fonctionnel |
| notify_pending_interrupts.py | Stub |

## Cron

- **sync_artifacts** : 0 0 * * 0 (dimanche minuit)
- **notify_pending_interrupts** : non configuré

## CI/CD

- GitHub Actions : `.github/workflows/ci.yml` (PR develop, main)
- gh authentifié

## Fichiers clés

- `graph/state.py`, `graph/nodes.py`, `graph/graph.py`, `graph/cascade.py`
- `serve.py`, `run_graph.py`
- `config/projects.json` : albert-agile
- `.env` : LANGCHAIN_TRACING_V2, LANGCHAIN_ENDPOINT (EU), LANGCHAIN_API_KEY, GOOGLE_API_KEY, ANTHROPIC_API_KEY
