# Plan — Reste Calypso (E2E, optionnels)

**Objectif** : Finaliser la validation E2E et, si souhaité, configurer les options chroma-mcp et LiteLLM.

**Référence** : [Implementation_Ecosysteme_Agile_Calypso.md](Implementation_Ecosysteme_Agile_Calypso.md), [CHECKLIST_E2E.md](../../docs/CHECKLIST_E2E.md).

**Terminal** : Toutes les commandes des tableaux ci-dessous sont à exécuter dans le **terminal intégré à VS Code** (panneau Terminal de l'IDE connecté à Calypso), sauf mention contraire.

---

## Vue d'ensemble

| Priorité | Élément | Effort | Dépendances |
|----------|---------|--------|-------------|
| **1** | Mettre à jour CHECKLIST_E2E.md | Faible | Exécuter les tests manquants (ou cocher les déjà validés) |
| **2** | Vérifier et cocher les cas E2E | Moyen | Ollama, venv, graphe |
| **3** | chroma-mcp (optionnel) | Moyen | chroma_db, index_rag |
| **4** | LiteLLM (optionnel) | Moyen | Ollama, clés API |

---

## 1. Mise à jour CHECKLIST_E2E.md

### 1.1 Exécuter les tests manquants

Avant de cocher, valider chaque cas sur Calypso. *Terminal : **intégré VS Code**.*

| # | Cas | Commande à exécuter | Cocher si OK |
|---|-----|---------------------|--------------|
| **1.1** | Ollama actif | `ollama list` | qwen2.5-coder:14b, qwen2.5:14b, nomic-embed-text présents |
| **1.2** | Import graphe | `cd albert-agile && source .venv/bin/activate && python -c "from graph.graph import graph; print('OK')"` | OK affiché |
| **1.3** | projects.json | Vérifier `config/projects.json` | albert-agile présent |
| **1.4** | Prereq script | `python scripts/test_e2e_manual.py --check-prereq` | PREREQ OK |
| **2.1** | Lancement E1 | `python run_graph.py --project-id albert-agile --start-phase E1 --thread-id albert-agile-e2e-check` | Graphe suspendu sur H1 |
| **2.2** | Liste interrupts | `python scripts/handle_interrupt.py` | thread_id listé |
| **2.3** | Validation H1 | `python scripts/handle_interrupt.py --thread-id albert-agile-e2e-check --approved` | Graphe repris |
| **2.4** | Rejet H1 + feedback | Nouveau run E1 (thread différent), puis `--rejected --feedback "Revoir le scope"` | Graphe reboucle vers r0 |
| **4.1** | HOTFIX | `python run_graph.py --project-id albert-agile --start-phase HOTFIX --thread-id albert-agile-hotfix-test --hotfix-description "Correction bug critique"` | HF-001 créé, route vers r4 |
| **5.1** | status.py | `python scripts/status.py` | albert-agile listé avec interrupts, pending_index |
| **5.2** | status.py JSON | `python scripts/status.py --json` | JSON valide |
| **6.1** | LangServe | `uvicorn serve:app --host 0.0.0.0 --port 8000` (en arrière-plan) | Serveur démarre sans erreur |
| **7.1** | pytest | `pytest tests/test_e2e_graph.py -v` | Tous les tests passent |

### 1.2 Modifier CHECKLIST_E2E.md

Remplacer `☐` par `☑` pour chaque cas validé dans [docs/CHECKLIST_E2E.md](../../docs/CHECKLIST_E2E.md).

---

## 2. chroma-mcp (optionnel)

RAG partagé IDE + agents. Continue.dev, Roo Code et Cursor peuvent interroger le même Chroma que les nœuds LangGraph.

### 2.1 Installer chroma-mcp

*Dans le **terminal intégré à VS Code** (depuis la racine du projet / venv activé) :*

```bash
cd /home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile
source .venv/bin/activate
pip install chroma-mcp
```

### 2.2 Configurer dans Continue et Roo Code

- Chemin Chroma : `$AGILE_ORCHESTRATION_ROOT/chroma_db` (ex. `/home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile/chroma_db`)
- **Continue** : ajouter chroma-mcp dans mcpServers (config.yaml sur PC Windows). Voir doc [Continue MCP](https://docs.continue.dev/customize/mcp-tools).
- **Roo Code** : configurer chroma-mcp dans `.roo/mcp.json` (projet) ou config globale. Voir doc [Roo Code MCP](https://docs.roocode.com/features/mcp/overview).

### 2.3 Vérification

- Dans Continue et Roo Code, une requête doit pouvoir utiliser le contexte RAG (chroma_query_documents) pour le projet.

### 2.4 Mettre à jour requirements.txt (optionnel)

Si on veut tracer la dépendance : ajouter `chroma-mcp` dans un fichier `requirements-optional.txt` ou dans `requirements.txt`.

---

## 3. LiteLLM (optionnel)

Proxy de routage automatique : choix du modèle selon la tâche, cascade local → Gemini → Claude.

### 3.1 Installer LiteLLM

*Dans le **terminal intégré à VS Code** (depuis la racine du projet / venv activé) :*

```bash
pip install 'litellm[proxy]'
```

### 3.2 Créer config.yaml

Fichier `config/litellm_config.yaml` (exemple) :

```yaml
model_list:
  - model_name: ollama-qwen-coder
    litellm_params:
      model: ollama/qwen2.5-coder:14b
  - model_name: ollama-qwen
    litellm_params:
      model: ollama/qwen2.5:14b
  - model_name: gemini-flash
    litellm_params:
      model: gemini/gemini-2.5-flash
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-20250514
```

### 3.3 Lancer le proxy

```bash
litellm --config config/litellm_config.yaml --port 4000
```

### 3.4 Configurer Continue / Roo Code

- Provider : OpenAI (compatible)
- Base URL : `http://localhost:4000`
- Modèle : `ollama-qwen-coder` (ou modèle virtuel de routage)

### 3.5 Documenter

Mettre à jour [Plan_Configuration_VSCode_Ollama_Local.md](Plan_Configuration_VSCode_Ollama_Local.md) et [docs/STATUS_IMPLEMENTATION.md](../../docs/STATUS_IMPLEMENTATION.md) si LiteLLM est déployé.

---

## 4. Ordre d'exécution recommandé

1. **Phase A** (obligatoire)  
   - Exécuter les tests 1.1–1.4, 2.1–2.4, 4.1, 5.1–5.2, 6.1, 7.1  
   - Mettre à jour CHECKLIST_E2E.md

2. **Phase B** (optionnel)  
   - chroma-mcp : installation + config Continue  
   - LiteLLM : installation + config + doc

3. **Phase C** (finalisation)  
   - Commit avec message détaillé  
   - Mettre à jour STATUS_IMPLEMENTATION.md si chroma-mcp ou LiteLLM sont configurés

---

## 5. Fichiers impactés

| Fichier | Action |
|---------|--------|
| docs/CHECKLIST_E2E.md | Cocher les cas validés |
| requirements.txt ou requirements-optional.txt | Ajouter chroma-mcp, litellm si utilisés |
| config/litellm_config.yaml | Créer si LiteLLM activé |
| docs/STATUS_IMPLEMENTATION.md | Mettre à jour section Cron / optionnels |
| specs/plans/Plan_Configuration_VSCode_Ollama_Local.md | Référencer LiteLLM / chroma-mcp |
