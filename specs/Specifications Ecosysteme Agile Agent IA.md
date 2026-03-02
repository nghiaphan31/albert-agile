##

* * *

📑 Manifeste de l'Écosystème Agile en Autarcie

*Contexte : Linux, RTX 3060 (12G VRAM), Google AI Studio (free-tier), Anthropic (Opus 4.6 / Sonnet 4.6). Priorité : coûts et qualité.*

| Section | Contenu |
|---------|---------|
| I | Matrice Modèles IA (local/cloud) par rôle — cohérence technique |
| II | Rôles, artefacts et régimes financiers |
| III | Outils, frameworks, modèles exacts à installer (dont LangGraph, Pydantic) |
| III.5–III.8 | LangChain/LangGraph ; Modèle de codage ; Human-in-the-Loop ; Mémoire/RAG (dont III.7-bis : temps réel, partage IDE via MCP) ; Procédures Opérationnelles Consolidées |
| IV | Comptes Cloud gratuits + checklist d'installation |
| V | Flux détaillés et livrables (Phase 0 + Usine Agile) |
| VI | Stratégies d'optimisation des coûts |
| VII | Exigences transversales (testabilité, traçabilité, modularité) |
| VIII | Rapports de simulation (références, corrections intégrées) |
| IX | Layout architectural (Mermaid) |
| Annexe A | Cartographie financière (synthèse par coût) |
| Annexe B | Historique des corrections par simulation (001–013) |

---

### I. Matrice Modèles IA par Rôle et par Flux (Cohérence Technique)

**Règle de cascade unique** : Pour chaque rôle, l'IA est sollicitée dans l'ordre suivant. On n'escalade au niveau supérieur que si le niveau inférieur échoue (qualité insuffisante) ou renvoie HTTP 429.

| Niveau | Technologie | Modèle exact | Usage typique | Coût |
|--------|-------------|--------------|---------------|------|
| **N0 – Local** | Ollama sur RTX 3060 (12G VRAM) | `qwen2.5-coder:7b` (code) ou `gemma3:12b-it-q4_K_M` (idéation) | Tâches courantes, ~80% des cas | 0 € |
| **N1 – Cloud gratuit** | Google AI Studio API | `gemini-2.5-flash` ou `gemini-2.5-flash-lite` | Fallback après N0 | 0 € |
| **N2 – Cloud payant** | Anthropic API | `claude-sonnet-4-6` (exécution) / `claude-opus-4-6` (architecture) | Dernier recours, décisions critiques | Pay-as-you-go |

**Mapping rôle → modèles par défaut** :

| Rôle | Modèle local (N0) | Modèle cloud gratuit (N1) | Modèle cloud payant (N2) |
|------|-------------------|---------------------------|---------------------------|
| R-0 Business Analyst | gemma3:12b-it-q4_K_M | gemini-2.5-flash | claude-opus-4-6 |
| R-2 System Architect | gemma3:12b-it-q4_K_M | gemini-2.5-flash | claude-opus-4-6 |
| R-3, R-4, R-5, R-6 | qwen2.5-coder:7b | gemini-2.5-flash | claude-sonnet-4-6 |

*R-1 Product Owner et R-7 Stakeholder : humains, pilotent via VS Code + Continue.dev.*

---

### II. Répertoire Détaillé des Rôles, Artefacts et Régimes Financiers

| ID | Rôle Agile & Mission | Entité | Technologie & Régime | Artefact (Livrable) |
| --- | --- | --- | --- | --- |
| R-0 | **Business Analyst** — Guide la phase d'idéation, challenge les hypothèses métier et aide à définir la proposition de valeur avant tout investissement technique. | Sparring Partner | Cascade : Ollama (gemma3:12b) → AI Studio (Gemini 2.5 Flash) → Opus 4.6 | Notes de Discovery, Gros Ticket initial mature |
| R-1 | **Product Owner** — Garant de la vision produit. Priorise la valeur métier, gère le backlog interactif via Continue.dev (RAG sur la codebase ; option : chroma-mcp pour RAG partagé avec agents) et s'assure de l'alignement. | Nghia (PM) | VS Code + Continue.dev + Roo Code. Régime : Local / Gratuit | Besoins - Product Backlog.md, Co-rédacteur de la DoD |
| R-2 | **System Architect** — Garant de la viabilité technique. Traduit les besoins métier en choix architecturaux, structures de données et contrats d'API. | L'Architecte | Cascade : Ollama (gemma3:12b) → AI Studio → Opus 4.6 | Architecture.md, Co-rédacteur de la DoD |
| R-3 | **Scrum Master** — Facilitateur et orchestrateur. Lève les obstacles, gère le découpage technique pour respecter la vélocité et anonymise les contextes. | Chef de Projet | Cascade : Ollama (qwen2.5-coder:7b) → AI Studio → Sonnet 4.6 | Sprint Backlog (tickets atomiques et ciblés) |
| R-4 | **Dev Team** — Force de production exécutive incarnée par Roo Code. Écrit le code source fonctionnel et garantit la non-régression via TDD. | Le Développeur | Cascade : Ollama (qwen2.5-coder:7b) → AI Studio → Sonnet 4.6 | Source Code, Unit Tests (TDD) |
| R-5 | **Release Manager** — Garant du versioning et de la stratégie de branching. Gère les conflits de fusion et isole les développements. | L'Archiviste | Git / MCP + Cascade : Ollama (qwen2.5-coder:7b) → AI Studio → Sonnet 4.6 | Feature Branches, Historique des Commits |
| R-6 | **QA & DevOps** — Garant de l'intégration continue. Exécute les tests, analyse les logs d'erreurs et déclenche la boucle de correction. | L'Inspecteur | Docker, Jest + Cascade : Ollama (qwen2.5-coder:7b) → AI Studio → Sonnet 4.6 | Test Reports & Logs (application stricte de la DoD) |
| R-7 | **Stakeholder** — Sponsor du projet. Évalue le ROI de l'incrément, supervise les tests finaux dans VS Code et valide l'alignement stratégique. | Nghia (Dir) | VS Code + Continue.dev + Roo Code. Régime : Local / Gratuit | Go/No-Go Decision, Valideur final de la DoD |

###

* * *

III. Outils, Frameworks et Modèles IA — Spécifications Techniques Détaillées

#### 3.1 Matériel et Moteurs Locaux

| Composant | Spécification | Rôle |
|-----------|---------------|------|
| GPU | NVIDIA RTX 3060, 12 Go VRAM | Exécution des modèles Ollama (Q4 quantization) |
| Moteur LLM | **Ollama** (https://ollama.com) | Runtime pour modèles locaux, API compatible OpenAI |

#### 3.2 Modèles Ollama à Installer (Téléchargement Unique)

| Modèle | Commande d'installation | VRAM | Usage principal |
|--------|-------------------------|------|-----------------|
| **qwen2.5-coder:7b** | `ollama pull qwen2.5-coder:7b` | ~8–10 Go | R-3, R-4, R-5, R-6 : code, tests, découpage, merge |
| **gemma3:12b-it-q4_K_M** | `ollama pull gemma3:12b-it-q4_K_M` | ~8,1 Go | R-0, R-2 : idéation, architecture, réflexion stratégique |

*Contexte : 128K tokens (Qwen), 128K (Gemma 3). Licence : Apache 2.0 / licence ouverte.*

#### 3.3 Interface et Orchestration

| Outil | Version / Référence | Usage |
|-------|--------------------|-------|
| **VS Code** | Dernière stable | IDE central |
| **Continue.dev** | Extension open-source | Autocomplétion, RAG codebase, pilotage des modèles (Ollama, API) |
| **Roo Code** | Extension / agent | Exécution autonome des tâches (sprints, CI) |
| **LangGraph + LangChain** | Dernière stable (LangGraph 1.x) | Orchestration du graphe d'agents, routage cascade, human-in-the-loop. Voir section III.5. |

#### 3.4 Chaîne de Qualité, RAG et CI/CD

| Outil | Usage |
|-------|-------|
| **Git** | Versioning, branches, historique |
| **MCP (Model Context Protocol)** | Contexte structuré de la codebase pour les agents ; chroma-mcp pour partage RAG agents + IDE (III.7-bis) |
| **Chroma** | Base vectorielle pour RAG agents (codebase, docs projet). Voir III.7. |
| **nomic-embed-text** (Ollama) | Modèle d'embeddings local pour Chroma. `ollama pull nomic-embed-text`. |
| **Docker** | Isolation, tests reproductibles |
| **Jest** (JS/TS) / **Pytest** (Python) | Tests unitaires et intégration |
| **ESLint** / **Ruff** | Linting |
| **GitHub Actions** | CI/CD (dépôts publics : gratuit) |

#### 3.5 Écosystème LangChain/LangGraph — Orchestration Multi-Agents et Human-in-the-Loop

**Justification** : Les rôles R-0 à R-6 sont des agents IA qui doivent collaborer selon un graphe de décision (cascade, routage, boucles). LangGraph (1.0 GA, octobre 2025) est le framework de référence pour orchestrer des agents multiples avec état partagé, cycles et human-in-the-loop. LangChain fournit les connecteurs LLM (Ollama, Anthropic, Google). Pydantic garantit des sorties structurées et validées. Cet écosystème permet d'automatiser le flux Agile tout en conservant des points de validation humaine aux moments critiques.

| Composant | Rôle | Justification |
|-----------|------|---------------|
| **LangGraph** | Orchestration du graphe d'agents. Chaque rôle (R-0 à R-6) = nœud. Arêtes = flux (E1→E2→…). Routage cascade N0→N1→N2 par branche conditionnelle. | Modèle en graphe (vs chaîne linéaire) : cycles (Self-Healing R-6→R-4), bifurcations, état partagé (TypedDict). `interrupt()` natif pour Human-in-the-Loop. Utilisé en prod par LinkedIn, Uber, Klarna. AgentExecutor LangChain déprécié en faveur de LangGraph. |
| **LangChain** | Connecteurs LLM (Ollama, Google AI Studio, Anthropic), gestion des retries/backoff, templates de prompts. | Dépendance de LangGraph. Abstraction unifiée : `ChatOllama`, `ChatAnthropic`, `ChatGoogleGenerativeAI`. Compatible Ollama via `langchain-ollama`. |
| **Pydantic** | Validation des sorties IA : schémas pour Gros Ticket, Sprint Backlog, Architecture.md, tickets. | Évite les outputs invalides (JSON malformé, champs manquants). Intégré à LangChain (`with_structured_output`). Typage strict = moins d'erreurs en production. |
| **LangSmith** | Traçage, débogage, monitoring des runs. Intégration native avec LangChain/LangGraph. | Free tier : 5000 traces/mois. Indispensable pour débugger des workflows multi-agents (quel agent a échoué, pourquoi, tokens consommés). Rétention 14 jours suffisante pour itérations. |
| **LangServe** | Exposition du graphe LangGraph en API REST (FastAPI). Endpoints `/invoke`, `/stream`, `/playground`. | Permet de déclencher les phases (E1–E6) depuis un script, un cron ou GitHub Actions. Déploiement local (pas de coût). Alternative : exécution directe en CLI Python. |

**Architecture d'intégration** : Un service Python héberge le graphe LangGraph. Les nœuds appellent Ollama (N0), Google API (N1) ou Anthropic (N2) selon la logique de cascade. Pydantic modélise l'état (Backlog, Architecture, SprintBacklog) et les sorties de chaque agent. LangSmith trace chaque exécution. L'humain (R-1, R-7) intervient via `interrupt()` aux points définis ci-dessous.

**Pydantic vs Pydantic AI** : Pydantic (bibliothèque de validation) est utilisée. Pydantic AI est un framework d'agents concurrent de LangChain ; pour éviter la fragmentation et profiter de l'écosystème LangGraph (Human-in-the-Loop mature, communauté large), on retient LangGraph + Pydantic (validation).

#### 3.5bis Modèle de codage (paradigme d'implémentation)

*Cette section synthétise le paradigme de codage des flux de travail. Elle sert de référence pour l'implémentation.*

| Concept | Implémentation |
|---------|----------------|
| **Rôles (R-0 à R-6)** | Nœuds du graphe — une fonction Python par rôle, qui reçoit l'état et retourne une mise à jour. |
| **Phases (E1→E2→…)** | Arêtes entre nœuds (transitions définies dans le graphe). |
| **État partagé** | `TypedDict` : Backlog, Architecture, SprintBacklog, DoD, messages, **project_root** (Path), **project_id** (str), **sprint_number** (int, défaut 1), **adr_counter** (int, défaut 0), **needs_architecture_review** (bool, défaut false). Initialisés par le nœud "load_context" (III.8-A) en entrée de chaque thread. Invocation : `start_phase "E1" | "E3" | "HOTFIX"` via config (III.8-A). |
| **Appels LLM** | Cascade N0→N1→N2 : essai Ollama (N0), puis Google AI Studio (N1), puis Anthropic (N2) en dernier recours. Logique de routage conditionnelle selon succès/échec/HTTP 429. |
| **Sorties structurées** | `with_structured_output` (LangChain) + schémas Pydantic sur chaque LLM. Garantit des sorties valides (Gros Ticket, tickets, Architecture, etc.). |
| **Self-Healing (R-6→R-4)** | Cycle dans le graphe : arête conditionnelle R-6→R-4 si tests en échec. Seuil strict : 3 itérations max, puis interrupt H5. |
| **Human-in-the-Loop** | `interrupt()` dans les nœuds aux points H1–H6. Le graphe suspend, le checkpointer sauvegarde. Reprise via `Command(resume=...)`. |
| **Tools (E4, E5)** | R-4 : `read_file`, `write_file`, `run_shell` (génération de code, exécution). R-5 : `run_shell` (git checkout, commit, merge). |
| **Flux de données par nœud** | (1) Lire l'état (checkpointer). (2) Interroger le RAG (Chroma) pour chunks pertinents. (3) Appeler l'LLM (cascade). (4) Écrire en BaseStore si nécessaire (E2, E6). (5) Retourner la mise à jour d'état. |
| **Persistance** | Checkpointer (SqliteSaver/PostgresSaver) par step. BaseStore pour mémoire long terme. Chroma pour RAG. |
| **Exposition** | LangServe (FastAPI) : `/invoke`, `/stream`, `/playground`. Alternative : invocation directe en CLI Python. |

**Correspondance rôle ↔ nœud** : Chaque ligne du tableau des rôles (section II) correspond à un nœud du graphe. R-1 et R-7 sont humains : ils interviennent via `interrupt()` (validation) et n'ont pas de nœud dédié ; le graphe s'arrête en attente de leur input.

#### 3.6 Human-in-the-Loop — Points d'Interruption Obligatoires

**Principe** : Automatiser au maximum le flux, mais bloquer l'exécution pour validation humaine aux décisions critiques. LangGraph `interrupt()` suspend le graphe, sauvegarde l'état (checkpointer), et attend un `Command(resume=...)` de l'opérateur.

| Point d'interrupt | Étape | Déclencheur | Action humaine | Justification |
|-------------------|-------|-------------|----------------|---------------|
| **H1** | Fin Phase 0 | R-0 a produit le Gros Ticket | R-1 (Product Owner) valide ou corrige le Gros Ticket avant injection dans le Backlog. | Décision stratégique : engagement sur la vision. Pas de délégation à l'IA. |
| **H2** | Fin E2 | R-2 a produit Architecture.md + draft DoD | R-7/R-1 valident l'architecture **et** co-construisent la DoD. Le payload H2 contient Architecture.md et un draft DoD généré par R-2. R-1 amende la DoD (critères d'acceptation), R-7 valide l'ensemble. La DoD finalisée est écrite dans l'état et dans BaseStore. Voir III.8-B et III.8-O. | Choix techniques engageants. DoD comme contrat d'acceptation partagé. |
| **H3** | Fin E3 | R-3 a produit le Sprint Backlog | R-1 valide le découpage et la priorisation des tickets. | Ajustement de la vélocité, risques de sur/sous-découpage. |
| **H4** | Fin E5 | CI local (R-6) ET CI 1 GitHub Actions verts | **Séquence** : (1) R-5 push unique en fin de E4 → PR feature/{project_id}-sprint-{NN}→develop ouverte. (2) CI 1 (GitHub Actions, feature→develop) et CI local (R-6) tournent en parallèle. R-6 poll CI 1 via `gh run watch` (timeout GITHUB_ACTIONS_TIMEOUT=600s). (3) H4 déclenché si les deux CI sont verts. R-7 Sprint Review. (4) E6 : R-5 merge feature→develop. (5) Post-E6 : R-5 ouvre PR develop→main → CI 2 (GitHub Actions, develop→main). Merge develop→main après CI 2 vert. Voir III.8-B et III.8-F. | Double validation pré-H4. Merge main séparé (post-E6). |
| **H5** | Escalade N2 | L'IA sollicite Claude Opus/Sonnet (coût) | R-1 ou R-7 approuve l'escalade vers l'API payante. | Contrôle des coûts. Évite les appels non intentionnels. |
| **H6** | Conflit Git | R-5 échoue à résoudre un conflit après 2 tentatives | R-1 résout manuellement (git mergetool), commit, puis reprend le graphe. | Fallback pour conflits complexes. Voir III.8. |

