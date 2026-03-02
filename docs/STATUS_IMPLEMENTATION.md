# État d'implémentation — Écosystème Agile Agent IA

*Dernière mise à jour : 2026-03-02*

*Nomenclature : [specs/NOMENCLATURE_R_H_E.md](../specs/NOMENCLATURE_R_H_E.md) — Rôles (R-x), Interrupts (H-x), Phases (E-x).*

## Plan Calypso — Phases exécutées

| Phase | Statut | Détail |
|-------|--------|--------|
| 0 | ✅ | Python 3.12, Git, Docker, NVIDIA RTX 3060, Ollama |
| 1 | ✅ | Ollama, qwen2.5-coder:7b, gemma3:12b-it-q4_K_M, nomic-embed-text, OLLAMA_KEEP_ALIVE |
| 2 | ✅ | venv, langgraph/langchain/chroma/etc., config/projects.json, AGILE_* dans .bashrc |
| 3 | ✅ | setup_project_hooks.sh, handle_interrupt, purge_checkpoints, export/import_chroma, notify_pending_interrupts, status, index_rag |
| 4 | ✅ | graph/, serve.py, run_graph.py, SqliteSaver, LangServe |
| 5 | ✅ | .env.example, .env, LANGCHAIN_ENDPOINT (EU), clés API |
| 6 | ✅ | gh installé, gh auth login (nghiaphan31) |
| 7 | ✅ | VS Code, Remote-SSH, Continue.dev, Roo Code (PC) |
| 8 | ✅ | setup_project_hooks exécuté, index RAG (recherche sémantique) (442 chunks) |
| 9 | ✅ | LangServe OK, run_graph OK, status.py OK |
| 10 | ⏳ | Implémentation réelle des agents (voir plan Phase 10) |

## Graphe LangGraph

- **Structure** : load_context → r0 (R-0 Albert Business Analyst) → r2 → r3 → r4 → r5 → r6 → END
- **Checkpointer** : SqliteSaver (checkpoints.sqlite)
- **Exposition** : uvicorn serve:app, path /agile
- **CLI** : `python run_graph.py --project-id albert-agile --start-phase E1`

## Agents (nœuds) — Stubs

Les nœuds R-0 (Albert Business Analyst) à R-6 (Albert QA & DevOps) existent mais retournent des messages statiques. Non implémenté :
- Appels LLM (cascade N0 (local Ollama)→N1 (cloud gratuit)→N2 (cloud payant))
- interrupt() H1 (validation Gros Ticket)–H6 (résolution conflit Git)
- Tools R-4 (Albert Dev Team)/R-5 (Albert Release Manager) (read_file, write_file, run_shell)
- RAG (recherche sémantique) Chroma, BaseStore (mémoire long terme)
- load_context complet (routing E1 (idéation)/E3 (Sprint Backlog)/HOTFIX (correctif urgent))

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
