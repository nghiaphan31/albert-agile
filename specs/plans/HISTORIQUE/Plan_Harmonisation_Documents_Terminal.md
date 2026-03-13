# Plan — Mise à jour des documents (terminal + harmonisation)

**Objectif** : Mettre à jour tous les documents applicables pour (1) préciser systématiquement le type de terminal (intégré VS Code vs externe), (2) harmoniser avec la synthèse de la discussion récente (parcours runtime, idéation, approbation/rejet).

**Références** : Synthèse discussion (terminal intégré VS Code recommandé partout ; idéation dans le chat Continue/Roo Code ; validation H1–H6 via `handle_interrupt.py` dans le terminal intégré).

---

## Convention à appliquer partout

| Désignation | Signification |
|-------------|----------------|
| **Terminal intégré à VS Code** | Panneau **Terminal** de VS Code (Ctrl+` / View → Terminal). En Remote-SSH, les commandes s’exécutent sur la machine distante (ex. Calypso). Une seule fenêtre IDE. |
| **Terminal intégré à Cursor** | Même chose dans Cursor : panneau Terminal de Cursor (bootstrap). |
| **Terminal externe (hors IDE)** | Terminal système (gnome-terminal, Konsole, etc.) ou client SSH séparé (PuTTY, `ssh user@calypso` dans un terminal hors IDE). |

**Règle** : Pour `run_graph.py`, `handle_interrupt.py`, `status.py`, et toute commande liée au flux Agile, le document doit indiquer explicitement **« terminal intégré à VS Code »** (ou **« terminal intégré à Cursor »** en phase bootstrap), sauf si le cas d’usage est volontairement « terminal externe ».

---

## Critères de maturité et moment de bascule Bootstrap → Runtime

### Objectif

Définir **quand** et **selon quels critères** on considère que l’écosystème est assez mûr pour passer du **mode bootstrap** (IDE = Cursor) au **mode runtime cible** (IDE = VS Code + Continue.dev + Roo Code).

### Critères de maturité (prérequis à la bascule)

La bascule est envisageable lorsque **tous** les points suivants sont satisfaits :

| # | Critère | Vérification | Référence |
|---|---------|--------------|-----------|
| M1 | **Phases 0 à 6 terminées** | Ollama, venv, LangGraph/scripts (run_graph, handle_interrupt, status, index_rag, hooks), graphe opérationnel, clés API cloud, CI (gh, GitHub Actions) | Implementation_Ecosysteme_Agile_Calypso.md Phases 0–6 |
| M2 | **Phase 7 réalisée** | VS Code installé sur le PC, extension Remote-SSH, connexion à Calypso OK ; extensions Continue.dev et Roo Code installées et configurées (au moins Ollama) | Plan_Configuration_VSCode_Ollama_Local.md |
| M3 | **Phase 8 réalisée** | `setup_project_hooks.sh` exécuté pour le projet (ex. albert-agile) ; `.agile-project-id`, `.agile-env` présents ; index RAG initial créé | Implementation Phase 8 |
| M4 | **Plan de test pré-bascule validé** | Tests automatiques et manuels exécutés et verts (voir [§ Plan de test pré-bascule](#plan-de-test-pré-bascule)) | Voir tableau ci-dessous |
| M5 | **Décision métier** | Tu vises le **travail quotidien** (priorisation backlog, validation H1–H4, sparring idéation) plutôt que la poursuite de l’implémentation / debug du graphe | — |

**Résumé** : Maturité = Phases 0–8 faites + plan de test pré-bascule validé + volonté de basculer vers le flux produit (VS Code comme IDE principal).

### Plan de test pré-bascule

Avant de considérer M4 comme satisfait, exécuter le plan de test ci-dessous. **Ordre recommandé** : tests automatiques d’abord, puis tests manuels.

#### Tests automatiques

| # | Commande | Condition de succès | Référence |
|---|----------|---------------------|-----------|
| A1 | `python scripts/test_e2e_manual.py --check-prereq` | Exit code 0, message « PREREQ OK » | CHECKLIST_E2E § 1.4 |
| A2 | `python scripts/test_e2e_manual.py --all --timeout 180` | Exit code 0, prereq + E1 + list + status OK | CHECKLIST_E2E § Commande rapide |
| A3 | `pytest tests/test_e2e_graph.py -v` | Tous les tests passent (exit code 0) | CHECKLIST_E2E § 7.1 |

**Exécution** : terminal intégré à Cursor (bootstrap) ou à VS Code, depuis la racine du projet avec venv activé.

#### Tests manuels (à cocher)

| # | Cas | Commande / action | Référence CHECKLIST_E2E |
|---|-----|-------------------|-------------------------|
| Ma1 | Lancement E1 | `python run_graph.py --project-id albert-agile --start-phase E1 --thread-id albert-agile-phase-0` | § 2.1 |
| Ma2 | Liste interrupts | `python scripts/handle_interrupt.py` | § 2.2 |
| Ma3 | Validation H1 | `python scripts/handle_interrupt.py --thread-id albert-agile-phase-0 --approved` | § 2.3 |
| Ma4 | status.py | `python scripts/status.py` | § 5.1 |

**Condition** : tous les cas Ma1–Ma4 validés (graphe suspendu sur H1, liste interrupts, graphe repris après approved, status affiche le projet).

**Optionnel pour bascule** (recommandé mais non bloquant) : § 2.4 (rejet H1 + feedback), § 5.2 (status --json), § 4.1 (HOTFIX).

#### Synthèse

- **Minimum pour critère M4** : A1 + A2 verts, et Ma1–Ma4 manuels cochés. A3 (pytest) peut être reporté si les tests ne couvrent pas encore le flux critique.
- **Idéal** : A1 + A2 + A3 verts, et Ma1–Ma4 (voire § 2.4, 5.2, 4.1) cochés.

### Moment pour passer en mode runtime

- **Quand** : Dès que les critères M1–M5 sont remplis, dont le **plan de test pré-bascule** (tests automatiques A1–A2 + tests manuels Ma1–Ma4 au minimum).
- **Comment** : Ouvrir VS Code, se connecter à Calypso en Remote-SSH, ouvrir le dossier du projet orchestration, utiliser le **terminal intégré à VS Code** pour `run_graph.py` / `handle_interrupt.py` / `status.py`, et le **chat Continue ou Roo Code** pour l’idéation. Cursor reste utilisable en parallèle pour du bootstrap ou du debug si besoin.
- **Retour en bootstrap** : Si un correctif majeur sur le graphe ou les scripts est nécessaire, tu peux retravailler sous Cursor (terminal intégré Cursor) puis revalider sous VS Code.

### À documenter dans Modes_Bootstrap_et_Runtime_Cible.md

Le document **Modes_Bootstrap_et_Runtime_Cible.md** (détail doc 8) doit inclure :
- une section **« Critères de maturité et bascule Bootstrap → Runtime »** reprenant le tableau M1–M5 et la définition du moment de bascule ;
- une section **« Plan de test pré-bascule »** reprenant les tableaux Tests automatiques (A1–A3) et Tests manuels (Ma1–Ma4), ainsi que la synthèse (minimum vs idéal), afin que ce soit la référence unique pour toute la doc.

---

## Documents concernés et ordre de mise à jour

L’ordre respecte les dépendances : d’abord le document de référence « convention », puis les specs, puis les plans et checklists.

| # | Document | Priorité | Contenu à ajouter/modifier |
|---|----------|----------|-----------------------------|
| 1 | **specs/plans/Plan_Harmonisation_Documents_Terminal.md** (ce fichier) | — | Conserver ce plan comme référence. |
| 2 | **specs/Specifications Ecosysteme Agile Agent IA.md** | 1 | Voir [§ Détail doc 2](#détail-doc-2-specifications-ecosysteme-agile-agent-ia) |
| 3 | **specs/plans/Implementation_Ecosysteme_Agile_Calypso.md** | 2 | Voir [§ Détail doc 3](#détail-doc-3-implementation_ecosysteme_agile_calypso) |
| 4 | **specs/plans/Plan_Configuration_VSCode_Ollama_Local.md** | 3 | Voir [§ Détail doc 4](#détail-doc-4-plan_configuration_vscode_ollama_local) |
| 5 | **specs/plans/Plan_Reste_Calypso_E2E_Optionnels.md** | 4 | Voir [§ Détail doc 5](#détail-doc-5-plan_reste_calypso_e2e_optionnels) |
| 6 | **docs/CHECKLIST_E2E.md** | 5 | Voir [§ Détail doc 6](#détail-doc-6-checklist_e2e) |
| 7 | **docs/STATUS_IMPLEMENTATION.md** | 6 | Voir [§ Détail doc 7](#détail-doc-7-status_implementation) |
| 8 | **specs/plans/Modes_Bootstrap_et_Runtime_Cible.md** (nouveau) | 7 | Parcours + **critères de maturité et bascule Bootstrap → Runtime** + tableau récap (voir § Détail doc 8) |

---

## Détail par document

### Détail doc 2 — Specifications Ecosysteme Agile Agent IA.md

- **Nomenclature 4D (début du doc)**  
  - Après la phrase qui définit SOURCE > APP > VUE → CIBLE, ajouter une sous-section courte **« VUE Terminal »** :  
    - *Terminal* dans la VUE désigne par défaut le **terminal intégré à l’IDE** (VS Code ou Cursor : panneau Terminal).  
    - Pour un terminal **externe** (hors IDE), préciser explicitement : *Terminal externe* ou *SSH hors IDE*.
- **Section III.8 (Procédures opérationnelles)**  
  - Partout où apparaissent les commandes `run_graph.py`, `handle_interrupt.py`, `status.py` :  
    - Préciser : *À exécuter dans le **terminal intégré à VS Code** (panneau Terminal de l’IDE), sauf usage volontaire d’un terminal externe.*  
  - Pour **Exécution** de handle_interrupt (endpoint LangServe vs script) :  
    - Indiquer que le script est utilisé depuis le **terminal intégré à VS Code** ; le playground LangServe s’ouvre dans le **navigateur**.
- **Notification interrupt > 48h**  
  - Pour « affichage terminal » : préciser *affichage dans le terminal qui exécute le script cron* (souvent terminal système / cron, pas IDE). Optionnel : préciser que la consultation des interrupts par l’humain se fait via `handle_interrupt.py` dans le **terminal intégré VS Code**.
- **Références croisées**  
  - Ajouter une référence vers le document **Modes_Bootstrap_et_Runtime_Cible.md** (parcours runtime détaillé) une fois celui-ci créé (section « Interface et Orchestration » ou équivalent).

---

### Détail doc 3 — Implementation_Ecosysteme_Agile_Calypso.md

- **Conventions (début)**  
  - Dans le tableau SOURCE / APP / VUE / CIBLE, en note sous VUE :  
    - *Terminal = **terminal intégré** à Cursor (bootstrap) ou à VS Code (runtime cible)** ; pas un terminal externe (SSH dans une autre fenêtre).*
  - Règle d’exécution : remplacer ou compléter par :  
    - *Les commandes dans le **terminal intégré à Cursor** (panneau Terminal) s’exécutent sur Calypso. En runtime cible, on utilise le **terminal intégré à VS Code** de la même façon.*
- **Bootstrap vs Cible**  
  - Préciser :  
    - Bootstrap : commandes (run_graph, handle_interrupt, status, etc.) dans le **terminal intégré à Cursor**.  
    - Cible : commandes dans le **terminal intégré à VS Code** ; idéation/sparring dans le **chat Continue ou Roo Code** (pas dans le terminal).
- **Chaque occurrence « [ PC > Cursor > Terminal ] »**  
  - Remplacer ou compléter par : *[ PC > Cursor > **Terminal intégré** ] → (Calypso)* pour éviter toute ambiguïté.
- **Phase 7 (IDE cible)**  
  - Ajouter une phrase : pour le travail quotidien (R-1, R-7), le lancement du graphe et la validation des interrupts se font depuis le **terminal intégré à VS Code** ; l’idéation se fait dans le chat Continue/Roo Code.
  - **Bascule Bootstrap → Runtime** : Ajouter une phrase ou un renvoi : le moment pour passer de Cursor (bootstrap) à VS Code (runtime cible) est défini par les **critères de maturité** (Phases 0–8 + E2E minimal + décision métier) ; voir [Plan_Harmonisation_Documents_Terminal.md](Plan_Harmonisation_Documents_Terminal.md) § Critères de maturité et [Modes_Bootstrap_et_Runtime_Cible.md](Modes_Bootstrap_et_Runtime_Cible.md).

---

### Détail doc 4 — Plan_Configuration_VSCode_Ollama_Local.md

- **Section 2.3 (Connexion à Calypso)**  
  - La phrase « Le Terminal intégré exécute les commandes **sur Calypso** » est déjà correcte. La rendre encore explicite :  
    - *Le **terminal intégré à VS Code** (panneau Terminal, Ctrl+`) exécute les commandes **sur Calypso** (contexte Remote-SSH). Ce n’est pas un terminal externe (ex. SSH dans une autre fenêtre).*