**Implémentation** : Utiliser un checkpointer (ex. `SqliteSaver` ou `PostgresSaver`) pour persister l'état. Chaque `interrupt()` retourne un payload JSON. Procédure : script `scripts/handle_interrupt.py` ou endpoint LangServe (voir III.8).

**Branches rejected** : Si `Command(resume={"status":"rejected","feedback":"..."})` : H1 rejected → relance nœud R-0 avec le feedback injecté dans l'état (`state.h1_feedback`). H2 rejected → relance R-2 avec feedback. H3 rejected → relance R-3 avec feedback. H4 rejected → commits correctifs sur même feature branch (pas nouvelle branche), nouveau cycle E5 obligatoire (CI local + GitHub Actions) avant H4 suivant ; limite 3 cycles H4-rejected → H5 avec payload `reason="max_h4_rejections"`. Voir III.8-B pour le catalogue complet des branches rejected et des reasons H5.

**Automatisation sans interrupt** : E4 (exécution code), E5 (tests, Self-Healing) s'exécutent sans blocage. Le Self-Healing (R-6→R-4) est une boucle automatisée avec seuil strict : 3 itérations max (`SELF_HEALING_MAX_ITERATIONS=3`). Au-delà → interrupt H5 pour décision humaine.

#### 3.7 Mémoire, Contextes, Persistance et RAG — Architecture Multi-Agents

**Constat** : Un écosystème multi-agents nécessite (1) une mémoire court terme par session (état du graphe), (2) une mémoire long terme partagée (décisions passées, learnings), (3) un accès sémantique à la codebase et aux documents projet. Sans RAG ni base vectorielle, les agents n'ont que le contexte injecté à chaque requête ; ils ne peuvent ni récupérer du code pertinent, ni s'appuyer sur des sprints passés, ni maintenir une cohérence sur plusieurs sessions éloignées.

**Architecture à trois couches** (écosystème LangChain/LangGraph) :

| Couche | Rôle | Technologie | Justification |
|--------|------|-------------|---------------|
| **Mémoire court terme (état par thread)** | Sauvegarder l'état du graphe à chaque étape. Reprendre après interrupt, crash, ou session suivante. Human-in-the-loop requiert une persistance fiable. | **Checkpointer** : `SqliteSaver` (local simple) ou `PostgresSaver` (production, concurrence) | Cycle read-execute-write : à chaque step, l'état (messages, variables, flags) est sérialisé. `thread_id` identifie une exécution (sprint, projet). Permet le "time-travel" (retour à un état antérieur) et la reprise après `interrupt()`. |
| **Mémoire long terme (cross-thread, cross-session)** | Stocker décisions, préférences, résumés de sprints, patterns de résolution. Les agents récupèrent des informations pertinentes par similarité sémantique. | **LangGraph BaseStore** avec recherche sémantique : `PostgresStore` (pgvector) ou store custom basé sur **Chroma** | Mémoire partagée entre tous les agents et toutes les sessions. Permet "rappel" : "comment avons-nous résolu un bug similaire ?", "quelles étaient les décisions d'architecture ?". LangGraph propose `PostgresStore` avec `search(query=...)` pour recherche sémantique. |
| **RAG — Codebase et documents projet** | Fournir aux agents le contexte pertinent : code existant, Architecture.md, Backlog, DoD, ADRs. Chaque agent (R-2, R-3, R-4) doit pouvoir récupérer des extraits par requête naturelle. | **Base vectorielle** : **Chroma** + **nomic-embed-text** (Ollama) | Continue.dev a son propre RAG (LanceDB, voyage-code-3) pour l'humain dans VS Code ; les agents LangGraph tournent dans un processus Python distinct et n'y ont pas accès. Ils nécessitent un RAG dédié. Chroma : in-process, sans service externe, ~3,5 Go pour 1M vecteurs (768 dim). nomic-embed-text : 100 % local via Ollama, 0 €, performant. |

**Contenu à indexer dans le RAG (vecteurs)** :

| Source | Usage par les agents |
|--------|----------------------|
| Codebase (`src/`, fichiers principaux) | R-4 (Dev) : récupérer code existant, patterns, types. R-2 (Architecte) : comprendre la structure actuelle. |
| Architecture.md, ADRs | R-2, R-3, R-4 : respect des décisions, cohérence architecturale. |
| Besoins - Product Backlog.md, DoD | R-1, R-3 : priorisation, critères d'acceptation. |
| Tickets résolus, résumés de sprints | R-3, R-4 : patterns de découpage, résolutions passées. |

**Flux de données** : À chaque étape du graphe, l'agent peut (1) lire l'état court terme (checkpointer), (2) interroger le RAG pour récupérer les K chunks les plus pertinents (ex. top 5), (3) écrire en mémoire long terme (BaseStore) les éléments à retenir pour plus tard. Les embeddings sont produits localement par `nomic-embed-text` (Ollama).

**Recommandations techniques** :

| Choix | Recommandation | Justification |
|-------|----------------|---------------|
| **Checkpointer** | `SqliteSaver` pour démarrage local ; `PostgresSaver` dès mise en production ou multi-utilisateurs | Sqlite : un fichier, zéro config. Postgres : robustesse, concurrence, compatible avec pgvector pour BaseStore. |
| **Base vectorielle** | **Chroma** | In-process, pas de service à lancer. Suffisant pour codebase + docs d'un projet (ordre de grandeur : 10K–100K chunks). Si scale > 1M chunks : migrer vers Qdrant ou Postgres+pgvector. |
| **Embeddings** | **nomic-embed-text** via Ollama (`ollama pull nomic-embed-text`) | Local, 0 €, 768 dimensions. Performances comparables à text-embedding-ada-002. Intégration LangChain : `OllamaEmbeddings(model="nomic-embed-text")`. |
| **Indexation** | Déclencher après chaque commit significatif ou en fin de sprint | Pipeline : chunking (par fichier ou AST pour le code), embeddings, insertion Chroma. Métadonnées : `source`, `type` (code|doc|ticket), `project`, `sprint`. Voir III.7-bis pour options temps réel et incrémentiel. |
| **RAG partagé IDE** | Option : Chroma exposé via MCP pour agents ET IDE | chroma-mcp (chroma-core/chroma-mcp) ou MCP custom. Continue.dev, Cursor, Cline peuvent se connecter au même Chroma que les agents. Un seul index = alignement humains/agents. Voir III.7-bis. |

**Persistance à travers sessions éloignées** : Le checkpointer conserve l'état par `thread_id`. Une "session" = un `thread_id` (ex. `sprint-2026-03-01` ou `project-X-phase-0`). Pour reprendre des semaines plus tard : réutiliser le même `thread_id` ; LangGraph charge le dernier checkpoint. La mémoire long terme (BaseStore) et le RAG (Chroma) sont persistés sur disque ; ils survivent aux redémarrages et aux sessions espacées.

#### 3.7-bis Chroma RAG — Options temps réel et partage IDE (MCP)

**Justification** : Chroma indexe code + docs + artefacts (Backlog, Architecture, DoD, ADRs, tickets). Pour atteindre une fraîcheur comparable aux IDE et partager le même RAG entre agents et humains, les options suivantes sont spécifiées.

**Options d'indexation (temps réel)** :

| Option | Description | Variable | Défaut |
|--------|-------------|----------|--------|
| **File watcher** | Déclenche index_rag à la sauvegarde de fichier (hors E4/E5) | `AGILE_RAG_FILE_WATCHER=true` | `false` |
| **Indexation incrémentale** | Ré-indexer uniquement les fichiers modifiés (hash ou mtime) | `AGILE_RAG_INCREMENTAL=true` | `true` si file watcher actif |
| **AGILE_DEFER_INDEX** | Conserver : évite conflit GPU pendant E4/E5 | — | Voir III.8-C |

**Règle GPU** : Si `AGILE_RAG_FILE_WATCHER=true`, le watcher ne lance **pas** d'indexation pendant E4/E5 (qwen2.5-coder sur GPU). Détection : processus LangGraph actif ou variable `AGILE_E4_E5_ACTIVE`. En mode différé, le watcher écrit dans `pending_index.log` comme le hook Git.

**Partage RAG avec l'IDE (MCP)** :

| Option | Description | Effort |
|--------|-------------|--------|
| **chroma-mcp** (recommandé en premier) | Serveur MCP existant (chroma-core/chroma-mcp). Configurer pour pointer vers la même instance Chroma que index_rag. Les IDE (Continue.dev, Cursor, Cline) se connectent via MCP. L'agent appelle `chroma_query_documents` pour le contexte code/docs. | Configuration + alignement schéma collections |
| **MCP custom** | Serveur MCP léger exposant `search_codebase(query, project_id, top_k)` si chroma-mcp ne convient pas (schéma, métadonnées projet). | Développement |

**Flux partagé** : index_rag.py alimente Chroma. Les nœuds LangGraph interrogent Chroma directement. chroma-mcp (ou MCP custom) expose la même Chroma aux clients MCP. Continue.dev/Cursor configurés avec chroma-mcp → même index pour agents et humains.

**Flux d'écriture BaseStore** (obligatoire pour mémoire long terme) : À la fin de E2, le nœud R-2 écrit dans le BaseStore (namespace `project/{id}/architecture`) un résumé "architecture_approved" avec date et version. À la fin de E6, un nœud post-review écrit (namespace `project/{id}/sprints`) un "sprint_summary" (résumé incrément, tickets livrés, décisions). Format JSON. Les agents R-3 et R-4 interrogent le BaseStore avant découpage ou implémentation pour récupérer les résumés pertinents.

#### 3.8 Procédures Opérationnelles Consolidées

*Cette section intègre l'ensemble des procédures opérationnelles finales issues des simulations 001–013. Elle remplace l'ancienne suite de sections III.8–III.19. L'historique détaillé par simulation est conservé en Annexe B.*

---

##### A. Nœud load_context — Initialisation de chaque thread

Exécuté en tout premier à chaque démarrage de thread (avant E1 pour un nouveau projet, avant E3/E4/HOTFIX pour un sprint ou un hotfix). Charge depuis le BaseStore :

1. `adr_counter` depuis `project/{id}/adr_counter`. Défaut : 0.
2. `sprint_number` depuis `project/{id}/sprint_counter`. Défaut : 1.
3. `dod` depuis `project/{id}/dod/{sprint_number}`. Fallback : `dod/{sprint_number-1}`. Si sprint_number=1 et aucune DoD : `None` (E2 la créera).
4. Injecte les valeurs dans l'état initial du thread.

**Résilience BaseStore** : Variable `AGILE_BASESTORE_STRICT` (défaut : `false`). Si `false` et BaseStore inaccessible : valeurs par défaut + log WARNING. Si `true` : exception explicite avec message d'aide.

**Routing start_phase** : load_context route le graphe selon le paramètre `start_phase` (`"E1"` | `"E3"` | `"HOTFIX"`). Valeur par défaut : `"E1"`. Commandes types :
- Nouveau projet : `python run_graph.py --project-id <id> --start-phase E1 --thread-id <id>-phase-0`
- Nouveau sprint : `python run_graph.py --project-id <id> --start-phase E3 --thread-id <id>-sprint-02`
- Hotfix : `python run_graph.py --project-id <id> --start-phase HOTFIX --thread-id <id>-hotfix-<date> --hotfix-description "..."`

