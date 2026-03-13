# Modes Bootstrap et Runtime cible — Parcours et type de terminal

**Objectif** : Document de référence pour qui fait quoi, où (IDE vs terminal), quel type de terminal (intégré VS Code / Cursor vs externe), et les critères de maturité pour basculer du bootstrap au runtime.

**Références** : [Plan_Configuration_VSCode_Ollama_Local.md](Plan_Configuration_VSCode_Ollama_Local.md), [Implementation_Ecosysteme_Agile_Calypso.md](Implementation_Ecosysteme_Agile_Calypso.md), [Specifications Ecosysteme Agile Agent IA.md](../Specifications%20Ecosysteme%20Agile%20Agent%20IA.md), [Plan_Harmonisation_Documents_Terminal.md](Plan_Harmonisation_Documents_Terminal.md).

---

## 1. Convention terminal

| Désignation | Signification |
|-------------|---------------|
| **Terminal intégré à VS Code** | Panneau **Terminal** de VS Code (Ctrl+` / View → Terminal). En Remote-SSH, les commandes s'exécutent sur la machine distante (ex. Calypso). Une seule fenêtre IDE. |
| **Terminal intégré à Cursor** | Même chose dans Cursor : panneau Terminal de Cursor (bootstrap). |
| **Terminal externe (hors IDE)** | Terminal système (gnome-terminal, Konsole, etc.) ou client SSH séparé (PuTTY, `ssh user@calypso` dans un terminal hors IDE). |

**Règle** : Pour `run_graph.py`, `handle_interrupt.py`, `status.py`, et toute commande liée au flux Agile, utiliser explicitement le **terminal intégré à VS Code** (ou **terminal intégré à Cursor** en bootstrap), sauf usage volontaire d'un terminal externe.

---

## 2. Critères de maturité et bascule Bootstrap → Runtime

### Objectif

Définir **quand** et **selon quels critères** on considère que l'écosystème est assez mûr pour passer du **mode bootstrap** (IDE = Cursor) au **mode runtime cible** (IDE = VS Code + Continue.dev + Roo Code).

### Critères de maturité (prérequis à la bascule)

| # | Critère | Vérification |
|---|---------|--------------|
| M1 | **Phases 0 à 6 terminées** | Ollama, venv, LangGraph/scripts (run_graph, handle_interrupt, status, index_rag, hooks), graphe opérationnel, clés API cloud, CI (gh, GitHub Actions) |
| M2 | **Phase 7 réalisée** | VS Code installé sur le PC, extension Remote-SSH, connexion à Calypso OK ; extensions Continue.dev et Roo Code installées et configurées (au moins Ollama) |
| M3 | **Phase 8 réalisée** | `setup_project_hooks.sh` exécuté pour le projet ; `.agile-project-id`, `.agile-env` présents ; index RAG initial créé |
| M4 | **Plan de test pré-bascule validé** | Tests automatiques A1–A2 + tests manuels Ma1–Ma4 validés (voir section 3) |
| M5 | **Décision métier** | Tu vises le **travail quotidien** (priorisation backlog, validation H1–H4, sparring idéation) plutôt que la poursuite de l'implémentation / debug du graphe |

### Moment pour passer en mode runtime

- **Quand** : Dès que M1–M5 sont remplis.
- **Comment** : Ouvrir VS Code, se connecter à Calypso en Remote-SSH, ouvrir le dossier du projet orchestration, utiliser le **terminal intégré à VS Code** pour les commandes, et le **chat Continue ou Roo Code** pour l'idéation.
- **Retour en bootstrap** : Si un correctif majeur sur le graphe ou les scripts est nécessaire, retravailler sous Cursor (terminal intégré Cursor) puis revalider sous VS Code.

---

## 3. Plan de test pré-bascule

Avant de considérer M4 comme satisfait, exécuter le plan de test ci-dessous. **Ordre recommandé** : tests automatiques d'abord, puis tests manuels.

### Tests automatiques

| # | Commande | Condition de succès |
|---|----------|---------------------|
| A1 | `python scripts/test_e2e_manual.py --check-prereq` | Exit code 0, message « PREREQ OK » |
| A2 | `python scripts/test_e2e_manual.py --all --timeout 180` | Exit code 0, prereq + E1 + list + status OK |
| A3 | `pytest tests/test_e2e_graph.py -v` | Tous les tests passent (exit code 0) |

**Exécution** : terminal intégré à Cursor (bootstrap) ou à VS Code, depuis la racine du projet avec venv activé.

### Tests manuels (à cocher)

| # | Cas | Commande / action |
|---|-----|-------------------|
| Ma1 | Lancement E1 | `python run_graph.py --project-id albert-agile --start-phase E1 --thread-id albert-agile-phase-0` |
| Ma2 | Liste interrupts | `python scripts/handle_interrupt.py` |
| Ma3 | Validation H1 | `python scripts/handle_interrupt.py --thread-id albert-agile-phase-0 --approved` |
| Ma4 | status.py | `python scripts/status.py` |

**Condition** : tous les cas Ma1–Ma4 validés (graphe suspendu sur H1, liste interrupts, graphe repris après approved, status affiche le projet).

**Optionnel pour bascule** (recommandé mais non bloquant) : rejet H1 + feedback (§ 2.4 CHECKLIST_E2E), status --json (§ 5.2), HOTFIX (§ 4.1).

### Synthèse

- **Minimum pour M4** : A1 + A2 verts, et Ma1–Ma4 manuels cochés. A3 (pytest) peut être reporté si les tests ne couvrent pas encore le flux critique.
- **Idéal** : A1 + A2 + A3 verts, et Ma1–Ma4 (voire § 2.4, 5.2, 4.1) cochés.

---

## 4. Bootstrap (Cursor)

- **IDE** : Cursor
- **Terminal** : **terminal intégré à Cursor** pour toutes les commandes (install, run_graph, handle_interrupt, status, pytest, etc.)
- Pas d'obligation d'utiliser un terminal externe

---

## 5. Runtime cible (VS Code + Continue + Roo Code)

- **IDE** : VS Code (Remote-SSH sur Calypso), chat Continue / Roo Code
- **Lancement du flux Agile** : `run_graph.py` depuis le **terminal intégré à VS Code**
- **Idéation (sparring)** : dans le **chat Continue ou Roo Code** (pas dans le terminal)
- **Validation des interrupts (H1–H6)** : `handle_interrupt.py` depuis le **terminal intégré à VS Code** (approbation/rejet + feedback)
- **Consultation du statut** : `status.py` depuis le **terminal intégré à VS Code**
- **Optionnel** : LangServe Playground dans le **navigateur** (`http://localhost:8000/agile/playground`)
- **Optionnel** : notification interrupt > 48h : script cron (environnement système) ; la réaction humaine reste via `handle_interrupt.py` dans le **terminal intégré à VS Code**

---

## 6. Tableau récapitulatif

| Action | Où | Type terminal | Remarque |
|--------|-----|---------------|----------|
| Lancer run_graph.py | VS Code | Intégré VS Code | — |
| handle_interrupt (liste / approuver / rejeter) | VS Code | Intégré VS Code | — |
| status.py | VS Code | Intégré VS Code | — |
| Idéation / sparring | VS Code | Chat Continue/Roo Code | Pas terminal |
| Playground | Navigateur | — | optionnel |
| notify_pending (cron) | Système | Cron / terminal système | Lecture des interrupts : terminal intégré VS Code |