- **Nouvelle sous-section après 2.3**  
  - **2.4 Convention terminal pour la suite**  
    - Toutes les commandes décrites dans ce plan (vérifications, `ollama list`, éventuellement LiteLLM, etc.) sont à exécuter dans le **terminal intégré à VS Code**. Pour l’exécution du graphe Agile (`run_graph.py`, `handle_interrupt.py`, `status.py`), voir [Modes_Bootstrap_et_Runtime_Cible.md](Modes_Bootstrap_et_Runtime_Cible.md) (ou Plan_Reste_Calypso_E2E_Optionnels.md).
- **Section 5 (Vérification)**  
  - Pour 5.5 (`ollama ps`) : préciser *Dans le **terminal intégré à VS Code** connecté à Calypso.*

---

### Détail doc 5 — Plan_Reste_Calypso_E2E_Optionnels.md

- **En-tête (après Vue d’ensemble)**  
  - Ajouter une phrase :  
    - *Toutes les commandes des tableaux ci-dessous sont à exécuter dans le **terminal intégré à VS Code** (panneau Terminal de l’IDE connecté à Calypso), sauf mention contraire.*
- **Tableau 1.1 (Exécuter les tests manquants)**  
  - Ajouter une colonne **« Terminal »** avec la valeur *Intégré VS Code* pour chaque ligne, ou garder une seule note en en-tête de tableau : *Terminal : **intégré VS Code**.*