Pour `start_phase HOTFIX` : load_context crée un Sprint Backlog synthétique `SprintBacklog(tickets=[Ticket(id="HF-001", description=hotfix_description)], architectural_change=False)`.

---

##### B. Procédure Human-in-the-Loop (interrupts H1–H6)

**Exécution** : Endpoint LangServe `/playground` ou script `scripts/handle_interrupt.py [--thread-id <id>]`.
- Si `--thread-id` omis : liste les threads en attente, triés par `project_id` puis par type H (H1→H6). Demande de choisir.
- Si `--thread-id` fourni mais thread sans interrupt : message d'erreur explicite, exit code 1.
- Exit codes : 0=succès, 1=erreur (thread invalide), 2=usage (arguments invalides).
- Séquence : (1) lit l'état via l'API LangServe, (2) affiche le payload `__interrupt__`, (3) attend l'entrée (`approved` | `rejected` | `feedback`), (4) envoie `graph.invoke(Command(resume=...), config)`.
- En absence de l'humain : option `resume={"status":"rejected","resume_after":"<date>"}`. Notification si interrupt non traité > 48h.

**Branches rejected** :
- **H1 rejected** → injecte feedback dans `state.h1_feedback`, reboucle vers R-0 (nouveau Gros Ticket). Limite : 3 cycles → H5 `reason="max_rejections_H1"`.
- **H2 rejected** → injecte dans `state.h2_feedback`, reboucle vers R-2 (Architecture + DoD revisitées). Limite : 3 cycles → H5 `reason="max_rejections_H2"`.
- **H3 rejected** → injecte dans `state.h3_feedback`, reboucle vers R-3 (Sprint Backlog refait). Limite : 3 cycles → H5 `reason="max_rejections_H3"`.
- **H4 rejected** → commits correctifs sur la même feature branch, nouveau cycle E5 obligatoire. Limite : 3 cycles → H5 `reason="max_h4_rejections"`.
- **H6** : Si R-5 échoue à résoudre un conflit Git après 2 tentatives → interrupt. L'humain résout (`git mergetool`), commit, puis `Command(resume="resolved")`.

**Catalogue complet des reasons H5** :

| reason | Déclencheur |
|--------|-------------|
| `cost_escalation` | Escalade vers N2 (Opus/Sonnet) pour coût |
| `max_rejections_H1` | 3 cycles H1-rejected |
| `max_rejections_H2` | 3 cycles H2-rejected |
| `max_rejections_H3` | 3 cycles H3-rejected |
| `max_h4_rejections` | 3 cycles H4-rejected |
| `github_actions_timeout` | Timeout polling CI 1 ou CI 2 (GITHUB_ACTIONS_TIMEOUT) |
| `ci2_github_actions_failure` | CI 2 rouge après merge_to_main |
| `pr_review_required` | Branch protection stricte sur main (reviewer requis) |

**H4 sequence complète** : (1) R-5 push unique feature branch fin E4 + `gh pr create --base develop`. (2) CI local (R-6) et CI 1 (GitHub Actions, feature→develop) tournent en parallèle. R-6 poll CI 1 via `gh pr checks {pr_number} --required --watch --interval 30` (timeout `GITHUB_ACTIONS_TIMEOUT=600s`). (3) Les deux CI verts → H4. (4) H4 resume approuvé → E6 (Retrofit + sprint_complete). **H4 est toujours l'interrupt de sortie de E5**, indépendamment du nombre de H5 précédents.

**Ordre opérations post-interrupt** (H1, H2, H4) : (1) mise à jour état avec feedback, (2) écriture BaseStore si applicable, (3) appel index_rag, (4) transition nœud suivant.

**T1 — Ordre strict pour H1** : R-1 doit avoir créé `Besoins - Product Backlog.md` et committé **avant** d'envoyer `Command(resume)` sur H1. Sinon post_h1 indexe un fichier vide.

---

##### C. Pipeline d'indexation RAG

**Déclencheurs** :
- **Nœud post_h1** (après H1 resume) : `index_rag.py --project-root {state.project_root} --project-id {state.project_id} --sources backlog`
- **Nœud post-H2** : `--sources architecture,dod`
- **Nœud post-H4** : `--sources all`
- **Hook Git post-commit** : lit `AGILE_PROJECT_ID` (depuis `.agile-project-id`) et `AGILE_ORCHESTRATION_ROOT` (depuis `.agile-env`). Appelle `python $AGILE_ORCHESTRATION_ROOT/scripts/index_rag.py --project-root $(pwd) --project-id $AGILE_PROJECT_ID`. Ne doit **pas** utiliser `$(basename $(pwd))` comme project_id.
- **File watcher** (optionnel) : Si `AGILE_RAG_FILE_WATCHER=true` dans `.agile-env`, un daemon/watchdog surveille les fichiers du projet et déclenche `index_rag.py --sources code` (ou `all`) sur modification. **Désactivé automatiquement pendant E4/E5** (conflit GPU avec qwen2.5-coder). Si `AGILE_DEFER_INDEX=true` et E4/E5 actif : écrit dans `pending_index.log` comme le hook.

**Mode différé (AGILE_DEFER_INDEX=true)** : Si actif dans `.agile-env`, le hook (et le file watcher si actif) écrit dans `logs/pending_index.log` (`<timestamp> <commit_hash> <project_id>`) au lieu de lancer index_rag. Le nœud sprint_complete traite `pending_index.log` en fin de sprint (hors E4/E5, évite les conflits GPU). Valeur par défaut : `false`.

**Indexation incrémentale** : Si `AGILE_RAG_INCREMENTAL=true`, index_rag ne ré-indexe que les fichiers modifiés (comparaison mtime ou hash). Réduit charge GPU et latence. Compatible avec file watcher. Valeur par défaut : `true` si file watcher actif, sinon `false`.

**Script index_rag.py** (dans le projet orchestration) :
- Signature : `--project-root <path> --project-id <id> [--sources backlog|architecture|code|all] [--strict] [--incremental]`
- Option `--incremental` : indexation incrémentale (fichiers modifiés uniquement)
- Résilience : try/except par fichier, skip en erreur, rapport dans `logs/index_rag_<timestamp>.log`
- Si `--strict` et 0 fichier indexé : exit 1. Si > 10 % en erreur : log warning dans `logs/index_errors.log`

**Bootstrap** : `scripts/setup_project_hooks.sh --orchestration-root <path> --project-root <path> --project-id <id>` :
- Crée `.agile-project-id` (project_id sur une ligne)
- Crée `.agile-env` (AGILE_ORCHESTRATION_ROOT, AGILE_PROJECT_ID, AGILE_DEFER_INDEX, AGILE_PROJECTS_JSON, AGILE_RAG_FILE_WATCHER, AGILE_RAG_INCREMENTAL)
- Crée la branche `develop` depuis `main` si absente : `git checkout -b develop main && git push -u origin develop`

---

##### D. Stratégie de branches Git

Modèle **feature-par-sprint** :

| Branche | Rôle | Gestionnaire |
|---------|------|-------------|
| `main` | Production. Merge uniquement après CI 2 vert. | R-5 |
| `develop` | Intégration continue. Base de toutes les features. | R-5 |
| `feature/{project_id}-sprint-{NN}` | Travail du sprint N. Créée depuis `develop`. | R-5 |
| `hotfix/{project_id}-{date}-{description}` | Correctif urgent depuis `main`. | R-5 |

**Flux sprint** : feature→develop (merge R-5 après H4 approuvé) → PR develop→main (CI 2) → merge develop→main (gh pr merge, après CI 2 vert).

**Flux hotfix** : hotfix créée depuis `main`. CI 1 sur PR hotfix→main. H4 validation. R-5 merge hotfix→main (`gh pr merge`). Puis R-5 merge hotfix→develop directement (`git checkout develop && git merge --no-ff hotfix/... && git push`) — sans PR ni CI supplémentaire, le code ayant déjà été validé.

**H6 conflits** : s'applique aux merge feature→develop et develop→main. Après 2 tentatives auto : interrupt H6.

**Timing push R-5** : push unique en fin de E4, après le dernier commit de ticket. Un seul trigger CI 1.

---

##### E. Nœud sprint_complete — Deux phases

**Phase 1 — sprint_summary** :
1. Écriture `sprint_summary` dans BaseStore (`project/{id}/sprints/sprint-{NN}`)
2. Déclenchement index_rag (ou traitement `pending_index.log` si `AGILE_DEFER_INDEX=true`)
3. Incrément `state.sprint_number` → N+1 et écriture BaseStore **uniquement en mode dégradé** (github_repo absent)

**Phase 2 — merge_to_main** (si `github_repo` présent) :
1. R-5 merge `feature/{id}-sprint-{NN} → develop`
2. `gh pr create --base main --head develop --title "Release sprint {NN}"`
3. `gh pr checks {pr_number} --required --watch --interval 30` (CI 2)
4. CI 2 vert → `gh pr merge --merge --delete-branch=false`. Incrément `state.sprint_number` → N+1, écriture BaseStore
5. CI 2 rouge → H5 `reason="ci2_github_actions_failure"` **sans modifier sprint_number**

**Branch protection** :
- Sans protection (solo) : `gh pr merge` automatique après CI 2 vert
- Avec protection CI-only sur `develop` : `gh pr merge` passe si CI vert
- Avec protection stricte sur `main` (reviewer requis) : H5 `reason="pr_review_required"`, opérateur approuve manuellement la PR, puis `Command(resume="merged")`

**auto_next_sprint** : si `projects[project_id].auto_next_sprint = true`, la boucle vers E3 (thread_id `{project_id}-sprint-{NN+1}`) se déclenche **après la phase 2** (mode complet) ou **après la phase 1** (mode dégradé).

---

##### F. GitHub Actions CI 1 et CI 2

| CI | PR cible | Déclencheur | Condition pour la suite |
|----|----------|-------------|------------------------|
| **CI 1** | `feature/{id}-sprint-{NN} → develop` | R-5 push fin E4 + `gh pr create` | Nécessaire pour déclencher H4 |
| **CI 2** | `develop → main` | sprint_complete phase 2 + `gh pr create` | Nécessaire pour merge develop→main |

**Polling** : R-6 utilise `gh pr checks {pr_number} --required --watch --interval 30`. Timeout `GITHUB_ACTIONS_TIMEOUT=600s` (défaut). Workflow GitHub Actions déclenché sur `pull_request` (pas seulement `push`).

**Mode dégradé** (github_repo absent dans projects.json) : CI 1/CI 2 skippés. H4 déclenché sur CI local seul. Log WARNING. Merge develop→main : action manuelle.

---

##### G. Gestion multi-projets et projects.json

**Convention thread_id** : `{project_id}-phase-0`, `{project_id}-sprint-{NN}` (padding 2 chiffres), `{project_id}-hotfix-{date}`.

**Format projects.json** (chemin : `$AGILE_ORCHESTRATION_ROOT/config/projects.json`, variable `AGILE_PROJECTS_JSON`) :
```json
{
  "<project_id>": {
    "path": "/chemin/absolu/projet",
    "auto_next_sprint": false,
    "archived": false,
    "github_repo": "owner/repo"
  }
}
```
- `github_repo` (optionnel) : requis pour CI 1/CI 2. Si absent → mode dégradé.
- `archived: true` : projet exclu des traitements actifs, gardé en référence.

**handle_interrupt.py** affiche les interrupts groupés par `project_id`, triés par H1→H6.

---

##### H. Articulation E4 : LangGraph pilote

E4 est piloté par les nœuds R-4 et R-5 du graphe. R-4 dispose de tools : `read_file`, `write_file`, `run_shell`. R-5 gère Git (`run_shell`). Les tools utilisent `state.project_root` comme répertoire de travail. Roo Code et Continue.dev restent l'interface humaine (hors flux automatisé). R-4 traite les tickets séquentiellement.

---

##### I. Self-Healing (R-6→R-4)

Seuil : `SELF_HEALING_MAX_ITERATIONS=3`. Au-delà → interrupt H5 `reason="cost_escalation"` (approbation N2) ou arrêt avec rapport d'échec.

**Backoff HTTP 429** : 3 tentatives max, backoff exponentiel (2^attempt secondes). Variable `API_429_MAX_RETRIES=3`. Si 429 persiste → H5 `reason="cost_escalation"` ou "pause et retry demain".

---

##### J. Stratégie GPU (Ollama)

Un seul modèle chargé à la fois. Priorité : `qwen2.5-coder` (E4, E5) > `gemma3` (Phase 0, E2). Configurer `OLLAMA_KEEP_ALIVE`. Utiliser `AGILE_DEFER_INDEX=true` pour éviter les indexations nomic-embed-text pendant E4/E5.

---

##### K. Politique de traçage LangSmith

Si risque de dépassement 5 000 traces/mois (free tier) : `LANGCHAIN_TRACING_SAMPLING_RATE=0.2` (20 %) ou `LANGCHAIN_TRACING_ERRORS_ONLY=true`. Priorité : conserver les runs en erreur.

---

##### L. Politique de rétention et archivage

**Checkpoints** : purge `scripts/purge_checkpoints.py [--dry-run] [--max-age-days 90]`. "90 jours" = date du dernier step. Exclure les threads avec `__interrupt__` non résolu. Log des threads supprimés.

**Chroma** : une collection par projet. `scripts/export_chroma.py --project-id <id> --output <path>.json`. `scripts/import_chroma.py --project-id <id> --input <path>.json`. Exporter avant suppression.

**Logs** : rotation 7 jours, max 100 Mo. LangSmith : rétention 14 jours (free tier), export optionnel via `export_langsmith_traces.py`.

---

##### M. Procédure de clôture de projet

Checklist (manuelle par R-1/R-7 ou via nœud optionnel `project_close`) :
1. R-5 merge final `develop → main` (`git merge --no-ff`) si non déjà fait
2. `scripts/export_chroma.py --project-id <id> --output archives/<id>-<date>.json`
3. `projects.json` : `"archived": true`
4. `scripts/purge_checkpoints.py --dry-run` (vérification)
5. BaseStore : `project/{id}/status = "archived"`
6. Documenter dans README ou Architecture.md

---

##### N. Génération de documentation (build_docs)

