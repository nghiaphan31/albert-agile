# Checklist E2E — Écosystème Agile

Plan formel des cas de validation pour les tests end-to-end. À cocher manuellement ou via `scripts/test_e2e_manual.py`.

**Référence** : [Plan Calypso Phase 9](../specs/plans/Implementation_Ecosysteme_Agile_Calypso.md#phase-9--validation-end-to-end), [Guide utilisateur](../specs/plans/Implementation_Ecosysteme_Agile_Calypso.md#guide-utilisateur-basique--initier-un-projet-de-développement).

**Terminal** : Les commandes de cette checklist sont à exécuter dans le **terminal intégré à VS Code** (ou Cursor en bootstrap), panneau Terminal de l'IDE. Ne pas utiliser un terminal externe (ex. SSH dans une autre fenêtre) sauf besoin explicite.

---

## 1. Prérequis

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 1.1 | Ollama actif | `ollama list` | qwen2.5-coder:14b, qwen2.5:14b, nomic-embed-text (option : qwen3:14b) | ☐ |
| 1.2 | Venv + import graphe | `python -c "from graph.graph import graph; print('OK')"` | OK affiché | ☐ |
| 1.3 | config/projects.json | Vérifier existence et format | albert-agile présent | ☐ |
| 1.4 | Script test prereq | `python scripts/test_e2e_manual.py --check-prereq` | PREREQ OK | ☐ |

---

## 2. Phase E1 (Idéation)

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 2.1 | Lancement E1 | `python run_graph.py --project-id albert-agile --start-phase E1 --thread-id albert-agile-phase-0` | Graphe suspendu sur H1, message "handle_interrupt" | ☐ |
| 2.2 | Liste interrupts | `python scripts/handle_interrupt.py` | thread_id albert-agile-phase-0 listé | ☐ |
| 2.3 | Validation H1 | `python scripts/handle_interrupt.py --thread-id albert-agile-phase-0 --approved` | Graphe repris, atteint H2 ou termine | ☐ |
| 2.4 | Rejet H1 + feedback | Lancer E1, puis `--rejected --feedback "Revoir le scope"` | Graphe reboucle vers r0 | ☐ |

---

## 3. Phase E3 (Sprint Backlog)

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 3.1 | Lancement E3 | `python run_graph.py --project-id albert-agile --start-phase E3 --thread-id albert-agile-sprint-01` | Graphe suspendu sur H3 | ☑ |
| 3.2 | Validation H3 | `handle_interrupt.py --thread-id albert-agile-sprint-01 --approved` | Graphe poursuit vers r4 | ☑ |

---

## 4. Phase HOTFIX

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 4.1 | Lancement HOTFIX | `python run_graph.py --project-id albert-agile --start-phase HOTFIX --thread-id albert-agile-hotfix-001 --hotfix-description "Correction bug critique"` | load_context crée HF-001, route vers r4 | ☐ |

---

## 5. Scripts et statut

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 5.1 | status.py | `python scripts/status.py` | Liste projets (albert-agile) | ☐ |
| 5.2 | status.py JSON | `python scripts/status.py --json` | JSON valide avec project_id, pending_index | ☐ |

---

## 6. LangServe (optionnel)

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 6.1 | Démarrage serveur | `uvicorn serve:app --host 0.0.0.0 --port 8000` | Serveur démarre sans erreur | ☐ |
| 6.2 | Playground | Ouvrir http://localhost:8000/agile/playground/ | Interface accessible | ☑ |

---

## 7. Tests automatisés (pytest)

| # | Cas | Commande / Action | Résultat attendu | ☐ |
|---|-----|-------------------|------------------|---|
| 7.1 | Tests E2E | `pytest tests/test_e2e_graph.py -v` | Tous les tests passent | ☐ |

---

## 8. Débogage

| # | Outil | Usage |
|---|-------|-------|
| 8.1 | LangSmith | `LANGCHAIN_TRACING_V2=true` + clé API → traces sur smith.langchain.com |
| 8.2 | checkpoints.sqlite | État persistant du graphe |
| 8.3 | logs/index_rag_*.log | Logs d'indexation RAG |
| 8.4 | AGILE_BASESTORE_STRICT=false | Mode dégradé si BaseStore absent |

---

## Commande rapide

```bash
# Vérification complète (prereq + E1 + list + status)
python scripts/test_e2e_manual.py --all --timeout 180

# Avec validation H1 automatique
python scripts/test_e2e_manual.py --all --approved --timeout 180
```