- **Sections 2 (chroma-mcp), 3 (LiteLLM)**  
  - Pour les blocs de commandes (`pip install`, `litellm --config`…) : préciser au-dessus du bloc *Dans le **terminal intégré à VS Code** (depuis la racine du projet / venv activé).*

---

### Détail doc 6 — CHECKLIST_E2E.md

- **Après la ligne « Référence : … »**  
  - Ajouter un encadré ou une note :  
    - **Terminal** : Les commandes de cette checklist sont à exécuter dans le **terminal intégré à VS Code** (ou Cursor en bootstrap), panneau Terminal de l’IDE. Ne pas utiliser un terminal externe (ex. SSH dans une autre fenêtre) sauf besoin explicite.
- **Tableaux des sections 1 à 7**  
  - Soit ajouter une colonne **Terminal** avec *Intégré VS Code* pour chaque cas, soit garder la note globale ci-dessus (recommandé pour éviter de surcharger les tableaux).

---

### Détail doc 7 — STATUS_IMPLEMENTATION.md

- **Section « Graphe LangGraph »**  
  - Après la ligne **CLI** : `python run_graph.py …`, ajouter :  
    - *Exécution recommandée : **terminal intégré à VS Code** (panneau Terminal), même machine ou session Remote-SSH.*
- **Section « Scripts »**  
  - En note sous le tableau :  
    - *Pour un usage interactif (run_graph, handle_interrupt, status) : **terminal intégré à VS Code**.* Les scripts appelés par cron (notify_pending_interrupts, sync_artifacts) s’exécutent dans l’environnement cron (pas dans l’IDE).