Étape dans E5 (avant les tests) : R-6 exécute `sphinx-build` (Python) ou `npm run docs` (JS/TS). Si pas de `conf.py` / `jsdoc.json` : skip avec log. Variable `BUILD_DOCS_REQUIRED=false` (défaut : skip silencieux ; `true` : échec si absent).

---

##### O. Synchronisation Architecture.md (sync_artifacts)

Optionnel. Nœud `sync_artifacts` ou cron (`SYNC_ARTIFACTS_CRON="0 0 * * 0"` = dimanche minuit) : compare la structure du code à Architecture.md et génère un rapport de dérive. Si non configuré : désactivé.

**Numérotation ADRs** : `state.adr_counter` (TypedDict, chargé depuis BaseStore `project/{id}/adr_counter`). Incrémenté par R-2 à chaque ADR produit. Fichier : `docs/ADR-{NNN:03d}-{date}-{slug}.md`.

**DoD versionnée** : namespace BaseStore `project/{id}/dod/{sprint_number}`. Chaque sprint conserve sa DoD. Chargée par load_context pour le sprint en cours.

**Re-déclenchement E2** : Si `state.sprint_backlog.architectural_change = True` (champ Pydantic SprintBacklog, défaut `False`, positionné par R-3), sprint_complete met `needs_architecture_review = True` et boucle vers E2 au lieu de E3.


---

IV. Comptes de Services Cloud à Mettre en Place (Priorité Gratuit)

| Service | Compte | Free Tier (mars 2026) | Usage dans l'écosystème |
|---------|--------|------------------------|-------------------------|
| **Google AI Studio** | Compte Google | Gemini 2.5 Flash : 10 RPM, 250–500 RPD, 250K TPM | Fallback N1 de la cascade |
| **Anthropic** | Compte API | Pay-as-you-go, pas d'abonnement minimum | Opus 4.6 / Sonnet 4.6 en dernier recours |
| **GitHub** | Compte personnel | 2000 min/mois Actions (privé), illimité (public) | CI/CD, dépôts, MCP |
| **LangSmith** | Compte free | 5000 traces/mois, 14 jours rétention | Traçage et débogage des workflows multi-agents (obligatoire pour production) |
| **Vercel** | Compte free | Déploiement frontend gratuit | À configurer uniquement si le projet livré est une application web frontend. Omettre pour librairies/CLI. |
| **Railway** | Compte free | Crédits mensuels limités | À configurer uniquement si le projet livré est une API backend à déployer. Omettre sinon. |

*Recommandation : privilégier les dépôts publics pour GitHub Actions illimité.*

#### 4.1 Checklist d'Installation (Ordre Recommandé)

1. **Ollama** : `curl -fsSL https://ollama.com/install.sh | sh` puis `ollama pull qwen2.5-coder:7b`, `ollama pull gemma3:12b-it-q4_K_M`, `ollama pull nomic-embed-text`
2. **VS Code** : Installation standard
3. **Continue.dev** : Extension depuis le marketplace. Configurer Ollama (`http://localhost:11434`) et les modèles `qwen2.5-coder:7b` / `gemma3:12b-it-q4_K_M`. Option RAG partagé : configurer chroma-mcp (étape 6) dans `.continue/mcpServers/` pour utiliser le même Chroma que les agents.
4. **Roo Code** : Extension depuis le marketplace. Même configuration Ollama
5. **LangGraph + LangChain + Pydantic + Chroma** : `pip install langgraph langchain langchain-ollama langchain-anthropic langchain-google-genai langchain-chroma pydantic chromadb`. Créer le projet Python du graphe (III.5), configurer le checkpointer et le RAG (III.7, III.7-bis). État TypedDict : inclure `dod`, `sprint_number` (int, défaut 1), `adr_counter` (int, défaut 0), `needs_architecture_review` (bool). Nœud "load_context" en entrée de thread. Voir III.8 (procédures consolidées). Stratégie branches Git : feature/{project_id}-sprint-{NN} depuis develop (III.8-D). Créer les scripts : `handle_interrupt.py`, `index_rag.py`, `setup_project_hooks.sh`, `purge_checkpoints.py`, `export_chroma.py`, `import_chroma.py` (voir III.8-C, III.8-J, III.8-L). Options RAG : file watcher, indexation incrémentale (III.7-bis). Créer `projects.json` (format III.8-G). Variable `AGILE_PROJECTS_JSON`. `API_429_MAX_RETRIES=3`. GitHub Actions sur `pull_request` (III.8-F). Checklist de clôture (III.8-M). Voir III.8.
6. **chroma-mcp** (optionnel, pour RAG partagé IDE) : `uvx chroma-mcp` ou `pip install chroma-mcp`. Configurer pour pointer vers la même Chroma que index_rag (client persistent ou HTTP). Ajouter à `.continue/mcpServers/` (Continue) ou `~/.cursor/mcp.json` (Cursor) pour que l'IDE utilise le même RAG que les agents. Voir III.7-bis.
7. **LangSmith** : Compte sur https://smith.langchain.com. Clé API à définir dans `LANGCHAIN_TRACING_V2=true` et `LANGCHAIN_API_KEY=...` pour traçage.
8. **Google AI Studio** : Clé API sur https://aistudio.google.com. Provider de fallback N1.
9. **Anthropic** : Clé API sur https://console.anthropic.com pour Opus/Sonnet en dernier recours.
10. **GitHub** : Compte + dépôt public (Actions illimité).
11. **GitHub CLI** : `gh` — `sudo apt install gh` puis `gh auth login` (une seule fois). Requis pour CI 1/CI 2 (`gh pr create`, `gh pr checks`). Requis pour CI 1/CI 2 (III.8-F).
12. **Docker** : Pour isolation des tests.
13. **Vercel / Railway** : Uniquement si le projet livré requiert un déploiement web (frontend ou API).

---

V. Les Flux Complets du Cycle de Vie (La Bascule Agile)

🛡️ **RÈGLE D'OR DE SÉCURITÉ ET DE CONFIDENTIALITÉ**

Avant toute escalade d'une tâche vers le Cloud (Gemini, Google AI Studio ou Claude API), le système ou l'opérateur doit garantir l'anonymisation absolue des données. **Il est formellement et absolument interdit d'envoyer des données privées, des informations confidentielles, des secrets industriels ou des clés d'API à une IA du Cloud.** Seul le contexte structurel anonymisé quitte la machine locale.

#### 5.1 PHASE 0 : La Fondation (Le "Gros Ticket" Gratuit)

Cette phase préliminaire se déroule en dehors de la rigueur et du coût du cycle Agile.

| Étape | Acteur | Input | Outil / Modèle | Livrable |
|-------|--------|-------|----------------|----------|
| Discovery & Ideation | R-1 (humain) + R-0 (IA) | Idée initiale, hypothèses | Cascade : gemma3:12b → Gemini 2.5 Flash (Web/API) → Opus 4.6 | Notes de Discovery |
| Cristallisation | R-0 (IA) | Notes de Discovery | Idem | **Gros Ticket initial mature** (Epic) |

*Règle : privilégier gemma3:12b en local. Escalade uniquement si blocage ou limite 429. **H1** : R-1 valide le Gros Ticket avant passage en Phase 1.*

#### 5.2 PHASE 1 à N : L'Usine Agile — Flux Détaillés et Livrables

| Étape | Acteur | Input | Outil / Modèle | Livrable | Qui délivre quoi | Human-in-the-Loop |
|-------|--------|-------|----------------|----------|------------------|-------------------|
| **E1 – Initialisation** | R-1 | Gros Ticket | VS Code, Continue.dev, `index_rag.py` | **Besoins - Product Backlog.md** | R-1 injecte le Gros Ticket validé (H1) dans le Backlog. Indexation RAG (Backlog) déclenchée. Continue.dev indexe la codebase. | **H1** : R-1 valide le Gros Ticket avant E1 |
| **E2 – Backlog Refinement** | R-2 | Backlog, Gros Ticket | Cascade : gemma3:12b → AI Studio → Opus 4.6 | **Architecture.md**, **DoD** (draft), **ADR-{NNN}** | R-2 produit Architecture.md + draft DoD (Pydantic) + ADR (compteur adr_counter). Payload H2 : Architecture.md + draft DoD. R-1 amende DoD, R-7 valide. Indexation RAG (architecture + dod). BaseStore : architecture_approved + DoD. Si rejected : relance R-2 avec feedback (max 3 cycles). Voir III.8-B et III.8-O. | **H2** : R-7/R-1 valident architecture et finalisent DoD |
| **E3 – Sprint Planning** | R-3 | Backlog, Architecture.md, DoD | Cascade : qwen2.5-coder:7b → AI Studio → Sonnet 4.6 | **Sprint Backlog** | R-3 découpe en micro-tâches. Priorité local. Si rejected : relance R-3 avec feedback (max 3 cycles). Voir III.8-B. | **H3** : R-1 valide le découpage avant E4 |
| **E4 – Sprint Execution** | R-4, R-5 | Sprint Backlog, DoD | LangGraph (nœuds R-4, R-5) + tools (read_file, write_file, run_shell) | Code source, tests unitaires, feature branch | R-4 génère le code via tools. R-5 gère Git. Automatique. Hook post-commit : différé si AGILE_DEFER_INDEX=true (pending_index.log). En cas de conflit Git : H6. Voir III.8-C. | — |
| **E5 – CI/CD Pipeline (local)** | R-6 | Code, DoD | Docker, Jest/Pytest, Linters, Sphinx/JSDoc + Cascade | **Test Reports**, verdict Pass/Fail | R-6 exécute build_docs puis tests locaux. Self-Healing R-6→R-4 si échec (max 3). CI vert → déclenche H4. GitHub Actions = CI de validation PR (avant merge main). Voir III.8-F et III.8-N. | **H4** : CI vert déclenche H4 (Sprint Review R-7). **H5** si escalade N2. |
| **E6 – Sprint Review & Retrofit** | R-7 | Incrément, DoD | VS Code, Continue.dev | **Go/No-Go**, mise à jour Backlog | E6 = phase post-H4. R-7 prononce Go/No-Go (via H4 resume). Si rejected : nouveau cycle E4→E5. Si approved : Retrofit Backlog (R-1). Nœud sprint_complete : sprint_summary, sprint_number++, index_rag (traite pending_index.log si AGILE_DEFER_INDEX). Si auto_next_sprint : boucle E3. Voir III.8-E et III.8-M. | — (H4 géré en E5) |

###

* * *

Annexe A. Cartographie Financière et Technique de l'Écosystème

Cette cartographie répertorie les technologies selon leur impact financier, validant le modèle de déploiement "Cascade".

#### 🖥️ 1. Local & Gratuit (L'Infrastructure de Base & Exécution)

L'arsenal qui tourne sur votre machine, maximisant la rentabilité de votre matériel (0€ au-delà de l'électricité).

* **NVIDIA RTX 3060 12G :** Le cœur matériel de l'usine, offrant la VRAM nécessaire pour l'exécution d'IA locale (modèles Q4) sans latence réseau, sans coût par token, et avec une confidentialité absolue à 100%.
* **Ollama :** Moteur d'exécution des LLMs locaux. Modèles installés : `qwen2.5-coder:7b` (code) et `gemma3:12b-it-q4_K_M` (idéation/architecture).
* **LangGraph + LangChain** : Backbone d'orchestration des agents. Voir section III.5.
* **Git & MCP (Model Context Protocol) :** Contexte structuré de la codebase. chroma-mcp pour RAG partagé agents + IDE (voir III.7-bis).
* **Chroma + nomic-embed-text :** RAG pour les agents (codebase, Architecture.md, Backlog, ADRs). Mémoire long terme via LangGraph BaseStore. Voir III.7.
* **Docker, Jest/Pytest, GitHub Actions :** Isolation, tests, CI/CD.

#### 💻 2. Local & Gratuit (L'Interface de Pilotage Open-Source)

L'interface de travail remplaçant les abonnements mensuels fixes (ex: Cursor).

* **VS Code + Continue.dev + Roo Code :** Cockpit central (Hub ENV-B). Continue.dev : autocomplétion alimentée par Ollama (RTX 3060). Roo Code : agents d'exécution autonomes. **0€/mois**.

#### ☁️ 3. Cloud & Gratuit (La Maturation et le Fallback)

* **Google AI Studio (Free Tier API) :** Modèles `gemini-2.5-flash` ou `gemini-2.5-flash-lite`. Fallback Niveau 1 (N1) de la cascade. Limites : 10 RPM, 250–500 RPD, 250K TPM.
* **LangSmith (Free Tier) :** 5000 traces/mois, rétention 14 jours. Traçage obligatoire des workflows LangGraph pour débogage et optimisation.
* _Règle d'intégration :_ Exponential Backoff obligatoire sur **HTTP 429** pour absorber les limites du Free Tier.

#### 🌩️ 4. Cloud & Pay-as-you-go (L'Expertise Critique en Ultime Recours)

* **API Claude Opus 4.6 :** Décisions d'architecture majeures (R-2). ~5 $/M tokens input, ~25 $/M output.
* **API Claude Sonnet 4.6 :** Exécution complexe (R-4, R-6). ~3 $/M input, ~15 $/M output. Utiliser le Prompt Caching pour réduire les coûts.

---

VI. Stratégies d'Optimisation des Coûts et des Ressources

| Stratégie | Description | Impact |
|-----------|-------------|--------|
| **Étalement des tâches** | Répartir les appels API sur la journée pour respecter les limites RPD (ex. Gemini 250–500 req/jour). Éviter les pics de consommation. | Réduction des 429, pas de surcoût cloud |
| **Prompt Caching (Anthropic)** | Réutiliser les contextes longs (Architecture.md, Backlog) via le cache. Cached reads : ~90 % de réduction sur Opus/Sonnet. | Jusqu'à 50 % d'économie sur les gros contextes |
| **Batch API (Anthropic)** | Regrouper les tâches non bloquantes (analyse de logs, génération de rapports, revues de code) et les soumettre en batch : 50 % de réduction. Utiliser systématiquement pour tout appel N2 non synchrone. | Jusqu'à 50 % d'économie sur Opus/Sonnet |
| **Anonymisation systématique** | Avant toute escalade cloud : supprimer secrets, données personnelles, chemins locaux. Envoyer uniquement des structures anonymisées. | Confidentialité + évite les fuites |
| **Seuils d'escalade stricts** | N0→N1 : après 2 échecs consécutifs ou HTTP 429. N1→N2 : après 1 échec N1 ou complexité > 500 lignes de contexte. H5 obligatoire avant tout appel N2 : approbation humaine. | Réduction des appels Opus/Sonnet, contrôle des coûts |
| **Backoff HTTP 429** | 3 tentatives max, backoff exponentiel (2^attempt s). Si 429 persiste : H5 (approbation N2) ou "pause et retry demain". Variable `API_429_MAX_RETRIES=3`. Voir III.10 (S6). | Résilience face aux quotas Free Tier |
| **Tests et lint locaux en priorité** | R-6 exécute Jest/Pytest en local. L'IA ne sert qu'à l'analyse des logs en cas d'échec. | 0 € pour la majorité des cycles |
| **Dépôts publics GitHub** | Utiliser des dépôts publics pour GitHub Actions : minutes illimitées gratuites. | 0 € CI/CD |
| **Contexte minimal** | Limiter la taille du contexte envoyé aux API (extraits pertinents, pas la codebase complète). | Moins de tokens = moins de coût |

---

VII. Exigences Transversales : Testabilité, Tracabilité, Modularité

| Exigence | Implémentation | Acteur / Outil |
|----------|----------------|----------------|
| **Testabilité by design** | TDD obligatoire : tests écrits avant ou avec le code. Couverture minimale définie dans la DoD. | R-4 (Dev Team), R-6 (QA) |
| **Tracabilité** | Chaque ticket lié à un commit ; Architecture.md et Backlog versionnés dans Git. ADRs (Architecture Decision Records) obligatoires pour toute décision impactant l'architecture : traçabilité des choix, justifications, et alternatives écartées. | R-5 (Release Manager), R-2 (Architecte), Git |
| **Journalisation** | Logs structurés (JSON) dans les pipelines CI/CD. Conservation des outputs IA (prompts/réponses) pour audit et amélioration. | R-6, GitHub Actions, fichiers `logs/` |
| **Tests end-to-end** | Suite E2E obligatoire pour projets web : **Playwright** (recommandé, multi-navigateur, stable). Déclenchée avant merge. Définie dans la DoD. Pour projets non-web : tests d'intégration (Pytest, Jest) suffisants. | R-6, pipeline CI |
| **Documentation** | README, Architecture.md, DoD à jour. DoD co-construite en H2 (R-2 draft + R-1 amende + R-7 valide), versionnée dans Git et BaseStore. Génération auto : **JSDoc** (JS/TS) ou **Sphinx** (Python). build_docs dans E5 (R-6). Checklist de clôture (III.8-M). Voir III.8-B (DoD/H2) et III.8-N (build_docs). | R-2 (DoD draft, ADRs), R-1 (amende DoD), R-7 (valide), R-6 (E5) |
| **Modularité** | Découpage en modules/bibliothèques réutilisables. Architecture.md impose les frontières. | R-2 (Architecture), R-4 (implémentation) |

---

VIII. Rapports de Simulation

**Objectif** : Les simulations permettent de valider l'écosystème sur plusieurs semaines, d'identifier les problèmes et manques, puis d'intégrer les corrections. Chaque rapport est numéroté et daté pour permettre des itérations successives.

| Numéro | Date | Fichier | Corrections intégrées |
|--------|------|---------|------------------------|
| **001** | 2026-03-01 | `specs/Simulation_001_2026-03-01.md` | Procédures H1–H6, pipeline indexation RAG, articulation E4 (LangGraph + tools), seuil Self-Healing (3), flux BaseStore, stratégie GPU, politique LangSmith, politique rétention (section III.8) |
| **002** | 2026-03-02 | `specs/Simulation_002_2026-03-02.md` | R1–R5, N1–N2 intégrés (section III.9) : handle_interrupt --thread-id, nœuds post_h1/post-H2/post-H4, index_rag emplacement/paramètres, project_root/project_id dans état, multi-projets, résilience index_rag. |
| **003** | 2026-03-03 | `specs/Simulation_003_2026-03-03.md` | S1–S12 intégrés (section III.10). |
| **004** | 2026-03-04 | `specs/Simulation_004_2026-03-04.md` | T1–T8 intégrés (section III.11). |
| **005** | 2026-03-05 | `specs/Simulation_005_2026-03-05.md` | Validation T1–T8. Convergence déclarée — réexaminée par Sim 006. |
| **006** | 2026-03-06 | `specs/Simulation_006_2026-03-06.md` | U1–U8 intégrés (section III.12) : DoD/H2 flux, branches rejected H1–H4, indexation différée GPU (AGILE_DEFER_INDEX), H4 trigger clarifié, numérotation ADRs, sprint_number état TypedDict, GitHub Actions vs R-6, clôture projet. |
| **007** | 2026-03-07 | `specs/Simulation_007_2026-03-07.md` | V1–V7 intégrés (section III.13) : payload H5 reason, nœud load_context, re-déclenchement E2, stratégie branches Git (feature/sprint+develop+main), H4 après H5 clarifié, DoD versionnée par sprint, H4-rejected cycle correctif. |
| **008** | 2026-03-08 | `specs/Simulation_008_2026-03-08.md` | W1–W6 intégrés (section III.14) : start_phase E1/E3, architectural_change Pydantic, DoD fallback sprint N-1, H4 conditionné GitHub Actions, workflow hotfix, AGILE_PROJECTS_JSON. |
| **009** | 2026-03-09 | `specs/Simulation_009_2026-03-09.md` | X1–X4 intégrés (section III.15) : CI 1 feature→develop / CI 2 develop→main, push unique fin E4, polling GitHub Actions via gh run watch (GITHUB_ACTIONS_TIMEOUT), AGILE_BASESTORE_STRICT. |
| **010** | 2026-03-10 | `specs/Simulation_010_2026-03-10.md` | Y1–Y5 intégrés (section III.16) : branche develop init, gh pr create/checks, merge_to_main nœud, start_phase HOTFIX, mode dégradé github_repo absent. |
| **011** | 2026-03-11 | `specs/Simulation_011_2026-03-11.md` | Z1–Z2 intégrés (section III.17) : sprint_complete en deux phases (sprint_summary puis merge_to_main avec incrément sprint_number après CI 2), branch protection GitHub documentée. |
| **012** | 2026-03-12 | `specs/Simulation_012_2026-03-12.md` | AA1–AA2 intégrés (section III.18) : sprint_number mode dégradé (incrément phase 1 si github_repo absent), suppression notation H4' (→ H5 reason=pr_review_required), catalogue complet reasons H5. Convergence définitive atteinte. |
| **013** | 2026-03-13 | `specs/Simulation_013_2026-03-13.md` | BB1–BB4 intégrés (section III.19) : numérotation checklist, W5 start_phase HOTFIX, hotfix→develop merge direct, auto_next_sprint boucle après phase 2. **Convergence définitive — zéro problème résiduel.** |

**Règle** : Simulations 001–013 validées et intégrées. Corrections consolidées en III.8. Historique détaillé en Annexe B. Spec **convergé et opérationnel** — prêt pour implémentation.


---

### Annexe B. Historique des Corrections par Simulation (001–013)

*Cette annexe conserve l'intégralité des listes de corrections incrémentales issues des simulations 001 à 013. Elle constitue la traçabilité complète des décisions de conception. Le document opérationnel de référence est la section III.8.*


#### B.1 Corrections Simulation 001 — Procédures opérationnelles initiales

*Source : Simulation_001_2026-03-01.*

**Procédure Human-in-the-Loop (interrupts H1–H6)** :
- Utiliser le endpoint LangServe `/playground` ou le script `scripts/handle_interrupt.py [--thread-id <id>]`. Si `--thread-id` est omis et plusieurs interrupts sont en attente : le script liste les threads **triés par project_id puis par type H (H1 avant H2…)** — ou par timestamp — et demande de choisir. Si `--thread-id` est fourni mais le thread n'a pas d'interrupt en attente : message d'erreur explicite, exit code 1 (voir III.10 S1, III.11 T8). Puis : (1) lit l'état du graphe via l'API, (2) affiche le payload `__interrupt__`, (3) attend l'entrée (approved | rejected | feedback), (4) envoie `graph.invoke(Command(resume=...), config)`. Voir III.9 (R1).
- En absence de l'humain : le graphe reste en attente. Option "rejeter avec report" : `resume={"status":"rejected","resume_after":"2026-03-05"}` pour programmer une reprise différée. Notification optionnelle (email, script) si un interrupt reste non traité > 48h.
- **H6 (nouveau)** : Si R-5 échoue à résoudre un conflit Git après 2 tentatives → interrupt dédié. L'humain résout manuellement (VS Code, `git mergetool`), commit, puis `Command(resume="resolved")` pour reprendre.

**Pipeline d'indexation RAG** :
- Déclencheurs : (1) **Nœud post_h1** (après H1 resume) : `run_shell(index_rag.py --project-root {state.project_root} --project-id {state.project_id} --sources backlog)`. **Ordre obligatoire** : R-1 doit avoir injecté le Gros Ticket dans le Backlog et committé *avant* d'envoyer `Command(resume)` sur H1, sinon post_h1 indexe un fichier vide ou inexistant (voir III.11 T1). **Hook et E4** : Si `AGILE_DEFER_INDEX=true` dans `.agile-env`, le hook post-commit ne lance pas index_rag immédiatement mais enregistre un fichier `logs/pending_index.log` (timestamp + commit hash). L'indexation est ensuite déclenchée par sprint_complete (fin E6), éliminant les conflits GPU pendant E4/E5. Voir III.12 (U3). (2) **Nœud post-H2** : idem `--sources architecture` ; (3) **Nœud post-H4** : idem `--sources all` ; (4) **Hook Git** post-commit : lit `$AGILE_ORCHESTRATION_ROOT` et `$AGILE_PROJECT_ID` (ou fichier `.agile-project-id`), appelle `python $AGILE_ORCHESTRATION_ROOT/scripts/index_rag.py --project-root $(pwd) --project-id $AGILE_PROJECT_ID`. **Bootstrap** : `scripts/setup_project_hooks.sh` (voir III.10 S2, III.11 T2, T3).
- Script `index_rag.py` : vit dans le projet orchestration. Signature : `--project-root <path> --project-id <id> [--sources backlog|architecture|code|all] [--strict]`. Résilience : try/except par fichier, skip en erreur, rapport final écrit dans `logs/index_rag_<timestamp>.log`. Si `--strict` et aucun fichier indexé avec succès : exit 1. Alerte si > 10 % de fichiers en erreur : log warning. Voir III.9 (R3, N2), III.10 (S5, S7).

**Articulation E4 : LangGraph pilote, tools filesystem/Git** : E4 est piloté par le nœud R-4 du graphe LangGraph. R-4 dispose de tools : `read_file`, `write_file`, `run_shell` (git, npm, etc.). Roo Code et Continue.dev restent l'interface humaine pour inspections et corrections manuelles ; le graphe n'attend pas de callback Roo Code. R-4 traite les tickets séquentiellement, écrit le code via `write_file`, et R-5 (nœud graphe) appelle `run_shell` pour git. Pour les tâches de code interactif (pair programming), Nghia peut utiliser Roo Code en dehors du flux automatisé.