---

### Détail doc 8 — Modes_Bootstrap_et_Runtime_Cible.md (nouveau)

- **Emplacement** : `specs/plans/Modes_Bootstrap_et_Runtime_Cible.md`
- **Contenu proposé** :
  1. **Titre** : Modes Bootstrap et Runtime cible — Parcours et type de terminal
  2. **Objectif** : Document de référence pour qui fait quoi, où (IDE vs terminal), et quel type de terminal (intégré VS Code / Cursor vs externe).
  3. **Convention terminal** : Reprendre le tableau intégré VS Code / Cursor vs externe (comme en début de ce plan).
  4. **Critères de maturité et bascule Bootstrap → Runtime** (obligatoire) : Reprendre la section [Critères de maturité et moment de bascule Bootstrap → Runtime](#critères-de-maturité-et-moment-de-bascule-bootstrap--runtime) de ce plan (tableau M1–M5, définition du moment de bascule, possibilité de retour en bootstrap).
  4bis. **Plan de test pré-bascule** (obligatoire) : Reprendre la section [Plan de test pré-bascule](#plan-de-test-pré-bascule) (tests automatiques A1–A3, tests manuels Ma1–Ma4, synthèse minimum vs idéal). C’est la référence unique pour toute la doc.
  5. **Bootstrap (Cursor)**  
     - IDE : Cursor.  
     - Terminal : **terminal intégré à Cursor** pour toutes les commandes (install, run_graph, handle_interrupt, status, pytest, etc.).  
     - Pas d’obligation d’utiliser un terminal externe.
  6. **Runtime cible (VS Code + Continue + Roo Code)**  
     - IDE : VS Code (Remote-SSH sur Calypso), chat Continue / Roo Code.  
     - **Lancement du flux Agile** : `run_graph.py` depuis le **terminal intégré à VS Code**.  
     - **Idéation (sparring)** : dans le **chat Continue ou Roo Code** (pas dans le terminal).  
     - **Validation des interrupts (H1–H6)** : `handle_interrupt.py` depuis le **terminal intégré à VS Code** (approbation/rejet + feedback).  
     - **Consultation du statut** : `status.py` depuis le **terminal intégré à VS Code**.  
     - **Optionnel** : LangServe Playground dans le **navigateur** (`http://localhost:8000/agile/playground`).  
     - **Optionnel** : notification interrupt > 48h : script cron (environnement système) ; la réaction humaine reste via `handle_interrupt.py` dans le **terminal intégré à VS Code**.
  7. **Tableau récapitulatif**  
     - Colonnes : Action | Où | Type terminal | Remarque.  
     - Lignes : Lancer run_graph.py | VS Code | Intégré VS Code | — ; handle_interrupt (liste / approuver / rejeter) | VS Code | Intégré VS Code | — ; status.py | VS Code | Intégré VS Code | — ; Idéation / sparring | VS Code | Chat Continue/Roo Code | Pas terminal ; Playground | Navigateur | — | optionnel ; notify_pending (cron) | Système | Cron / terminal système | Lecture des interrupts : terminal intégré VS Code.
  8. **Références** : Plan_Configuration_VSCode_Ollama_Local.md, Implementation_Ecosysteme_Agile_Calypso.md, Specifications Ecosysteme Agile Agent IA.md, Plan_Harmonisation_Documents_Terminal.md (critères de maturité).

---

## Ordre d’exécution recommandé

1. Créer **Modes_Bootstrap_et_Runtime_Cible.md** (doc 8) pour avoir la référence de parcours et le tableau récap.
2. Mettre à jour **Specifications Ecosysteme Agile Agent IA.md** (doc 2) : nomenclature + sections III.8 et notification.
3. Mettre à jour **Implementation_Ecosysteme_Agile_Calypso.md** (doc 3) : conventions + toutes les occurrences Terminal.
4. Mettre à jour **Plan_Configuration_VSCode_Ollama_Local.md** (doc 4) : section 2.3 + 2.4 + 5.5.
5. Mettre à jour **Plan_Reste_Calypso_E2E_Optionnels.md** (doc 5) : en-tête + tableau 1.1 + blocs commandes chroma-mcp / LiteLLM.
6. Mettre à jour **CHECKLIST_E2E.md** (doc 6) : note terminal + optionnel colonne.
7. Mettre à jour **STATUS_IMPLEMENTATION.md** (doc 7) : CLI + note Scripts.
8. Dans **Specifications Ecosysteme Agile Agent IA.md**, ajouter la référence vers **Modes_Bootstrap_et_Runtime_Cible.md** si pas déjà fait à l’étape 2.

---

## Fichiers impactés (résumé)

| Fichier | Type de modification |
|---------|----------------------|
| specs/plans/Plan_Harmonisation_Documents_Terminal.md | Création (ce plan) + **Critères de maturité et bascule Bootstrap → Runtime** |
| specs/Specifications Ecosysteme Agile Agent IA.md | Nomenclature VUE Terminal, précisions III.8, référence Modes_Bootstrap |
| specs/plans/Implementation_Ecosysteme_Agile_Calypso.md | Convention terminal, Bootstrap vs Cible, [ PC > Cursor > Terminal intégré ], **référence critères maturité (bascule)** |
| specs/plans/Plan_Configuration_VSCode_Ollama_Local.md | 2.3 explicite, 2.4 nouvelle section, 5.5 |
| specs/plans/Plan_Reste_Calypso_E2E_Optionnels.md | Note terminal, colonne/note tableau 1.1, blocs commandes |
| docs/CHECKLIST_E2E.md | Note terminal en en-tête, optionnel colonne |
| docs/STATUS_IMPLEMENTATION.md | Ligne CLI, note Scripts |
| specs/plans/Modes_Bootstrap_et_Runtime_Cible.md | Création (parcours + **critères de maturité** + **plan de test pré-bascule** + tableau récap) |

---

*Fin du plan.*