**Seuil Self-Healing** : Configuration fixe : `SELF_HEALING_MAX_ITERATIONS = 3`. Au-delà de 3 cycles R-6→R-4 sans succès → interrupt H5 (approbation humaine pour escalade N2 ou arrêt avec rapport d'échec).

**Stratégie GPU (Ollama)** : Un seul modèle chargé à la fois. Ordre de priorité : qwen2.5-coder (E4, E5) > gemma3 (E0, E2). Configurer `OLLAMA_KEEP_ALIVE` pour le modèle prioritaire du flux en cours. Éviter d'exécuter des indexations RAG massives (nomic-embed-text) pendant E4/E5 ; lancer l'indexation en fin de journée ou entre sprints.

**Politique de traçage LangSmith** : En cas de risque de dépassement 5000 traces/mois : configurer `LANGCHAIN_TRACING_SAMPLING_RATE=0.2` (20 % des runs) ou `LANGCHAIN_TRACING_ERRORS_ONLY=true` pour tracer uniquement les échecs. Priorité : conserver les traces des runs en erreur pour débogage.

**Politique de rétention** : Purge des checkpoints > 90 jours (script `scripts/purge_checkpoints.py`). Critères : "90 jours" = dernier step du thread. **Exclure** les threads ayant un `__interrupt__` non résolu. Signature : `purge_checkpoints.py [--dry-run] [--max-age-days 90]`. Voir III.10 (S8). Chroma : une collection par projet ; archiver (export) avant suppression. Procédure : `scripts/export_chroma.py --project-id <id> --output <path>` et `import_chroma.py` pour réimport. Limite logs : rotation 7 jours, max 100 Mo.

#### B.2 Corrections Simulation 002 (R1–R5, N1–N2)

*Les éléments ci-dessous proviennent du rapport Simulation_002_2026-03-02 et corrigent les problèmes résiduels et nouveaux identifiés.*

**R1 — handle_interrupt.py : identification du thread_id**  
*Problème* : Lorsque plusieurs projets ou sprints ont un interrupt en attente, le script ne sait pas quel thread traiter.  
*Correction* : `handle_interrupt.py` accepte l'argument optionnel `--thread-id <id>`. S'il est omis, le script interroge l'API LangServe pour lister les threads dont l'état contient `__interrupt__`, affiche la liste (thread_id, type H1–H6, timestamp), et demande à l'utilisateur de choisir. Justification : permet de gérer plusieurs projets en parallèle sans confusion.

**R2 — Mécanisme de déclenchement indexation à E1**  
*Problème* : E1 est une action humaine (R-1 injecte le Backlog). L'indexation "Fin E1" n'était pas rattachée à un mécanisme explicite.  
*Correction* : Deux déclencheurs complémentaires. (1) **Hook Git post-commit** : lorsque le Backlog est committé, le hook lance `index_rag.py --project-root $(pwd) --project-id <id>`. (2) **Nœud graphe "post_h1"** : après `Command(resume=...)` sur H1, un nœud exécute `run_shell(index_rag.py ...)` pour indexer le Backlog avant de passer à E2. Le nœud post_h1 garantit l'indexation même si le hook Git n'est pas configuré. Justification : redondance pour fiabilité ; le hook couvre les mises à jour ultérieures du Backlog.

**R3 — Emplacement et paramètres de index_rag.py**  
*Problème* : Emplacement du script (orchestration vs projet) et paramètres non spécifiés.  
*Correction* : Le script vit dans le **projet orchestration** (répertoire du graphe LangGraph). Signature : `python scripts/index_rag.py --project-root <path> --project-id <id> [--sources backlog|architecture|code|all]`. `--project-root` : chemin absolu du projet cible (ex. dépôt kanban). `--project-id` : identifiant pour la collection Chroma (ex. `kanban`, `api-meteo`). `--sources` : limite l'indexation (défaut `all`). Justification : un seul script, réutilisable pour tous les projets ; les chemins sont passés explicitement, pas de configuration implicite.

**R4 — Ordre des opérations post-H2 et post-H4**  
*Problème* : Ordre flou entre écriture BaseStore, indexation et reprise du graphe.  
*Correction* : Pour tout interrupt H2, H4 (et H1), le nœud qui reçoit le `resume` exécute dans cet ordre : (1) mise à jour de l'état avec le feedback utilisateur ; (2) écriture en BaseStore si applicable (H2 → architecture_approved, H4 → sprint_summary) ; (3) appel à `index_rag.py` avec les sources pertinentes ; (4) transition vers le nœud suivant. Justification : garantit que la mémoire et le RAG sont à jour avant que le flux ne reprenne.

**R5 — project_root et project_id dans l'état du graphe**  
*Problème* : Les nœuds R-4, R-5 et les tools doivent connaître le chemin du projet.  
*Correction* : L'état TypedDict inclut obligatoirement `project_root: Path` et `project_id: str`. Initialisation : à l'entrée du flux (Phase 0 ou E1), l'invocation du graphe reçoit en config `{"configurable": {"thread_id": "...", "project_root": "/path/to/projet", "project_id": "kanban"}}`. Ces valeurs sont injectées dans l'état initial. Les tools `read_file`, `write_file`, `run_shell` utilisent `project_root` comme répertoire de travail. Justification : évite les chemins en dur ; un même graphe peut traiter plusieurs projets.

**N1 — Gestion multi-projets**  
*Problème* : Plusieurs projets en parallèle : project_id, project_root, handle_interrupt.  
*Correction* : Convention `thread_id` : `{project_id}-phase-0` (Phase 0) ou `{project_id}-sprint-{NN}` (sprint N, padding 2 chiffres : 01, 02, …). Exemples : `kanban-phase-0`, `kanban-sprint-01`, `api-meteo-sprint-02`. Voir III.11 (T5). Une config `projects.json` associe `project_id` → `path` (et optionnellement `auto_next_sprint`). Format : `{"kanban": {"path": "/home/user/kanban", "auto_next_sprint": false}, "api-meteo": {"path": "..."}}`. `handle_interrupt.py` affiche les interrupts groupés par project_id. Justification : isolation, traçabilité, tri correct.

**N2 — Résilience de index_rag.py**  
*Problème* : Un fichier ou un chunk problématique peut faire échouer toute l'indexation.  
*Correction* : Le script traite chaque fichier dans un try/except. En cas d'erreur sur un fichier (encoding, chunk trop long, embedding échoué) : log de l'erreur, skip du fichier, poursuite des autres. En fin d'exécution : rapport (fichiers indexés, fichiers en erreur, total). Option `--strict` : si aucun fichier n'a été indexé avec succès, exit code 1 (pour alerter les hooks). Justification : un fichier corrompu ou atypique ne bloque pas l'indexation du reste du projet ; le rapport permet de diagnostiquer.

#### B.3 Corrections Simulation 003 (S1–S12)

*Les éléments ci-dessous proviennent du rapport Simulation_003_2026-03-03 et corrigent les problèmes identifiés en conditions multi-projets et longue durée.*

**S1 — handle_interrupt.py : validation du thread_id**  
Si `--thread-id` est fourni mais le thread n'a pas d'interrupt en attente : message d'erreur explicite, exit code 1. Exit codes : 0=succès, 1=erreur (thread invalide, etc.), 2=usage (arguments invalides). Voir III.11 (T8).

**S2 — Bootstrap hooks Git pour nouveau projet**  
Script `scripts/setup_project_hooks.sh` : à exécuter lors de la création d'un nouveau dépôt. Signature : `--orchestration-root <path> --project-root <path> --project-id <id>`. Le script : (1) crée un fichier `.agile-project-id` à la racine du projet (contenu : project_id) ; (2) crée un fichier `.agile-env` ou configure le hook pour lire `AGILE_ORCHESTRATION_ROOT` et `AGILE_PROJECT_ID` au runtime (pas de chemin figé). Voir III.11 (T2, T3).

**S3 — Ordre d'affichage des interrupts**  
Quand `handle_interrupt.py` liste les threads sans `--thread-id`, tri par `project_id` puis par type H (H1, H2, H3, H4, H5, H6). Alternative : tri par timestamp (plus ancien en premier).

**S4 — Boucle E6 → E3 (sprint N+1)**  
Après E6, le nœud "sprint_complete" : (a) écrit sprint_summary en BaseStore (namespace `project/{id}/sprints`) et déclenche index_rag (ou traite `pending_index.log` si `AGILE_DEFER_INDEX=true`) ; (b) incrémente `state.sprint_number` et écrit la nouvelle valeur dans BaseStore (`project/{id}/sprint_counter`) ; (c) consulte `projects.json` pour `projects[project_id].auto_next_sprint` (défaut : false). Si true : boucle vers E3 avec `thread_id={project_id}-sprint-{NN}` (N+1, padding 2 chiffres, calculé depuis `state.sprint_number`). **Timing** : la boucle E3 se déclenche après la phase 2 (merge_to_main complet, sprint_number incrémenté) ; en mode dégradé (github_repo absent), après la phase 1 (incrément immédiat). Voir III.19 (BB4). Si false : termine avec message pour invocation manuelle. Voir III.11 (T4, T5), III.12 (U6).

**S5 — Rapport index_rag consommé**  
Le script `index_rag.py` écrit son rapport dans `logs/index_rag_<timestamp>.log` (répertoire du projet orchestration). Le hook Git ou un wrapper peut rediriger stdout/stderr vers ce fichier. Permet un audit ultérieur.

**S6 — Backoff HTTP 429 et gestion quota**  
Stratégie retry sur HTTP 429 : 3 tentatives max, backoff exponentiel (2^attempt secondes). Configurer les connecteurs LangChain (Google, Anthropic) avec `max_retries=3` et backoff. Si 429 persiste après 3 retries : considérer "quota épuisé" → déclencher H5 pour approbation N2 (Sonnet/Opus) ou option "pause et retry demain". Variable `API_429_MAX_RETRIES=3`.

**S7 — Alerte sur échec index_rag**  
Si `index_rag.py` s'exécute avec `--strict` et exit 1 (aucun fichier indexé), ou si > 10 % des fichiers sont en erreur : écrire une entrée dans `logs/index_errors.log` avec timestamp, project_id, nombre d'erreurs. Option : notification (email, script) si ce fichier est consulté par un cron de monitoring.

**S8 — Purge checkpoints : critères détaillés**  
Script `purge_checkpoints.py` : `--max-age-days 90` (défaut), `--dry-run` (affiche sans supprimer). "90 jours" = date du dernier step du thread. **Exclure** les threads dont l'état contient `__interrupt__` (interrupt non traité). Log des threads supprimés.

**S9 — Rétention traces LangSmith**  
Rétention 14 jours (free tier). Pour audit long terme : option d'export périodique via API LangSmith vers stockage local (fichiers JSON) ou S3. Script `scripts/export_langsmith_traces.py` (optionnel, hors scope minimal). Documenter que la rétention courte est assumée.

**S10 — Archivage Chroma**  
Scripts `scripts/export_chroma.py --project-id <id> --output <path>.json` et `scripts/import_chroma.py --project-id <id> --input <path>.json`. Format : export JSON des vecteurs et métadonnées. Avant suppression d'un projet : exporter, puis supprimer la collection. Pour réactiver : importer.

**S11 — Sync Architecture.md et artefacts**  
Nœud optionnel "sync_artifacts" ou tâche cron : compare le code (structure des modules) à Architecture.md et génère un rapport de dérive. R-2 produit un ADR à la fin de E2 (décisions d'architecture) via template Pydantic ; numérotation : `ADR-{NNN}-{date}-{slug}.md` où NNN provient du compteur `adr_counter` (état TypedDict, incrémenté par R-2). Voir III.12 (U5). Projets terminés dans `projects.json` : flag `"archived": true` pour les garder en référence sans les traiter comme actifs.

**S12 — Génération documentation (Sphinx/JSDoc)**  
Étape "build_docs" dans E5 (avant les tests) : R-6 exécute `sphinx-build` (Python) ou `npm run docs` (JS/TS). Si pas de `conf.py` (Python) ou `jsdoc.json` (JS/TS) : skip avec log. Variable `BUILD_DOCS_REQUIRED=false` (défaut) : si true, échec bloque. Voir III.11 (T6).

#### B.4 Corrections Simulation 004 (T1–T8)

*Les éléments ci-dessous proviennent du rapport Simulation_004_2026-03-04 et corrigent les derniers problèmes résiduels.*

**T1 — Ordre H1 / E1 / post_h1**  
R-1 doit injecter le Gros Ticket dans `Besoins - Product Backlog.md` et committer *avant* d'envoyer `Command(resume="approved")` sur H1. Sinon, post_h1 indexe un fichier inexistant ou vide. Procédure : (1) valider le Gros Ticket (H1 affiché), (2) créer le dépôt projet si besoin, (3) créer le fichier Backlog avec le contenu du Gros Ticket, (4) commit, (5) lancer handle_interrupt et envoyer resume.

**T2 — project_id dans le hook**  
Le hook ne doit pas utiliser `$(basename $(pwd))` (peut différer de projects.json). Utiliser un fichier `.agile-project-id` à la racine du projet (contenu : project_id sur une ligne), ou la variable `AGILE_PROJECT_ID` définie par setup_project_hooks. setup_project_hooks reçoit `--project-id <id>` et écrit ce fichier ou configure l'env.

**T3 — ORCHESTRATION_ROOT non figé**  
Le hook lit `$AGILE_ORCHESTRATION_ROOT` au moment de l'exécution (pas de chemin absolu figé). setup_project_hooks crée un wrapper qui exporte cette variable avant d'appeler index_rag. Ou : fichier `.agile-env` à la racine du projet avec `AGILE_ORCHESTRATION_ROOT=/path`. Ce fichier est généré par setup_project_hooks.

**T4 — Config auto_next_sprint**  
Format `projects.json` étendu : `{"<project_id>": {"path": "/path", "auto_next_sprint": true|false}}`. Défaut : false. Le nœud sprint_complete consulte cette config pour décider de boucler vers E3.

**T5 — Format thread_id pour sprints**  
Convention : `{project_id}-sprint-{NN}` avec padding 2 chiffres (sprint-01, sprint-02, …). Évite les tri alphabétiques incorrects (sprint-10 avant sprint-2). Documenter dans N1.

**T6 — build_docs si pas de config**  
Si aucun `conf.py` (Sphinx) ou `jsdoc.json` : skip avec log "No doc config, skipping build_docs". Variable `BUILD_DOCS_REQUIRED` : false (défaut) = skip silencieux ; true = échec si pas de config.

**T7 — Déclenchement sync_artifacts**  
Optionnel. Déclenchement : cron (ex. `SYNC_ARTIFACTS_CRON="0 0 * * 0"` = dimanche minuit) ou invocation manuelle du nœud. Si non configuré : désactivé.

**T8 — Exit codes handle_interrupt**  
Normalisation : 0 = succès ; 1 = erreur (thread sans interrupt, ou autre) ; 2 = usage (arguments invalides, ex. --thread-id manquant quand requis). Documenter dans la doc du script.

#### B.5 Corrections Simulation 006 (U1–U8)

*Les éléments ci-dessous proviennent du rapport Simulation_006_2026-03-06. Ils corrigent des ambiguïtés critiques non couvertes par les simulations 001–005.*

**U1 — Co-construction de la DoD dans H2**  
*Problème* : La DoD n'avait pas de flux de création explicite dans le graphe. R-1 est humain, sans nœud dédié ; aucun interrupt H ne portait la DoD.  
*Correction* : Le nœud R-2 (E2) génère un *draft* DoD via template Pydantic (critères basés sur Architecture.md). Le payload H2 contient Architecture.md **et** ce draft DoD. Lors de la validation H2, R-1 amende la DoD (critères d'acceptation métier) et R-7 valide l'ensemble. La DoD finalisée est stockée dans `state.dod` (TypedDict) et écrite en BaseStore (`project/{id}/dod`). Elle est indexée dans le RAG (nœud post-H2 : `--sources architecture,dod`). R-6 charge la DoD depuis l'état ou le BaseStore en E5.

**U2 — Branches "rejected" sur interrupts H1–H4**  
*Problème* : `Command(resume={"status":"rejected"})` n'avait pas de comportement défini pour chaque interrupt. Sans boucle de correction, le pipeline se bloquait ou terminait en erreur.  
*Correction* : Chaque nœud qui reçoit un `resume` vérifie `status` :  
- H1 rejected : injecter le feedback dans l'état (`state.h1_feedback`), reboucler vers R-0 (R-0 produit un nouveau Gros Ticket en tenant compte du feedback). Limite : 3 cycles, puis arrêt avec rapport.  
- H2 rejected : injecter le feedback dans `state.h2_feedback`, reboucler vers R-2 (Architecture + DoD revisitées). Limite : 3 cycles.  
- H3 rejected : injecter dans `state.h3_feedback`, reboucler vers R-3 (Sprint Backlog refait). Limite : 3 cycles.  
- H4 rejected : injecter dans `state.h4_feedback`, R-4/R-5 traitent le correctif (nouveau cycle E4→E5). Nouveau CI requis. H4 se redéclenche après CI vert.  
Convention : si la limite de 3 cycles est atteinte pour H1/H2/H3 → interrupt H5 (escalade humaine).

**U3 — Indexation différée pendant E4/E5 (conflit GPU)**  
*Problème* : Le hook Git post-commit lance nomic-embed-text après chaque commit de R-5 en E4, provoquant un conflit GPU avec qwen2.5-coder.  
*Correction* : Variable `AGILE_DEFER_INDEX=true` dans `.agile-env` (configurée par `setup_project_hooks.sh`). Comportement hook modifié : si `AGILE_DEFER_INDEX=true`, le hook écrit une ligne dans `logs/pending_index.log` (format : `<timestamp> <commit_hash> <project_id>`) au lieu de lancer index_rag. Le nœud sprint_complete lit `pending_index.log`, lance index_rag une seule fois en fin de sprint (hors E4/E5), puis vide le fichier. Valeur par défaut : `AGILE_DEFER_INDEX=false` (comportement actuel inchangé si non configuré).

**U4 — H4 : clarification du point de déclenchement**  
*Problème* : H4 était décrit simultanément comme "fin E6" (tableau III.6) et "pipeline CI/CD au vert" (tableau V.5.2), créant une incohérence sur le moment exact de l'interrupt.  
*Correction* : H4 est déclenché **à la fin de E5** (pipeline CI/CD au vert, R-6 valide). Le graphe suspend. R-7 effectue alors le Sprint Review (inspecte l'incrément) et prononce le Go/No-Go via `Command(resume={"status":"approved"|"rejected"})`. E6 = phase post-H4 : Retrofit Backlog (si approuvé) + nœud sprint_complete. Cette séquence est désormais cohérente entre III.6 et V.5.2.

**U5 — Numérotation et compteur des ADRs**  
*Problème* : Les ADRs produits par R-2 à la fin de E2 n'avaient pas de convention de numérotation, risquant des collisions (ex. ADR-001 créé deux fois).  
*Correction* : `adr_counter: int` dans l'état TypedDict (valeur initiale : 0). À chaque ADR produit par R-2 : incrémenter `state.adr_counter`, écrire la valeur dans BaseStore (`project/{id}/adr_counter`). Nom de fichier : `docs/ADR-{NNN:03d}-{date}-{slug}.md` (ex. `ADR-001-2026-03-06-architecture-initiale.md`). La valeur est chargée depuis BaseStore au démarrage d'un nouveau thread (pour éviter les collisions entre sessions).

**U6 — sprint_number dans l'état TypedDict**  
*Problème* : Le nœud sprint_complete dérivait N+1 en parsant le thread_id courant, fragile si le format du thread_id était non standard.  
*Correction* : `sprint_number: int` dans l'état TypedDict (valeur initiale : 1). sprint_complete est en deux phases : (1) sprint_summary — écriture BaseStore, index_rag, sprint_number reste N **sauf en mode dégradé** (github_repo absent) où sprint_number est incrémenté ici directement ; (2) merge_to_main — si github_repo présent, après CI 2 vert, incrément sprint_number → N+1 et écriture BaseStore. Voir III.17 (Z1), III.18 (AA1). Le thread_id suivant est `f"{project_id}-sprint-{state.sprint_number:02d}"`. Au démarrage d'un thread, `sprint_number` est chargé depuis BaseStore si disponible.

**U7 — Relation GitHub Actions / nœud R-6**  
*Problème* : GitHub Actions (CI/CD) et R-6 (nœud LangGraph) étaient deux pipelines CI distincts, sans relation documentée.  
*Correction* : Rôles complémentaires : (1) **R-6 (LangGraph)** = CI local sur feature branch avant merge (E5 : Docker, Jest/Pytest, lint, build_docs). Doit passer pour déclencher H4. (2) **GitHub Actions** = CI de validation sur PR et merge main (tests d'intégration, tests E2E Playwright). Doit passer avant que R-5 ne merge la feature branch dans main. En cas de divergence (R-6 passe, GitHub Actions échoue) : priorité GitHub Actions ; R-4 corrige et relance.

**U8 — Procédure de clôture de projet**  
*Problème* : Aucune procédure décrite pour clore un projet terminé (archivage Chroma, merge final, mise à jour projects.json).  
*Correction* : Checklist de clôture (exécutée manuellement par R-1/R-7 ou via nœud optionnel "project_close") :  
1. R-5 effectue le merge final de la branche develop dans main (`git merge --no-ff`).  
2. Exécuter `scripts/export_chroma.py --project-id <id> --output archives/<id>-<date>.json`.  
3. Mettre `"archived": true` dans `projects.json` (le projet est exclu des traitements actifs).  
4. Exécuter `scripts/purge_checkpoints.py --dry-run` pour vérifier les threads sans interrupt.  
5. Documenter la clôture dans le BaseStore (`project/{id}/status = "archived"`).  
Cette checklist est ajoutée à la documentation du projet (README ou Architecture.md).

#### B.6 Corrections Simulation 007 (V1–V7)

*Les éléments ci-dessous proviennent du rapport Simulation_007_2026-03-07.*

**V1 — Payload H5 : distinction reason**  
H5 est réutilisé pour deux cas : (a) escalade N2 (coût), (b) limite de rejections H1/H2/H3/H4 atteinte. Pour éviter la confusion, le payload `interrupt()` de H5 inclut obligatoirement un champ `reason` : `"cost_escalation"` (cas habituel d'escalade N2) ou `"max_rejections_H{n}"` (ex. `"max_rejections_H2"` après 3 H2-rejected), ou `"max_h4_rejections"`. Le script `handle_interrupt.py` affiche un message différent selon `reason`. Aucun nouveau type H7 requis.

**V2 — Nœud "load_context" en entrée de thread**  
Nœud "load_context" exécuté en premier à chaque démarrage de thread (avant E1 pour un nouveau projet, avant E3 pour un sprint suivant) :  
1. Lit `adr_counter` depuis BaseStore (`project/{id}/adr_counter`). Si absent : 0.  
2. Lit `sprint_number` depuis BaseStore (`project/{id}/sprint_counter`). Si absent : 1.  
3. Lit la dernière DoD depuis BaseStore (`project/{id}/dod/{sprint_number}`). Si absente : `None` (E2 déclenchera la création).  
4. Injecte les valeurs dans l'état initial du thread.  
Ce nœud garantit la continuité entre sessions et évite les collisions de compteurs.

**V3 — Re-déclenchement de E2 sur changement architectural**  
Le nœud sprint_complete (fin E6) positionne `state.needs_architecture_review = True` si le Sprint Backlog contient des tickets taggués `#architectural-change` ou si R-3 l'a signalé. Dans ce cas, la boucle sprint_complete redirige vers E2 au lieu de E3. H2 se re-déclenche (R-2 amende Architecture.md + DoD). Après H2 approuvé : retour à E3. Si aucun changement architectural : boucle directe E6→E3 (comportement par défaut).

**V4 — Stratégie de branches Git (modèle défini)**  
Modèle retenu : **feature branch par sprint** (pas par ticket). Topologie :  
- `main` : branche de production. R-5 ne merge dans main qu'après H4 approuvé + GitHub Actions vert (V5).  
- `develop` : branche d'intégration continue. R-5 crée `feature/{project_id}-sprint-{NN}` depuis `develop`.  
- R-4 génère les commits sur la feature branch. R-5 merge feature→develop après H4 approuvé.  
- GitHub Actions déclenché sur la PR develop→main.  
- H6 (conflit Git) s'applique aux merge feature→develop et develop→main.

**V5 — H4 toujours déclenché après CI vert dans E5**  
H4 est l'interrupt de *sortie* de E5. H5 est un interrupt *intra-E5* (bloquant temporaire pour escalade N2 ou max_rejections). Séquence garantie : E5 → [0 ou N interrupts H5] → CI vert → interrupt H4. Le nœud E5 vérifie CI vert avant de déclencher H4, quelle que soit l'historique H5. Si CI reste rouge après H5 et N2 : le nœud peut relancer Self-Healing ou escalader à nouveau.

**V6 — DoD versionnée par sprint dans BaseStore**  
Namespace BaseStore : `project/{id}/dod/{sprint_number}` (ex. `project/cli/dod/1`, `project/cli/dod/2`). À la fin de H2, le nœud post-H2 écrit la DoD finalisée sous `project/{id}/dod/{sprint_number}`. Le nœud load_context charge `project/{id}/dod/{sprint_number}` ; si absent (premier sprint), charge `project/{id}/dod/1` ou crée. En lecture, R-6 utilise la DoD de `state.dod` (chargée à l'init du thread). Les DoDs passées sont conservées pour audit.

**V7 — H4 rejected : cycle correctif sur même feature branch**  
H4 rejected → R-4 génère des commits correctifs sur la *même* feature branch (suffixe `fix-attempt-N`). Nouveau cycle E5 obligatoire (CI local R-6, puis GitHub Actions si feature branch pushée). H4 se redéclenche après nouveau CI vert. Limite : 3 cycles H4-rejected → H5 avec `reason="max_h4_rejections"`. La feature branch conserve l'historique complet (développement + corrections).

#### B.7 Corrections Simulation 008 (W1–W6)

*Les éléments ci-dessous proviennent du rapport Simulation_008_2026-03-08.*

**W1 — Entry point du graphe : start_phase**  
L'invocation du graphe accepte un paramètre de config `start_phase: "E1" | "E3"` (via `{"configurable": {"start_phase": "E3", ...}}`). Le nœud load_context route vers E1 (nouveau projet : création Backlog) ou vers E3 (nouveau sprint : Sprint Planning) selon ce paramètre. Commandes types :  
- Nouveau projet : `python run_graph.py --project-id cli --start-phase E1 --thread-id cli-phase-0`  
- Nouveau sprint : `python run_graph.py --project-id cli --start-phase E3 --thread-id cli-sprint-02`  
Valeur par défaut : `E1` (fail-safe pour les nouveaux projets).

**W2 — needs_architecture_review : champ Pydantic Sprint Backlog**  
Le schéma Pydantic `SprintBacklog` (sortie de R-3) inclut `architectural_change: bool` (défaut : false). R-3 positionne ce champ à true si les nouveaux tickets impliquent des changements de modules, de contrats d'API, ou de dépendances non prévus dans Architecture.md (détection via RAG + comparaison). sprint_complete lit `state.sprint_backlog.architectural_change` et positionne `state.needs_architecture_review` en conséquence.

**W3 — DoD manquante avant re-E2 : fallback version précédente**  
load_context : si `project/{id}/dod/{sprint_number}` absent dans BaseStore → charger `project/{id}/dod/{sprint_number - 1}`. Si sprint_number=1 et aucune DoD disponible : `state.dod = None` (normal : E2 créera la DoD). Règle : `state.dod` n'est jamais `None` dès que sprint_number > 1, sauf si le BaseStore est corrompu ou vide (alerte dans les logs).

**W4 — H4 conditionné à CI local ET GitHub Actions**  
Nouveau flux E5→H4 : R-5 pousse la feature branch vers le remote *avant* que H4 soit déclenché. GitHub Actions tourne sur la PR feature→develop. Si GitHub Actions passe : H4 est déclenché (Sprint Review R-7). Si GitHub Actions échoue : retour Self-Healing (R-4 corrige, nouveau cycle E5). H4 n'est jamais déclenché si GitHub Actions est rouge. Cette approche élimine le cas "H4-approved puis merge impossible". Voir III.13 (V4).

**W5 — Workflow hotfix**  
Branche `hotfix/{project_id}-{date}-{description}` créée depuis `main` par R-5. Invocation graphe : `--start-phase HOTFIX --thread-id {project_id}-hotfix-{date}` (voir III.16 Y4 pour le Sprint Backlog synthétique). R-4 applique le correctif. R-6 lance E5 (CI local + GitHub Actions sur PR hotfix→main). R-5 merge hotfix→main + hotfix→develop après H4. Aucun Sprint Review : le merge hotfix→main est la validation. Documenter dans Architecture.md (ADR de hotfix).

**W6 — Variable AGILE_PROJECTS_JSON**  
Variable d'environnement `AGILE_PROJECTS_JSON` (défaut : `$AGILE_ORCHESTRATION_ROOT/config/projects.json`). Définie dans `.agile-env` ou en variable système. `setup_project_hooks.sh` génère la valeur par défaut. Les nœuds load_context, sprint_complete, et handle_interrupt.py lisent projects.json via cette variable. Si la variable est absente et le chemin par défaut inexistant : erreur explicite avec message d'aide.

#### B.8 Corrections Simulation 009 (X1–X4)

*Les éléments ci-dessous proviennent du rapport Simulation_009_2026-03-09.*

**X1 — Deux PR GitHub Actions distinctes (CI 1 et CI 2)**  
Clarification de la stratégie CI :  
- **CI 1** (pré-H4, obligatoire) : GitHub Actions déclenché sur PR `feature/{project_id}-sprint-{NN} → develop`. Condition nécessaire au déclenchement de H4. Valide l'intégration du sprint dans develop.  
- **CI 2** (post-E6, obligatoire avant merge main) : GitHub Actions déclenché sur PR `develop → main`. R-5 ouvre cette PR après sprint_complete (post-H4). Merge develop→main conditionné à CI 2 vert. Effectué par R-5 (nœud "merge_to_main" post-sprint_complete, ou action manuelle).  
Les deux CI partagent la même configuration GitHub Actions mais s'exécutent sur des PRs différentes.

**X2 — Push R-5 en fin de E4 (timing unique)**  
R-5 effectue un push unique à la fin de E4, après le dernier commit de ticket. Ce push ouvre la PR feature→develop sur GitHub. GitHub Actions CI 1 démarre. R-6 (CI local) démarre en parallèle dans le même nœud E5. Pas de push intermédiaire pendant E4 (évite les triggers répétés de GitHub Actions et les conflits AGILE_DEFER_INDEX).

**X3 — Polling GitHub Actions par R-6 (gh run watch)**  
R-6 (nœud E5) attend le résultat de CI 1 via `run_shell("gh run watch --repo {repo} --exit-status --interval 30")`. Variable `GITHUB_ACTIONS_TIMEOUT=600` secondes (défaut 10 min). Si le run CI 1 n'est pas terminé dans ce délai : interrupt H5 avec `reason="github_actions_timeout"` (L'opérateur peut étendre ou relancer le CI). `gh run watch` nécessite GitHub CLI (`gh`) installé et authentifié. Ajouter `gh` à la checklist d'installation. `repo` = valeur `projects[project_id].github_repo` dans projects.json (nouveau champ optionnel).

**X4 — AGILE_BASESTORE_STRICT : résilience load_context**  
Variable `AGILE_BASESTORE_STRICT=false` (défaut) : si BaseStore inaccessible, load_context utilise les valeurs par défaut (adr_counter=0, sprint_number=1, dod=None) et log WARNING. Si `AGILE_BASESTORE_STRICT=true` : load_context lève une exception explicite avec message d'aide (vérifier la connexion BaseStore). Recommandé en production : `AGILE_BASESTORE_STRICT=true`.

#### B.9 Corrections Simulation 010 (Y1–Y5)

*Les éléments ci-dessous proviennent du rapport Simulation_010_2026-03-10.*

**Y1 — Création de la branche develop**  
`setup_project_hooks.sh` crée la branche `develop` depuis `main` si elle n'existe pas : `git checkout -b develop main && git push -u origin develop`. Ajouté à la checklist d'installation (étape "init_branches"). Si `develop` existe déjà : skip silencieux.

**Y2 — gh pr create et gh pr checks**  
Après le push de la feature branch en fin de E4 (X2), R-5 exécute `gh pr create --base develop --head feature/{project_id}-sprint-{NN} --title "Sprint {NN}" --body "Sprint automatisé"`. Le workflow GitHub Actions doit être déclenché sur `pull_request` (et non seulement `push`). R-6 surveille CI 1 via `gh pr checks {pr_number} --required --watch --interval 30`. Ajouter à la checklist : `gh auth login` (une seule fois, jeton persisté dans `~/.config/gh`).

**Y3 — Nœud merge_to_main dans sprint_complete**  
sprint_complete, après écriture BaseStore sprint_summary, exécute le nœud R-5 "merge_to_main" : (1) `gh pr create --base main --head develop --title "Release sprint {NN}"`. (2) `gh pr checks {pr_number} --required --watch --interval 30` (CI 2). (3) Si CI 2 vert : `gh pr merge --merge --delete-branch=false` (merge develop→main). (4) Si CI 2 rouge : interrupt H5 avec `reason="ci2_github_actions_failure"`. R-4 corrige sur feature branch, nouveau cycle E5/CI 1, puis re-push develop, CI 2 se relance.

**Y4 — start_phase HOTFIX**  
Nouveau `start_phase: "HOTFIX"`. Invocation : `python run_graph.py --project-id webhook --start-phase HOTFIX --thread-id webhook-hotfix-2026-03-10 --hotfix-description "Fix NPE in X"`. load_context crée un Sprint Backlog synthétique : `SprintBacklog(tickets=[Ticket(id="HF-001", description=hotfix_description)], architectural_change=False)`. Le reste du flux E4→E5→H4 s'applique normalement. Merge : (1) CI 1 et H4 valident hotfix→main. (2) R-5 merge hotfix→develop directement (`git checkout develop && git merge --no-ff hotfix/... && git push`) sans PR ni CI supplémentaire — le code a déjà été validé sur main. Voir III.19 (BB3).

**Y5 — Mode dégradé si github_repo absent**  
Si `projects[project_id].github_repo` est absent ou vide : le nœud E5 ne lance pas `gh pr create` ni `gh pr checks`. CI 1 est skippé. Log WARNING : `"[E5] github_repo non configuré pour {project_id} — CI GitHub Actions skippé. H4 déclenché sur CI local seul."` H4 déclenché uniquement sur CI local (R-6) vert. Merge develop→main : action manuelle (pas de nœud merge_to_main). Documenter dans le README du projet.

#### B.10 Corrections Simulation 011 (Z1–Z2)

*Les éléments ci-dessous proviennent du rapport Simulation_011_2026-03-11.*

**Z1 — sprint_complete : incrément sprint_number après CI 2 seulement**  
sprint_complete est restructuré en deux phases atomiques :  
1. **Phase sprint_summary** : écriture du sprint_summary dans BaseStore (`project/{id}/sprints/sprint-{NN}`), déclenchement index_rag (ou traitement pending_index.log si AGILE_DEFER_INDEX). `sprint_number` reste à N.  
2. **Phase merge_to_main** : exécution du nœud R-5 merge_to_main (gh pr create develop→main, gh pr checks CI 2, gh pr merge). **Seulement si CI 2 vert** : incrémenter `state.sprint_number` → N+1 et écrire dans BaseStore (`project/{id}/sprint_counter`). Si CI 2 rouge → H5 `reason="ci2_github_actions_failure"` sans modification de sprint_number. La correction s'applique sur develop (commits sur feature branch → merge feature→develop) ; une fois CI 2 vert → incrément.

**Z2 — Branch protection et merge automatique**  
Documentation dans le README du projet orchestration :  
- **Cas sans branch protection** (recommandé pour usage solo) : `gh pr merge` s'exécute automatiquement après CI 2 vert.  
- **Cas avec branch protection sur develop** : ne pas activer de required reviewer sur `develop`. Seule la vérification CI (status checks) est requise. `gh pr merge` passe si CI vert.  
- **Cas avec branch protection stricte sur main** (requis reviewer) : le nœud merge_to_main ouvre la PR develop→main et attend. Interrupt H5 (`reason="pr_review_required"`) : l'opérateur approuve manuellement la PR sur GitHub, puis `Command(resume="merged")`. R-5 ne merge pas automatiquement.  
Recommandation : activer uniquement la vérification CI sur `develop` ; garder la décision de merge main aux humains si souhaité (configurable).

#### B.11 Corrections Simulation 012 (AA1–AA2)

*Les éléments ci-dessous proviennent du rapport Simulation_012_2026-03-12. Ce sont les dernières corrections avant convergence.*

**AA1 — sprint_number incrément en mode dégradé**  
Règle de clôture du sprint_number (deux cas mutuellement exclusifs) :  
- Si `projects[project_id].github_repo` est présent et non vide : incrément sprint_number dans la **phase 2** (merge_to_main), après CI 2 vert.  
- Si `github_repo` est absent ou vide (mode dégradé) : incrément sprint_number dans la **phase 1** (sprint_summary), immédiatement après écriture BaseStore sprint_summary.  
Le nœud sprint_complete vérifie `github_repo` en début d'exécution pour choisir la règle d'incrément.

**AA2 — Suppression de la notation H4' : H5 avec reason**  
La notation "H4'" introduite en III.17 est supprimée. Le cas "PR develop→main requiert un reviewer humain" est géré par H5 avec `reason="pr_review_required"`. Conformément à la convention V1 (III.13), H5 est le seul interrupt d'escalade humaine, distingué par son champ `reason` :  
- `"cost_escalation"` : escalade N2 (coût)  
- `"max_rejections_H{n}"` : limite de cycles rejected atteinte  
- `"max_h4_rejections"` : limite H4-rejected atteinte  
- `"github_actions_timeout"` : timeout polling CI 1 ou CI 2  
- `"ci2_github_actions_failure"` : CI 2 rouge après merge_to_main  
- `"pr_review_required"` : branch protection stricte sur main, merge nécessite approbation humaine  

#### B.12 Corrections Simulation 013 (BB1–BB4)

*Les éléments ci-dessous proviennent du rapport Simulation_013_2026-03-13 — simulation finale 3 mois.*

**BB1 — Checklist 4.1 : numérotation corrigée**  
Deux étapes étaient numérotées "11". Correction : 10=GitHub CLI, 11=Docker, 12=Vercel/Railway.

**BB2 — W5 (hotfix) : start_phase E4 obsolète remplacé par HOTFIX**  
La section W5 (III.14) utilisait `--start-phase E4` introduit avant que Y4 (III.16) ne crée `start_phase HOTFIX`. W5 est mis à jour pour utiliser `--start-phase HOTFIX` (conforme à Y4 qui crée le SprintBacklog synthétique HF-001). Plus d'ambiguïté sur l'entry point hotfix.

**BB3 — Hotfix merge develop→ : direct sans PR**  
Le merge hotfix→develop est un merge direct (`git merge --no-ff`) sans PR ni CI supplémentaire : le code a déjà été validé par CI 1 (PR hotfix→main) et H4 (Sprint Review). Évite une double validation inutile sur develop pour un correctif d'urgence. Documenter dans Architecture.md (ADR de hotfix si besoin).

**BB4 — auto_next_sprint : boucle E3 après phase 2 (ou phase 1 en dégradé)**  
Si `auto_next_sprint=true`, la boucle vers E3 (sprint N+1) se déclenche :  
- Après **phase 2** (merge_to_main vert, sprint_number incrémenté) si `github_repo` présent.  
- Après **phase 1** (sprint_summary, incrément immédiat) si mode dégradé (github_repo absent).  
Cela garantit que E3 du sprint N+1 démarre avec un sprint_number et un develop à jour.

---

IX. Layout Architectural Senior

*Note : E4 piloté par LangGraph (nœuds R-4, R-5 + tools), cf. Simulation 001.*



Extrait de code




graph TD
classDef humain fill:#e1f5fe,stroke:#039be5,stroke-width:2px,color:#000
classDef aiFree fill:#e8f5e9,stroke:#2e7d32,stroke-width:2px,color:#000
classDef aiPaid fill:#fff3e0,stroke:#e65100,stroke-width:2px,color:#000
classDef localNode fill:#eceff1,stroke:#607d8b,stroke-width:2px,color:#000
classDef artifact fill:#ffffff,stroke:#9e9e9e,stroke-width:2px,color:#000,stroke-dasharray: 5 5

%% --- PHASE 0: MATURATION (GRATUITE) ---
%% Titre raccourci, et textes des bulles rallongés pour étirer la boîte et protéger le titre
subgraph PHASE\_0 \[ 🛠️ PHASE 0 : DISCOVERY HORS AGILE \]
direction LR
R1\_Init(("R-1: Product Owner<br/>Nghia (PM)<br/>(Porteur de la vision initiale)")):::humain
R0\["R-0: Business Analyst<br/>Cascade: gemma3:12b -> Gemini -> Opus 4.6"\]:::aiFree
R1\_Init <-->|Iterations illimitees| R0
end

%% --- LE POINT DE BASCULE ---
subgraph BASCULE \[FRONTIERE DE FACTURATION ET ENTREE EN AGILE\]
GrosTicket\[/"Gros Ticket Initial Mature<br/>(Livrable fondateur hors cycle)"/\]:::artifact
R0 -.->|Cristallise| GrosTicket
end

%% --- L'USINE AGILE (API PAYANTES & OUTILS LOCAUX) ---
subgraph USINE \[ ⚙️ USINE AGILE ITERATIVE ET STRUCTUREE \]
direction TB

%% COUCHE STRATÉGIQUE
subgraph ENV\_C \[ENV-C : EXPERTISE INTELLIGENCE EN CASCADE\]
R2\["R-2: System Architect<br/>Cascade: gemma3:12b -> AI Studio -> Opus 4.6"\]:::aiPaid
R4\["R-4: Dev Team<br/>Cascade: qwen2.5-coder:7b -> AI Studio -> Sonnet 4.6"\]:::aiPaid
end

%% COUCHE PILOTAGE
subgraph ENV\_B \[ENV-B : HUB VS CODE HYBRIDE\]
direction LR
R1\_Agile(("R-1: Product Owner<br/>Nghia (PM)<br/>(Gratuit / Open-Source)")):::humain
Backlog\[/"Besoins - Product Backlog.md<br/>(Vivant et Iteratif)"/\]:::artifact
ArchDoc\[/"Architecture.md<br/>(Specifications)"/\]:::artifact
DoD\[/"Definition of Done (DoD)<br/>(Contrat d'acceptation)"/\]:::artifact
R7(("R-7: Stakeholder<br/>Nghia (Dir)<br/>(Gratuit / Open-Source)")):::humain
end

%% COUCHE EXÉCUTION
subgraph ENV\_D \[ENV-D : FACTORY LOCALE GRATUITE\]
direction TB
R3\["R-3: Scrum Master<br/>Cascade: qwen2.5-coder:7b -> AI Studio -> Sonnet"\]:::localNode
SprintBacklog\[/"Sprint Backlog<br/>(Tickets Atomiques)"/\]:::artifact
R5\[("R-5: Release Manager<br/>Git + Cascade qwen2.5-coder/Sonnet")\]:::localNode
R6{"R-6: QA et DevOps<br/>Docker, Jest + Cascade qwen2.5-coder/Sonnet"}:::localNode
end
end

%% --- LIAISONS LOGIQUES DU CYCLE AGILE ---
GrosTicket -->|E1: Initialise l'Usine| Backlog

%% Activité de R-1 dans le Hub
R1\_Agile <-->|Gere et Priorise| Backlog
R1\_Agile -.->|Co-construit| DoD
R2 -.->|Co-construit| DoD
R7 -.->|Valide| DoD

Backlog -->|Input pour Refinement| R2
R2 -->|E2: Construit| ArchDoc

ArchDoc -->|E3: Validation| R7

%% R-3 est mis en évidence ici
Backlog & ArchDoc -->|Fournit le contexte| R3
R3 -->|Genere| SprintBacklog

SprintBacklog -->|E4: Assigne Ticket| R4
R4 -->|E4: Code via API| R5
R5 -->|E5: Trigger CI-CD| R6

%% La DoD devient la grille de lecture de la QA
DoD -->|Criteres de validation| R6

R6 -- "REJECT: Self-Healing" --> R4
R6 ==>|E6: Valide et Deploie| R7

%% Rétrofit cible directement le Backlog vivant
R7 -.->|Retrofit - Mise a jour iterative| Backlog

%% =========================================================
%% CONTRAINTES INVISIBLES POUR ÉCRASER LA HAUTEUR DE L'USINE
%% =========================================================
%% Ces liens n'affichent rien, ils forcent R-1 et R-7 à se
%% rapprocher du centre, raccourcissant drastiquement les flèches.
R1\_Agile ~~~ ArchDoc
R7 ~~~ ArchDoc
GrosTicket ~~~ Backlog