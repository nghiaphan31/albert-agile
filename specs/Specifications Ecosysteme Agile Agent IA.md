##

* * *

📑 Manifeste de l'Écosystème Agile en Autarcie

*Référence : [NOMENCLATURE_R_H_E.md](NOMENCLATURE_R_H_E.md) — Rôles (R-x), Interrupts (H-x), Phases (E-x).*

*Contexte : Linux, GPU NVIDIA (VRAM ≥ 16 Go recommandé, ex. RTX 5060 Ti 16G), Google AI Studio (free-tier), Anthropic (Opus 4.6 / Sonnet 4.6). Priorité : coûts et qualité. Legacy 12 Go (RTX 3060) : voir Simulation 014 + `docs/HARDWARE_GPU.md`.*

**Nomenclature 4D** (actions humaines en environnement distribué) : Toute action humaine est préfixée par le format : SOURCE > APP > VUE → CIBLE. Ex. : PC > Cursor > Terminal → Calypso signifie que vous tapez sur votre PC, la commande s'exécute sur Calypso. SOURCE = machine où vous tapez (ex. PC). APP = logiciel (Cursor, Navigateur Web). VUE = zone d'écran (Terminal, Éditeur, Chat). CIBLE = machine où la commande s'exécute (Calypso, Cloud). Règle : aucune ambiguïté tolérée.

**VUE Terminal** : *Terminal* dans la VUE désigne par défaut le **terminal intégré à l'IDE** (VS Code ou Cursor : panneau Terminal). Pour un terminal **externe** (hors IDE), préciser explicitement : *Terminal externe* ou *SSH hors IDE*.

| Section | Contenu |
|---------|---------|
| I | Matrice Modèles IA (local/cloud) par rôle — cohérence technique |
| II | Rôles, artefacts et régimes financiers |
| III | Outils, frameworks, modèles exacts à installer (dont LangGraph, Pydantic) |
| III.5–III.8 | LangChain/LangGraph ; Modèle de codage ; Human-in-the-Loop ; Mémoire/RAG (recherche sémantique) (III.7-bis : temps réel, partage IDE ; III.7-ter : SearXNG ; III.7-quater : nomenclature Sécurité & Extensions Presidio/SearXNG) ; Procédures Opérationnelles Consolidées |
| IV | Comptes Cloud gratuits + checklist d'installation |
| V | Flux détaillés et livrables (Phase 0 + Usine Agile) |
| VI | Stratégies d'optimisation des coûts |
| VII | Exigences transversales (testabilité, traçabilité, modularité) |
| VIII | Rapports de simulation (références, corrections intégrées) |
| IX | Layout architectural (Mermaid) |
| Annexe A | Cartographie financière (synthèse par coût) |
| Annexe B | Historique des corrections par simulation (001–014) |

---

### I. Matrice Modèles IA par Rôle et par Flux (Cohérence Technique)

**Règle de cascade unique** : Pour chaque rôle, l'IA est sollicitée dans l'ordre suivant. On n'escalade au niveau supérieur que si le niveau inférieur échoue (qualité insuffisante) ou renvoie HTTP 429.

| Niveau | Technologie | Modèle exact | Usage typique | Coût |
|--------|-------------|--------------|---------------|------|
| **N0 (local Ollama) – Local** | Ollama sur GPU NVIDIA (profil VRAM — voir `docs/HARDWARE_GPU.md`) | `qwen2.5-coder:14b` (code) ou `qwen2.5:14b` (idéation) ; *legacy 12 Go* : qwen2.5-coder:7b/3b, gemma3:12b (voir Simulation 014) | Tâches courantes, ~80% des cas | 0 € |
| **N1 (cloud gratuit) – Cloud gratuit** | Google AI Studio API | `gemini-2.5-flash` ou `gemini-2.5-flash-lite` | Fallback après N0 (local Ollama) | 0 € |
| **N2 (cloud payant) – Cloud payant** | Anthropic API | `claude-sonnet-4-6` (exécution) / `claude-opus-4-6` (architecture) | Dernier recours, décisions critiques | Pay-as-you-go |

**Mapping rôle → modèles par défaut** :

| Rôle | Modèle local (N0 (local Ollama)) | Modèle cloud gratuit (N1 (cloud gratuit)) | Modèle cloud payant (N2 (cloud payant)) |
|------|-------------------|---------------------------|---------------------------|
| R-0 (Business Analyst IA) | qwen2.5:14b | gemini-2.5-flash | claude-opus-4-6 |
| R-2 (System Architect IA) | qwen2.5:14b | gemini-2.5-flash | claude-opus-4-6 |
| R-3 (Scrum Master IA), R-4 (Dev Team IA), R-5 (Release Manager IA), R-6 (QA & DevOps IA) | qwen2.5-coder:14b | gemini-2.5-flash | claude-sonnet-4-6 |

*R-1 (Product Owner) et R-7 (Stakeholder) : rôles de supervision, pilotent via VS Code + Continue.dev.*

---

### II. Répertoire Détaillé des Rôles, Artefacts et Régimes Financiers

| ID | Rôle Agile & Mission | Entité | Technologie & Régime | Artefact (Livrable) |
| --- | --- | --- | --- | --- |
| R-0 (Business Analyst IA) | **Business Analyst IA** — Guide la phase d'idéation, challenge les hypothèses métier et aide à définir la proposition de valeur avant tout investissement technique. | Sparring Partner | Cascade : Ollama (qwen2.5:14b) → AI Studio (Gemini 2.5 Flash) → Opus 4.6 | Notes de Discovery, Epic initial mature |
| R-1 (Product Owner) | **Product Owner** — Garant de la vision produit. Priorise la valeur métier, gère le backlog interactif via Continue.dev ou Roo Code (RAG (recherche sémantique) sur la codebase ; option : chroma-mcp pour RAG (recherche sémantique) partagé avec agents) et s'assure de l'alignement. | Superviseur produit | VS Code + Continue.dev + Roo Code. Régime : Local / Gratuit | Besoins - Product Backlog.md, Co-rédacteur de la DoD (Definition of Done) |
| R-2 (System Architect IA) | **System Architect IA** — Garant de la viabilité technique. Traduit les besoins métier en choix architecturaux, structures de données et contrats d'API. | L'Architecte | Cascade : Ollama (qwen2.5:14b) → AI Studio → Opus 4.6 | Architecture.md, Co-rédacteur de la DoD (Definition of Done) |
| R-3 (Scrum Master IA) | **Scrum Master IA** — Facilitateur et orchestrateur. Lève les obstacles, gère le découpage technique pour respecter la vélocité et anonymise les contextes. | Chef de Projet | Cascade : Ollama (qwen2.5-coder:14b) → AI Studio → Sonnet 4.6 | Sprint Backlog (tickets atomiques et ciblés) |
| R-4 (Dev Team IA) | **Dev Team IA** — Force de production exécutive incarnée par Roo Code. Écrit le code source fonctionnel et garantit la non-régression via TDD. | Le Développeur | Cascade : Ollama (qwen2.5-coder:14b) → AI Studio → Sonnet 4.6 | Source Code, Unit Tests (TDD) |
| R-5 (Release Manager IA) | **Release Manager IA** — Garant du versioning et de la stratégie de branching. Gère les conflits de fusion et isole les développements. | L'Archiviste | Git / MCP (Model Context Protocol) + Cascade : Ollama (qwen2.5-coder:14b) → AI Studio → Sonnet 4.6 | Feature Branches, Historique des Commits |
| R-6 (QA & DevOps IA) | **QA & DevOps IA** — Garant de l'intégration continue. Exécute les tests, analyse les logs d'erreurs et déclenche la boucle de correction. | L'Inspecteur | Docker, Jest + Cascade : Ollama (qwen2.5-coder:14b) → AI Studio → Sonnet 4.6 | Test Reports & Logs (application stricte de la DoD (Definition of Done)) |
| R-7 (Stakeholder) | **Stakeholder** — Sponsor du projet. Évalue le ROI de l'incrément, supervise les tests finaux dans VS Code et valide l'alignement stratégique. | Superviseur stratégique | VS Code + Continue.dev + Roo Code. Régime : Local / Gratuit | Go/No-Go Decision, Valideur final de la DoD (Definition of Done) |

###

* * *

III. Outils, Frameworks et Modèles IA — Spécifications Techniques Détaillées

#### 3.1 Matériel et Moteurs Locaux

| Composant | Spécification | Rôle |
|-----------|---------------|------|
| GPU | GPU NVIDIA (VRAM ≥ 16 Go recommandé) | Exécution des modèles Ollama (Q4 quantization) |
| Moteur LLM | **Ollama** (https://ollama.com) | Runtime pour modèles locaux, API compatible OpenAI |

#### 3.2 Modèles Ollama à Installer (Téléchargement Unique)

| Modèle | Commande d'installation | VRAM | Usage principal |
|--------|-------------------------|------|-----------------|
| **qwen2.5-coder:14b** | `ollama pull qwen2.5-coder:14b` | ~9–10 Go | R-3 (Scrum Master IA), R-4 (Dev Team IA), R-5 (Release Manager IA), R-6 (QA & DevOps IA) : code, tests, découpage, merge |
| **qwen2.5:14b** | `ollama pull qwen2.5:14b` | ~9 Go | R-0 (Business Analyst IA), R-2 (System Architect IA) : idéation, architecture, réflexion stratégique |
| **nomic-embed-text** | `ollama pull nomic-embed-text` | ~0,5 Go | Embeddings RAG (recherche sémantique) |

*Contexte : 128K tokens (Qwen). Licence : Apache 2.0. Profil VRAM 16 Go (RTX 5060 Ti). Option thinking Tier 1 : `qwen3:14b` — voir `specs/plans/Strategie_Modeles_LLM_Thinking_Albert_Agile.md`. Alternatives : `deepseek-coder-v2:16b` (Tier2), `qwen2.5:14b-instruct-q4_K_M` (Tier1). Legacy 12 Go : voir `docs/HARDWARE_GPU.md` + Simulation 014.*

#### 3.3 Interface et Orchestration

| Outil | Version / Référence | Usage |
|-------|--------------------|-------|
| **VS Code** | Dernière stable | IDE central |
| **Continue.dev** | Extension open-source | Autocomplétion, RAG (recherche sémantique) codebase, pilotage des modèles (Ollama, Gemini, Anthropic). Modes : **manuel** (choix explicite) ou **routage automatique** (via proxy, ex. LiteLLM). Voir III.3-bis. |
| **Roo Code** | Extension / agent | Exécution autonome des tâches (sprints, CI). Modes : manuel ou routage automatique (comme Continue). |
| **LangGraph + LangChain** | Dernière stable (LangGraph 1.x) | Orchestration du graphe d'agents, routage cascade, human-in-the-loop. Voir section III.5. |

#### 3.3-bis Sélection des modèles IDE : modes manuel et routage automatique

L'IDE (VS Code + Continue.dev / Roo Code) supporte deux modes de sélection des modèles, à l'instar de Cursor Pro (Smart / manuel) :

| Mode | Comportement | Usage typique |
|------|--------------|---------------|
| **Manuel** | L'utilisateur sélectionne explicitement le modèle à chaque requête (Ollama, Gemini, Anthropic). | Contrôle total, débogage, maîtrise des coûts. |
| **Routage automatique** | Un proxy (ex. LiteLLM) route les requêtes selon la tâche (code → coder, idéation → idéation/thinking) et applique une cascade en cas d'échec : local (Ollama) → Gemini (gratuit) → Claude. | Expérience "smart" alignée sur le graphe LangGraph. |

**Référence** : Voir `specs/plans/Plan_Configuration_VSCode_Ollama_Local.md` pour la configuration détaillée (modes, LiteLLM, modèles Ollama/Gemini/Anthropic). Pour le parcours runtime, les critères de maturité et la bascule Bootstrap → Runtime : voir [Modes_Bootstrap_et_Runtime_Cible.md](plans/Modes_Bootstrap_et_Runtime_Cible.md).

#### 3.4 Chaîne de Qualité, RAG (recherche sémantique) et CI/CD

| Outil | Usage |
|-------|-------|
| **Git** | Versioning, branches, historique |
| **MCP (Model Context Protocol)** | Contexte structuré de la codebase pour les agents ; chroma-mcp pour partage RAG (recherche sémantique) agents + IDE (III.7-bis) |
| **Chroma** | Base vectorielle pour RAG (recherche sémantique) agents (codebase, docs projet). Voir III.7. |
| **nomic-embed-text** (Ollama) | Modèle d'embeddings local pour Chroma. `ollama pull nomic-embed-text`. |
| **SearXNG** | Métamoteur de recherche web auto-hébergé (Docker). Accès web temps réel pour agents (Worker, Architect) — contourne knowledge cutoff et contenu statique RAG. 100 % gratuit, anonymisation des requêtes. Voir III.7-ter. |
| **Microsoft Presidio** | Moteur NLP open-source pour anonymisation/désanonymisation des prompts (PII, secrets, IP). Intégration possible via LiteLLM (proxy bidirectionnel : masking sortant, unmasking entrant). Voir III.5-ter et specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md §10. |
| **Docker** | Isolation, tests reproductibles |
| **Jest** (JS/TS) / **Pytest** (Python) | Tests unitaires et intégration |
| **ESLint** / **Ruff** | Linting |
| **GitHub Actions** | CI/CD (dépôts publics : gratuit) |

#### 3.5 Écosystème LangChain/LangGraph — Orchestration Multi-Agents et Human-in-the-Loop

**Justification** : Les rôles R-0 (Business Analyst IA) à R-6 (QA & DevOps IA) sont des agents IA qui doivent collaborer selon un graphe de décision (cascade, routage, boucles). LangGraph (1.0 GA, octobre 2025) est le framework de référence pour orchestrer des agents multiples avec état partagé, cycles et human-in-the-loop. LangChain fournit les connecteurs LLM (Ollama, Anthropic, Google). Pydantic garantit des sorties structurées et validées. Cet écosystème permet d'automatiser le flux Agile tout en conservant des points de validation humaine aux moments critiques.

| Composant | Rôle | Justification |
|-----------|------|---------------|
| **LangGraph** | Orchestration du graphe d'agents. Chaque rôle (R-0 (Business Analyst IA) à R-6 (QA & DevOps IA)) = nœud. Arêtes = flux (E1 (idéation, Epic)→E2 (architecture, DoD (Definition of Done))→…). Routage cascade N0 (local Ollama)→N1 (cloud gratuit)→N2 (cloud payant) par branche conditionnelle. | Modèle en graphe (vs chaîne linéaire) : cycles (Self-Healing R-6 (QA & DevOps IA)→R-4 (Dev Team IA)), bifurcations, état partagé (TypedDict). `interrupt()` natif pour Human-in-the-Loop. Utilisé en prod par LinkedIn, Uber, Klarna. AgentExecutor LangChain déprécié en faveur de LangGraph. |
| **LangChain** | Connecteurs LLM (Ollama, Google AI Studio, Anthropic), gestion des retries/backoff, templates de prompts. | Dépendance de LangGraph. Abstraction unifiée : `ChatOllama`, `ChatAnthropic`, `ChatGoogleGenerativeAI`. Compatible Ollama via `langchain-ollama`. |
| **Pydantic** | Validation des sorties IA : schémas pour Epic, Sprint Backlog, Architecture.md, tickets. | Évite les outputs invalides (JSON malformé, champs manquants). Intégré à LangChain (`with_structured_output`). Typage strict = moins d'erreurs en production. |
| **LangSmith** | Traçage, débogage, monitoring des runs. Intégration native avec LangChain/LangGraph. | Free tier : 5000 traces/mois. Indispensable pour débugger des workflows multi-agents (quel agent a échoué, pourquoi, tokens consommés). Rétention 14 jours suffisante pour itérations. |
| **LangServe** | Exposition du graphe LangGraph en API REST (FastAPI). Endpoints `/invoke`, `/stream`, `/playground`. | Permet de déclencher les phases (E1 (idéation, Epic)–E6 (clôture sprint, merge)) depuis un script, un cron ou GitHub Actions. Déploiement local (pas de coût). Alternative : exécution directe en CLI Python. |

**Architecture d'intégration** : Un service Python héberge le graphe LangGraph. Les nœuds appellent Ollama (N0 (local Ollama)), Google API (N1 (cloud gratuit)) ou Anthropic (N2 (cloud payant)) selon la logique de cascade. Pydantic modélise l'état (Backlog, Architecture, SprintBacklog) et les sorties de chaque agent. LangSmith trace chaque exécution. Les rôles de supervision (R-1 (Product Owner), R-7 (Stakeholder)) interviennent via `interrupt()` aux points définis ci-dessous.

**Gestion des exceptions Ollama comme "échec N0 (local Ollama)" (F8 (cascade échec N0))** : Toute exception levée lors d'un appel à `ChatOllama` — quelle que soit sa nature (`ConnectionError`, `TimeoutError`, `OllamaRuntimeError`, VRAM épuisée / OOM GPU, modèle non chargé) — doit être capturée dans un bloc `try/except Exception` autour de l'appel N0 (local Ollama) et traitée comme un **échec N0 (local Ollama)**, déclenchant immédiatement l'escalade vers N1 (cloud gratuit) (Google AI Studio). L'exception **ne doit jamais remonter** comme erreur fatale du graphe LangGraph. Implémenter dans une fonction utilitaire `call_with_cascade(llm_n0, llm_n1, llm_n2, prompt, schema)` appelée par tous les nœuds, qui encapsule la logique try/except + escalade + retry HTTP 429. Log structuré à chaque escalade : `{"level": "WARNING", "event": "n0_failure", "reason": str(e), "escalating_to": "N1"}`. Sur VRAM limitée (legacy 12 Go), les OOM GPU sont le cas d'échec N0 (local Ollama) le plus probable en début de session (modèle pas encore chargé ou VRAM fragmentée).

**Pydantic vs Pydantic AI** : Pydantic (bibliothèque de validation) est utilisée. Pydantic AI est un framework d'agents concurrent de LangChain ; pour éviter la fragmentation et profiter de l'écosystème LangGraph (Human-in-the-Loop mature, communauté large), on retient LangGraph + Pydantic (validation).

#### 3.5bis Modèle de codage (paradigme d'implémentation)

*Cette section synthétise le paradigme de codage des flux de travail. Elle sert de référence pour l'implémentation.*

| Concept | Implémentation |
|---------|----------------|
| **Rôles (R-0 (Business Analyst IA) à R-6 (QA & DevOps IA))** | Nœuds du graphe — une fonction Python par rôle, qui reçoit l'état et retourne une mise à jour. |
| **Phases (E1 (idéation, Epic)→E2 (architecture, DoD (Definition of Done))→…)** | Arêtes entre nœuds (transitions définies dans le graphe). |
| **État partagé** | `TypedDict` : Backlog, Architecture, SprintBacklog, DoD (Definition of Done), messages, **project_root** (Path), **project_id** (str), **sprint_number** (int, défaut 1), **adr_counter** (int, défaut 0), **needs_architecture_review** (bool, défaut false). Initialisés par le nœud "load_context" (III.8-A) en entrée de chaque thread. Invocation : `start_phase "E1 (idéation, Epic)" | "E3 (Sprint Backlog)" | "HOTFIX (correctif urgent)"` via config (III.8-A). |
| **Appels LLM** | Cascade N0 (local Ollama)→N1 (cloud gratuit)→N2 (cloud payant) : essai Ollama (N0 (local Ollama)), puis Google AI Studio (N1 (cloud gratuit)), puis Anthropic (N2 (cloud payant)) en dernier recours. Logique de routage conditionnelle selon succès/échec/HTTP 429. |
| **Sorties structurées** | `with_structured_output` (LangChain) + schémas Pydantic sur chaque LLM. Garantit des sorties valides (Epic, tickets, Architecture, etc.). |
| **Self-Healing (R-6 (QA & DevOps IA)→R-4 (Dev Team IA))** | Cycle dans le graphe : arête conditionnelle R-6 (QA & DevOps IA)→R-4 (Dev Team IA) si tests en échec. Seuil strict : 3 itérations max, puis interrupt H5 (approbation escalade API payante). |
| **Human-in-the-Loop** | `interrupt()` dans les nœuds aux points H1 (validation Epic)–H6 (résolution conflit Git). Le graphe suspend, le checkpointer sauvegarde. Reprise via `Command(resume=...)`. |
| **Tools (E4 (exécution code, sprint), E5 (tests, CI local))** | R-4 (Dev Team IA) : `read_file`, `write_file`, `run_shell` (génération de code, exécution). R-5 (Release Manager IA) : `run_shell` (git checkout, commit, merge). **Option SearXNG** : tool recherche web pour R-2 (System Architect IA) (CVE, benchmarks), R-4 (Dev Team IA) et R-6 (QA & DevOps IA) (debug, doc API récente) — évite boucles HITL et hallucinations. Voir III.7-ter. |
| **Flux de données par nœud** | (1) Lire l'état (checkpointer). (2) Interroger le RAG (recherche sémantique) (Chroma) pour chunks pertinents. (3) Appeler l'LLM (cascade). (4) Écrire en BaseStore (mémoire long terme) si nécessaire (E2 (architecture, DoD (Definition of Done)), E6 (clôture sprint, merge)). (5) Retourner la mise à jour d'état. |
| **Persistance** | Checkpointer (SqliteSaver/PostgresSaver) par step. BaseStore (mémoire long terme) pour mémoire long terme. Chroma pour RAG (recherche sémantique). |
| **Exposition** | LangServe (FastAPI) : `/invoke`, `/stream`, `/playground`. Alternative : invocation directe en CLI Python. |

**Correspondance rôle ↔ nœud** : Chaque ligne du tableau des rôles (section II) correspond à un nœud du graphe. R-1 (Product Owner) et R-7 (Stakeholder) sont des rôles de supervision : ils interviennent via `interrupt()` (validation) et n'ont pas de nœud dédié ; le graphe s'arrête en attente de leur input.

**Lois albert-core et injection par rôle** : Les agents appliquent les lois définies dans specs/REGLES_AGENTS_AGILE.md (référence : plan lois albert-core). Chaque nœud charge graph/laws.py et injecte dans le system prompt les lois applicables à son rôle (ex. R-0 : L1 Anti-précipitation, L4 Gabarit CDC ; R-4 : L8 Non-destruction, L9, L19 Idempotence, L21 Doc-as-code). Lois transverses (L0, L3, L7, L8, L9, L11, L18, L-ANON) s'appliquent à tous les nœuds.

#### 3.5-ter L-ANON — Gateway anonymisation cloud (règle absolue)

**Règle L-ANON** : Aucune donnée personnelle ne quitte la machine locale vers le cloud (Gemini, Claude) sans anonymisation préalable ou autorisation explicite du superviseur désigné (rôle R-1/R-7). L'IA locale (Ollama) est la **gateway de sortie** : tout contenu envoyé à Gemini ou Anthropic doit passer par une couche d'anonymisation avant l'appel API.

**Implémentation (choix possibles)** :
- **Option A — Anonymizer actuel** : specs/REGLES_ANONYMISATION.md (règles métier), config/anonymisation.yaml (patterns et mappings), graph/anonymizer.py avec scrub() et apply_rules(). Point d'intégration : graph/cascade.py, avant chaque appel à ChatGoogleGenerativeAI ou ChatAnthropic.
- **Option B — Microsoft Presidio (LiteLLM)** : Déployé au niveau du routeur LiteLLM, proxy bidirectionnel transparent. **Flux sortant (Masking)** : Presidio détecte et remplace PII, secrets, IP par des tokens (ex. `[SECRET_KEY]`). **Flux entrant (Unmasking)** : Restauration des valeurs réelles dans la réponse avant retour au graphe. Avantage : LangGraph et agents manipulent les données en clair ; sécurité centralisée à l'infrastructure. Voir specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md section 10.
- **Appels Ollama (N0 local)** : non anonymisés — les données restent locales.
- **Données considérées personnelles** : noms, emails, chemins /home/..., adresses IP, URLs internes, clés API, tokens. Règles de remplacement : ex. chemins utilisateur → [PROJECT_ROOT]/, emails → [EMAIL_REDACTED].
- **Autorisation explicite** : Variable AGILE_ALLOW_PERSONAL_CLOUD + confirmation via interrupt ou handle_interrupt.py. Seul le superviseur désigné (rôle R-1/R-7) peut débloquer l'envoi de données non anonymisées.

Cette règle renforce la "Règle d'or de sécurité" (section V) et la stratégie "Anonymisation systématique" (section VI).

#### 3.6 Human-in-the-Loop — Points d'Interruption Obligatoires

**Principe** : Automatiser au maximum le flux, mais bloquer l'exécution pour validation humaine aux décisions critiques. LangGraph `interrupt()` suspend le graphe, sauvegarde l'état (checkpointer), et attend un `Command(resume=...)` de l'opérateur.

| Point d'interrupt | Étape | Déclencheur | Action humaine | Justification |
|-------------------|-------|-------------|----------------|---------------|
| **H1 (validation Epic)** | Fin Phase 0 | R-0 (Business Analyst IA) a produit l'Epic | R-1 (Product Owner) valide ou corrige l'Epic avant injection dans le Backlog. | Décision stratégique : engagement sur la vision. Pas de délégation à l'IA. |
| **H2 (validation Architecture + DoD (Definition of Done))** | Fin E2 (architecture, DoD (Definition of Done)) | R-2 (System Architect IA) a produit Architecture.md + draft DoD (Definition of Done) | R-7 (Stakeholder)/R-1 (Product Owner) valident l'architecture **et** co-construisent la DoD (Definition of Done). Le payload H2 (validation Architecture + DoD (Definition of Done)) contient Architecture.md et un draft DoD (Definition of Done) généré par R-2 (System Architect IA). R-1 (Product Owner) amende la DoD (Definition of Done) (critères d'acceptation), R-7 (Stakeholder) valide l'ensemble. La DoD (Definition of Done) finalisée est écrite dans l'état et dans BaseStore (mémoire long terme). Voir III.8-B et III.8-O. | Choix techniques engageants. DoD (Definition of Done) comme contrat d'acceptation partagé. |
| **H3 (validation Sprint Backlog)** | Fin E3 (Sprint Backlog) | R-3 (Scrum Master IA) a produit le Sprint Backlog | R-1 (Product Owner) valide le découpage et la priorisation des tickets. **Option : forcer `architectural_change=True`** — si R-1 (Product Owner) estime que des tickets impliquent des changements architecturaux non détectés par R-3 (Scrum Master IA), il peut positionner ce flag via le payload de résumé H3 (validation Sprint Backlog) (`Command(resume={"status":"approved","force_architectural_change":true})`), ce qui redéclenche E2 (architecture, DoD (Definition of Done)) avant E4 (exécution code, sprint). | Ajustement de la vélocité, risques de sur/sous-découpage. Filet de sécurité humain si R-3 (Scrum Master IA) n'a pas détecté la nature architecturale des changements (voir F2 (détection changement architectural)). |
| **H4 (Sprint Review, CI verts)** | Fin E5 (tests, CI local) | CI local (R-6 (QA & DevOps IA)) ET CI 1 (feature→develop) GitHub Actions verts | **Séquence** : (1) R-5 (Release Manager IA) push unique en fin de E4 (exécution code, sprint) → PR feature/{project_id}-sprint-{NN}→develop ouverte. (2) CI 1 (feature→develop) (GitHub Actions, feature→develop) et CI local (R-6 (QA & DevOps IA)) tournent en parallèle. R-6 (QA & DevOps IA) poll CI 1 (feature→develop) via `gh run watch` (timeout GITHUB_ACTIONS_TIMEOUT=600s). (3) H4 (Sprint Review, CI verts) déclenché si les deux CI sont verts. R-7 (Stakeholder) réalise la Sprint Review. (4) E6 (clôture sprint, merge) : R-5 (Release Manager IA) merge feature→develop. (5) Post-E6 (clôture sprint, merge) : R-5 (Release Manager IA) ouvre PR develop→main → CI 2 (develop→main) (GitHub Actions, develop→main). Merge develop→main après CI 2 (develop→main) vert. Voir III.8-B et III.8-F. | Double validation pré-H4 (Sprint Review, CI verts). Merge main séparé (post-E6 (clôture sprint, merge)). |
| **H5 (approbation escalade API payante)** | Escalade N2 (cloud payant) | L'IA sollicite Claude Opus/Sonnet (coût) | R-1 (Product Owner) ou R-7 (Stakeholder) approuve l'escalade vers l'API payante. | Contrôle des coûts. Évite les appels non intentionnels. |
| **H6 (résolution conflit Git)** | Conflit Git | R-5 (Release Manager IA) échoue à résoudre un conflit après 2 tentatives | R-1 (Product Owner) résout manuellement (git mergetool), commit, puis reprend le graphe. | Fallback pour conflits complexes. Voir III.8. |

**Implémentation** : Utiliser un checkpointer (ex. `SqliteSaver` ou `PostgresSaver`) pour persister l'état. Chaque `interrupt()` retourne un payload JSON. Procédure : script `scripts/handle_interrupt.py` ou endpoint LangServe (voir III.8).

**Branches rejected** : Si `Command(resume={"status":"rejected","feedback":"..."})` : H1 (validation Epic) rejected → relance nœud R-0 (Business Analyst IA) avec le feedback injecté dans l'état (`state.h1_feedback`). H2 (validation Architecture + DoD (Definition of Done)) rejected → relance R-2 (System Architect IA) avec feedback. H3 (validation Sprint Backlog) rejected → relance R-3 (Scrum Master IA) avec feedback. H4 (Sprint Review, CI verts) rejected → commits correctifs sur même feature branch (pas nouvelle branche), nouveau cycle E5 (tests, CI local) obligatoire (CI local + GitHub Actions) avant H4 (Sprint Review, CI verts) suivant ; limite 3 cycles H4 (Sprint Review, CI verts)-rejected → H5 (approbation escalade API payante) avec payload `reason="max_h4_rejections"`. Voir III.8-B pour le catalogue complet des branches rejected et des reasons H5 (approbation escalade API payante).

**Automatisation sans interrupt** : E4 (exécution code, sprint), E5 (tests, CI local, Self-Healing) s'exécutent sans blocage. Le Self-Healing (R-6 (QA & DevOps IA)→R-4 (Dev Team IA)) est une boucle automatisée avec seuil strict : 3 itérations max (`SELF_HEALING_MAX_ITERATIONS=3`). Au-delà → interrupt H5 (approbation escalade API payante) pour décision humaine.

#### 3.7 Mémoire, Contextes, Persistance et RAG (recherche sémantique) — Architecture Multi-Agents

**Constat** : Un écosystème multi-agents nécessite (1) une mémoire court terme par session (état du graphe), (2) une mémoire long terme partagée (décisions passées, learnings), (3) un accès sémantique à la codebase et aux documents projet. Sans RAG (recherche sémantique) ni base vectorielle, les agents n'ont que le contexte injecté à chaque requête ; ils ne peuvent ni récupérer du code pertinent, ni s'appuyer sur des sprints passés, ni maintenir une cohérence sur plusieurs sessions éloignées.

**Architecture à trois couches** (écosystème LangChain/LangGraph) :

| Couche | Rôle | Technologie | Justification |
|--------|------|-------------|---------------|
| **Mémoire court terme (état par thread)** | Sauvegarder l'état du graphe à chaque étape. Reprendre après interrupt, crash, ou session suivante. Human-in-the-loop requiert une persistance fiable. | **Checkpointer** : `SqliteSaver` (local simple) ou `PostgresSaver` (production, concurrence) | Cycle read-execute-write : à chaque step, l'état (messages, variables, flags) est sérialisé. `thread_id` identifie une exécution (sprint, projet). Permet le "time-travel" (retour à un état antérieur) et la reprise après `interrupt()`. |
| **Mémoire long terme (cross-thread, cross-session)** | Stocker décisions, préférences, résumés de sprints, patterns de résolution. Les agents récupèrent des informations pertinentes par similarité sémantique. | **LangGraph BaseStore (mémoire long terme)** avec recherche sémantique : `PostgresStore` (pgvector) ou store custom basé sur **Chroma** | Mémoire partagée entre tous les agents et toutes les sessions. Permet "rappel" : "comment avons-nous résolu un bug similaire ?", "quelles étaient les décisions d'architecture ?". LangGraph propose `PostgresStore` avec `search(query=...)` pour recherche sémantique. |
| **RAG (recherche sémantique) — Codebase et documents projet** | Fournir aux agents le contexte pertinent : code existant, Architecture.md, Backlog, DoD (Definition of Done), ADRs. Chaque agent (R-2 (System Architect IA), R-3 (Scrum Master IA), R-4 (Dev Team IA)) doit pouvoir récupérer des extraits par requête naturelle. | **Base vectorielle** : **Chroma** + **nomic-embed-text** (Ollama) | Continue.dev a son propre RAG (recherche sémantique) (LanceDB, voyage-code-3) pour l'humain dans VS Code ; les agents LangGraph tournent dans un processus Python distinct et n'y ont pas accès. Ils nécessitent un RAG (recherche sémantique) dédié. Chroma : in-process, sans service externe, ~3,5 Go pour 1M vecteurs (768 dim). nomic-embed-text : 100 % local via Ollama, 0 €, performant. |

**Contenu à indexer dans le RAG (recherche sémantique) (vecteurs)** :

| Source | Usage par les agents |
|--------|----------------------|
| Codebase (`src/`, fichiers principaux) | R-4 (Dev Team IA) (Dev) : récupérer code existant, patterns, types. R-2 (System Architect IA) (Architecte) : comprendre la structure actuelle. |
| Architecture.md, ADRs | R-2 (System Architect IA), R-3 (Scrum Master IA), R-4 (Dev Team IA) : respect des décisions, cohérence architecturale. |
| Besoins - Product Backlog.md, DoD (Definition of Done) | R-1 (Product Owner), R-3 (Scrum Master IA) : priorisation, critères d'acceptation. |
| Tickets résolus, résumés de sprints | R-3 (Scrum Master IA), R-4 (Dev Team IA) : patterns de découpage, résolutions passées. |

**Flux de données** : À chaque étape du graphe, l'agent peut (1) lire l'état court terme (checkpointer), (2) interroger le RAG (recherche sémantique) pour récupérer les K chunks les plus pertinents (ex. top 5), (3) écrire en mémoire long terme (BaseStore (mémoire long terme)) les éléments à retenir pour plus tard. Les embeddings sont produits localement par `nomic-embed-text` (Ollama).

**Recommandations techniques** :

| Choix | Recommandation | Justification |
|-------|----------------|---------------|
| **Checkpointer** | `SqliteSaver` pour démarrage local ; `PostgresSaver` dès mise en production ou multi-utilisateurs | Sqlite : un fichier, zéro config. Postgres : robustesse, concurrence, compatible avec pgvector pour BaseStore (mémoire long terme). |
| **Base vectorielle** | **Chroma** | In-process, pas de service à lancer. Suffisant pour codebase + docs d'un projet (ordre de grandeur : 10K–100K chunks). Si scale > 1M chunks : migrer vers Qdrant ou Postgres+pgvector. |
| **Embeddings** | **nomic-embed-text** via Ollama (`ollama pull nomic-embed-text`) | Local, 0 €, 768 dimensions. Performances comparables à text-embedding-ada-002. Intégration LangChain : `OllamaEmbeddings(model="nomic-embed-text")`. |
| **Indexation** | Déclencher après chaque commit significatif ou en fin de sprint | Pipeline : chunking (par fichier ou AST pour le code), embeddings, insertion Chroma. Métadonnées : `source`, `type` (code|doc|ticket), `project`, `sprint`. Voir III.7-bis pour options temps réel et incrémentiel. |
| **RAG (recherche sémantique) partagé IDE** | Option : Chroma exposé via MCP (Model Context Protocol) pour agents ET IDE | chroma-mcp (chroma-core/chroma-mcp) ou MCP (Model Context Protocol) custom. Continue.dev, Roo Code, Cursor, Cline peuvent se connecter au même Chroma que les agents. Un seul index = alignement humains/agents. Voir III.7-bis. |

**Persistance à travers sessions éloignées** : Le checkpointer conserve l'état par `thread_id`. Une "session" = un `thread_id` (ex. `sprint-2026-03-01` ou `project-X-phase-0`). Pour reprendre des semaines plus tard : réutiliser le même `thread_id` ; LangGraph charge le dernier checkpoint. La mémoire long terme (BaseStore (mémoire long terme)) et le RAG (recherche sémantique) (Chroma) sont persistés sur disque ; ils survivent aux redémarrages et aux sessions espacées.

#### 3.7-bis Chroma RAG (recherche sémantique) — Options temps réel et partage IDE (MCP (Model Context Protocol))

**Justification** : Chroma indexe code + docs + artefacts (Backlog, Architecture, DoD (Definition of Done), ADRs, tickets). Pour atteindre une fraîcheur comparable aux IDE et partager le même RAG (recherche sémantique) entre agents et humains, les options suivantes sont spécifiées.

**Options d'indexation (temps réel)** :

| Option | Description | Variable | Défaut |
|--------|-------------|----------|--------|
| **File watcher** | Déclenche index_rag à la sauvegarde de fichier (hors E4 (exécution code, sprint)/E5 (tests, CI local)) | `AGILE_RAG_FILE_WATCHER=true` | `false` |
| **Indexation incrémentale** | Ré-indexer uniquement les fichiers modifiés (hash ou mtime) | `AGILE_RAG_INCREMENTAL=true` | `true` si file watcher actif |
| **AGILE_DEFER_INDEX** | Indexation différée : évite conflit GPU pendant E4 (exécution code, sprint)/E5 (tests, CI local) | `AGILE_DEFER_INDEX=true` | `true` (défaut — voir III.8-C, F7 (AGILE_DEFER_INDEX)) |

**Règle GPU** : Si `AGILE_RAG_FILE_WATCHER=true`, le watcher ne lance **pas** d'indexation pendant E4 (exécution code, sprint)/E5 (tests, CI local) (qwen2.5-coder sur GPU). Détection : processus LangGraph actif ou variable `AGILE_E4_E5_ACTIVE`. En mode différé, le watcher écrit dans `pending_index.log` comme le hook Git.

**Partage RAG (recherche sémantique) avec l'IDE (MCP (Model Context Protocol))** :

| Option | Description | Effort |
|--------|-------------|--------|
| **chroma-mcp** (recommandé en premier) | Serveur MCP (Model Context Protocol) existant (chroma-core/chroma-mcp). Configurer pour pointer vers la même instance Chroma que index_rag. Les IDE (Continue.dev, Roo Code, Cursor, Cline) se connectent via MCP (Model Context Protocol). L'agent appelle `chroma_query_documents` pour le contexte code/docs. | Configuration + alignement schéma collections |
| **MCP (Model Context Protocol) custom** | Serveur MCP (Model Context Protocol) léger exposant `search_codebase(query, project_id, top_k)` si chroma-mcp ne convient pas (schéma, métadonnées projet). | Développement |

**Flux partagé** : index_rag.py alimente Chroma. Les nœuds LangGraph interrogent Chroma directement. chroma-mcp (ou MCP (Model Context Protocol) custom) expose la même Chroma aux clients MCP (Model Context Protocol). Continue.dev, Roo Code et Cursor configurés avec chroma-mcp → même index pour agents et humains.

**Risque concurrence Chroma** : En mode SQLite (`persist_directory`), Chroma peut subir des locks si accès concurrent (index_rag + query_rag + chroma-mcp). **Décision actuelle** : ne jamais exécuter index_rag pendant E4/E5 (AGILE_DEFER_INDEX=true, indexation différée en fin de sprint). À réviser si migration vers Chroma serveur HTTP ou accès concurrent avéré en prod. Voir specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md section 8 (C.9).

**Flux d'écriture BaseStore (mémoire long terme)** (obligatoire pour mémoire long terme) : À la fin de E2 (architecture, DoD (Definition of Done)), le nœud R-2 (System Architect IA) écrit dans le BaseStore (mémoire long terme) (namespace `project/{id}/architecture`) un résumé "architecture_approved" avec date et version. À la fin de E6 (clôture sprint, merge), un nœud post-review écrit (namespace `project/{id}/sprints`) un "sprint_summary" (résumé incrément, tickets livrés, décisions). Format JSON. Les agents R-3 (Scrum Master IA) et R-4 (Dev Team IA) interrogent le BaseStore (mémoire long terme) avant découpage ou implémentation pour récupérer les résumés pertinents.

#### 3.7-ter SearXNG — Recherche web temps réel pour les agents (complément RAG)

**Justification** : Le RAG (recherche sémantique) (Chroma) fournit le contexte code/docs projet, mais les agents restent limités par le *knowledge cutoff* des LLM et le contenu statique indexé. SearXNG comble ce manque : accès web en temps réel, privé et gratuit.

| Aspect | Détail |
|--------|--------|
| **Qu'est-ce que SearXNG** | Métamoteur open source auto-hébergé. Interroge simultanément Google, Bing, DuckDuckGo, GitHub, StackOverflow, etc., agrège les résultats, supprime les pisteurs, renvoie JSON. |
| **Usage par rôle** | **R-2 (System Architect IA)** : CVE, benchmarks, état de l'art. **R-4 (Dev Team IA)** : erreurs de compilation, doc API récente, issues GitHub. **R-6 (QA & DevOps IA)** : debug, stack traces. |
| **Alignement Coût Zéro** | 100 % gratuit et illimité. Alternative aux API payantes (Tavily, Google Search, Bing). Conteneur Docker aux côtés de Chroma, FastAPI. |
| **Protection PI** | Proxy : anonymise les requêtes des agents avant envoi aux moteurs. Cohérent avec L-ANON (données locales). |
| **Engines paramétrables** | Requêtes ciblées : GitHub (implémentation), StackOverflow (debug), ArXiv (recherche). |
| **Intégration LangChain** | `SearxSearchWrapper` (LangChain). Tool standard passé au graphe. Conteneur `searxng/searxng` dans docker-compose, format JSON. |

**Référence** : Voir `specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md` section 9.

#### 3.7-quater Nomenclature technique — Sécurité & Extensions

| Technologie | Rôle |
|-------------|------|
| **Microsoft Presidio** | Moteur NLP local d'anonymisation et désanonymisation des prompts (PII, secrets, IP, variables internes). |
| **SearXNG** | Métamoteur de recherche auto-hébergé (web-browsing privé pour agents). |
| **LangChain SearxSearchWrapper** | Interface connectant le graphe LangGraph à l'API locale SearXNG. |

**Référence** : specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md section 10.

#### 3.8 Procédures Opérationnelles Consolidées

*Cette section intègre l'ensemble des procédures opérationnelles finales issues des simulations 001–013. Elle remplace l'ancienne suite de sections III.8–III.19. L'historique détaillé par simulation est conservé en Annexe B.*

---

##### A. Nœud load_context — Initialisation de chaque thread

Exécuté en tout premier à chaque démarrage de thread (avant E1 (idéation, Epic) pour un nouveau projet, avant E3 (Sprint Backlog)/E4 (exécution code, sprint)/HOTFIX (correctif urgent) pour un sprint ou un hotfix). Charge depuis le BaseStore (mémoire long terme) :

1. `adr_counter` depuis `project/{id}/adr_counter`. Défaut : 0.
2. `sprint_number` depuis `project/{id}/sprint_counter`. Défaut : 1.
3. `dod` depuis `project/{id}/dod/{sprint_number}`. Fallback : `dod/{sprint_number-1}`. Si sprint_number=1 et aucune DoD (Definition of Done) : `None` (E2 (architecture, DoD (Definition of Done)) la créera).
4. Injecte les valeurs dans l'état initial du thread.

**Résilience BaseStore (mémoire long terme)** : Variable `AGILE_BASESTORE_STRICT` (défaut : `true` en production, `false` en développement — F10 (AGILE_BASESTORE_STRICT)). Si `false` et BaseStore (mémoire long terme) inaccessible : valeurs par défaut + log WARNING (risque d'incohérence silencieuse : un projet au sprint 5 redémarre avec sprint_number=1). Si `true` : exception explicite avec message d'aide — **recommandé dès qu'un projet a dépassé le sprint 1**. `setup_project_hooks.sh` génère `.agile-env` avec `AGILE_BASESTORE_STRICT=true` par défaut.

**Vérification d'intégrité au démarrage (F10 (AGILE_BASESTORE_STRICT))** : Avant d'accepter les valeurs par défaut en mode `false`, load_context vérifie que le BaseStore (mémoire long terme) est réellement inaccessible (connexion refusée, fichier absent) plutôt que simplement vide (cas normal au premier lancement). Si le BaseStore (mémoire long terme) est accessible mais renvoie des valeurs manquantes, les valeurs par défaut sont utilisées normalement (premier sprint). Si le BaseStore (mémoire long terme) est inaccessible et que `sprint_number > 1` est détectable via un autre moyen (ex. présence de branches `feature/{id}-sprint-0{N}` en Git) : log ERROR au lieu de WARNING, et suggestion d'activer `AGILE_BASESTORE_STRICT=true`.

**Routing start_phase** : load_context route le graphe selon le paramètre `start_phase` (`"E1 (idéation, Epic)"` | `"E3 (Sprint Backlog)"` | `"HOTFIX (correctif urgent)"`). Valeur par défaut : `"E1 (idéation, Epic)"`. Commandes types — *à exécuter dans le **terminal intégré à VS Code** (panneau Terminal de l'IDE), sauf usage volontaire d'un terminal externe* :
- Nouveau projet : `python run_graph.py --project-id <id> --start-phase E1 (idéation, Epic) --thread-id <id>-phase-0`
- Nouveau sprint : `python run_graph.py --project-id <id> --start-phase E3 (Sprint Backlog) --thread-id <id>-sprint-02`
- Hotfix : `python run_graph.py --project-id <id> --start-phase HOTFIX (correctif urgent) --thread-id <id>-hotfix-<date> --hotfix-description "..."`

Pour `start_phase HOTFIX (correctif urgent)` : load_context crée un Sprint Backlog synthétique `SprintBacklog(tickets=[Ticket(id="HF-001", description=hotfix_description)], architectural_change=False)`.

---

##### B. Procédure Human-in-the-Loop (interrupts H1 (validation Epic)–H6 (résolution conflit Git))

**Exécution** : Endpoint LangServe `/playground` (s'ouvre dans le **navigateur**) ou script `scripts/handle_interrupt.py [--thread-id <id>]` (à lancer depuis le **terminal intégré à VS Code**).
- Si `--thread-id` omis : liste les threads en attente, triés par `project_id` puis par type H (H1 (validation Epic)→H6 (résolution conflit Git)). Demande de choisir.
- Si `--thread-id` fourni mais thread sans interrupt : message d'erreur explicite, exit code 1.
- Exit codes : 0=succès, 1=erreur (thread invalide), 2=usage (arguments invalides).
- Séquence : (1) lit l'état via l'API LangServe, (2) affiche le payload `__interrupt__`, (3) attend l'entrée (`approved` | `rejected` | `feedback`), (4) envoie `graph.invoke(Command(resume=...), config)`.
- En absence de l'humain : option `resume={"status":"rejected","resume_after":"<date>"}`. **Notification obligatoire si interrupt non traité > 48h** (F5 (notification interrupt > 48h)) : un script cron `scripts/notify_pending_interrupts.py` (lancé toutes les heures par `setup_project_hooks.sh`) vérifie les threads en attente et émet une alerte — par défaut via log `logs/pending_interrupts_alert.log` + affichage dans le terminal qui exécute le script cron (souvent terminal système / cron, pas IDE). Pour notification email ou webhook : configurer `AGILE_NOTIFY_CMD="<commande>"` dans `.agile-env` (ex. `"mail -s 'Interrupt en attente' nghia@example.com"` ou `"curl -X POST <webhook_url> -d '...'"`) ; si absent, la notification reste locale (log). Variable `AGILE_INTERRUPT_TIMEOUT_HOURS=48` (défaut). La consultation des interrupts par l'humain se fait via `handle_interrupt.py` dans le **terminal intégré à VS Code**.

**Branches rejected** :
- **H1 (validation Epic) rejected** → injecte feedback dans `state.h1_feedback`, reboucle vers R-0 (Business Analyst IA) (nouveau Epic). Limite : 3 cycles → H5 (approbation escalade API payante) `reason="max_rejections_H1 (validation Epic)"`.
- **H2 (validation Architecture + DoD (Definition of Done)) rejected** → injecte dans `state.h2_feedback`, reboucle vers R-2 (System Architect IA) (Architecture + DoD (Definition of Done) revisitées). Limite : 3 cycles → H5 (approbation escalade API payante) `reason="max_rejections_H2 (validation Architecture + DoD (Definition of Done))"`.
- **H3 (validation Sprint Backlog) rejected** → injecte dans `state.h3_feedback`, reboucle vers R-3 (Scrum Master IA) (Sprint Backlog refait). Limite : 3 cycles → H5 (approbation escalade API payante) `reason="max_rejections_H3 (validation Sprint Backlog)"`.
- **H3 (validation Sprint Backlog) approved avec `force_architectural_change=true`** → le nœud post-H3 (validation Sprint Backlog) positionne `state.needs_architecture_review = True` et `state.sprint_backlog.architectural_change = True`, puis route vers E2 (architecture, DoD (Definition of Done)) au lieu de E4 (exécution code, sprint). Voir III.8-O (re-déclenchement E2 (architecture, DoD (Definition of Done))).
- **H4 (Sprint Review, CI verts) rejected** → commits correctifs sur la même feature branch, nouveau cycle E5 (tests, CI local) obligatoire. Limite : 3 cycles → H5 (approbation escalade API payante) `reason="max_h4_rejections"`.
- **H6 (résolution conflit Git)** : Si R-5 (Release Manager IA) échoue à résoudre un conflit Git après 2 tentatives → interrupt. L'humain résout (`git mergetool`), commit, puis `Command(resume="resolved")`.

**L18 — Contradictions RAG/Backlog/Architecture** : Si les sources (RAG, Backlog, Architecture.md) se contredisent, l'agent produit un payload interrupt avec reason=spec_contradiction et liste les sources en conflit. R-1 (Product Owner) ou R-7 (Stakeholder) résout la contradiction (correction des artefacts, choix explicite). Jamais arbitrer silencieusement (loi L18 Arrêt sur contradiction).

**Catalogue complet des reasons H5 (approbation escalade API payante)** :

| reason | Déclencheur |
|--------|-------------|
| `cost_escalation` | Escalade vers N2 (cloud payant) (Opus/Sonnet) pour coût |
| `max_rejections_H1 (validation Epic)` | 3 cycles H1 (validation Epic)-rejected |
| `max_rejections_H2 (validation Architecture + DoD (Definition of Done))` | 3 cycles H2 (validation Architecture + DoD (Definition of Done))-rejected |
| `max_rejections_H3 (validation Sprint Backlog)` | 3 cycles H3 (validation Sprint Backlog)-rejected |
| `max_h4_rejections` | 3 cycles H4 (Sprint Review, CI verts)-rejected |
| `github_actions_timeout` | Timeout polling CI 1 (feature→develop) ou CI 2 (develop→main) (GITHUB_ACTIONS_TIMEOUT) |
| `ci2_github_actions_failure` | CI 2 (develop→main) rouge après merge_to_main |
| `pr_review_required` | Branch protection stricte sur main (reviewer requis) |
| `spec_contradiction` | Contradiction détectée entre RAG (recherche sémantique), Backlog, Architecture.md (L18) |

**H4 (Sprint Review, CI verts) sequence complète** : (1) R-5 (Albert Release Manager) push unique feature branch fin E4 (exécution code, sprint) + `gh pr create --base develop`. (2) CI local (R-6 (Albert QA & DevOps)) et CI 1 (feature→develop) (GitHub Actions, feature→develop) tournent en parallèle. R-6 (Albert QA & DevOps) poll CI 1 (feature→develop) via `gh pr checks {pr_number} --required --watch --interval 30` (timeout `GITHUB_ACTIONS_TIMEOUT=600s`). (3) Les deux CI verts → H4 (Sprint Review, CI verts). (4) H4 (Sprint Review, CI verts) resume approuvé → E6 (clôture sprint, merge) : Retrofit + sprint_complete. **H4 (Sprint Review, CI verts) est toujours l'interrupt de sortie de E5 (tests, CI local)**, indépendamment du nombre de H5 (approbation escalade API payante) précédents.

**Ordre opérations post-interrupt** (H1 (validation Epic), H2 (validation Architecture + DoD (Definition of Done)), H4 (Sprint Review, CI verts)) : (1) mise à jour état avec feedback, (2) écriture BaseStore (mémoire long terme) si applicable, (3) appel index_rag, (4) transition nœud suivant.

**T1 — Ordre strict pour H1 (validation Epic)** : R-1 (Product Owner) doit avoir créé `Besoins - Product Backlog.md` et committé **avant** d'envoyer `Command(resume)` sur H1 (validation Epic). Sinon post_h1 indexe un fichier vide.

---

##### C. Pipeline d'indexation RAG (recherche sémantique)

**Déclencheurs** :
- **Nœud post_h1** (après H1 (validation Epic) resume) : `index_rag.py --project-root {state.project_root} --project-id {state.project_id} --sources backlog`
- **Nœud post-H2 (validation Architecture + DoD (Definition of Done))** : `--sources architecture,dod`
- **Nœud post-H4 (Sprint Review, CI verts)** : `--sources all`
- **Hook Git post-commit** : lit `AGILE_PROJECT_ID` (depuis `.agile-project-id`) et `AGILE_ORCHESTRATION_ROOT` (depuis `.agile-env`). Appelle `python $AGILE_ORCHESTRATION_ROOT/scripts/index_rag.py --project-root $(pwd) --project-id $AGILE_PROJECT_ID`. Ne doit **pas** utiliser `$(basename $(pwd))` comme project_id.
- **File watcher** (optionnel) : Si `AGILE_RAG_FILE_WATCHER=true` dans `.agile-env`, un daemon/watchdog surveille les fichiers du projet et déclenche `index_rag.py --sources code` (ou `all`) sur modification. **Désactivé automatiquement pendant E4 (exécution code, sprint)/E5 (tests, CI local)** (conflit GPU avec qwen2.5-coder). Si `AGILE_DEFER_INDEX=true` et E4 (exécution code, sprint)/E5 (tests, CI local) actif : écrit dans `pending_index.log` comme le hook.

**Mode différé (AGILE_DEFER_INDEX=true)** : Si actif dans `.agile-env`, le hook (et le file watcher si actif) écrit dans `logs/pending_index.log` (`<timestamp> <commit_hash> <project_id>`) au lieu de lancer index_rag. Le nœud sprint_complete traite `pending_index.log` en fin de sprint (hors E4 (exécution code, sprint)/E5 (tests, CI local), évite les conflits GPU). **Valeur par défaut : `true`** (F7 (AGILE_DEFER_INDEX)) — `setup_project_hooks.sh` génère `.agile-env` avec `AGILE_DEFER_INDEX=true` par défaut. Pour désactiver (si GPU disposant de > 16 Go VRAM) : modifier manuellement `.agile-env`. En legacy 12 Go (`AGILE_GPU_PROFILE=legacy_12gb`), ne jamais passer à `false` (nomic-embed-text + qwen2.5-coder partagent le GPU ; indexation pendant E4/E5 = conflit probable).

**Indexation incrémentale** : Si `AGILE_RAG_INCREMENTAL=true`, index_rag ne ré-indexe que les fichiers modifiés (comparaison mtime ou hash). Réduit charge GPU et latence. Compatible avec file watcher. Valeur par défaut : `true` si file watcher actif, sinon `false`.

**Script index_rag.py** (dans le projet orchestration) :
- Signature : `--project-root <path> --project-id <id> [--sources backlog|architecture|code|all] [--strict] [--incremental]`
- Option `--incremental` : indexation incrémentale (fichiers modifiés uniquement)
- Résilience : try/except par fichier, skip en erreur, rapport dans `logs/index_rag_<timestamp>.log`
- Si `--strict` et 0 fichier indexé : exit 1. Si > 10 % en erreur : log warning dans `logs/index_errors.log`

**Bootstrap** : `scripts/setup_project_hooks.sh --orchestration-root <path> --project-root <path> --project-id <id>` :
- Crée `.agile-project-id` (project_id sur une ligne)
- Crée `.agile-env` (AGILE_ORCHESTRATION_ROOT, AGILE_PROJECT_ID, AGILE_DEFER_INDEX=true, AGILE_PROJECTS_JSON, AGILE_RAG_FILE_WATCHER=false, AGILE_RAG_INCREMENTAL, AGILE_BASESTORE_STRICT=true, AGILE_INTERRUPT_TIMEOUT_HOURS=48, AGILE_NOTIFY_CMD, SYNC_ARTIFACTS_CRON="0 0 * * 0")
- Crée la branche `develop` depuis `main` si absente : `git checkout -b develop main && git push -u origin develop`

---

##### D. Stratégie de branches Git

Modèle **feature-par-sprint** :

| Branche | Rôle | Gestionnaire |
|---------|------|-------------|
| `main` | Production. Merge uniquement après CI 2 (develop→main) vert. | R-5 (Albert Release Manager) |
| `develop` | Intégration continue. Base de toutes les features. | R-5 (Albert Release Manager) |
| `feature/{project_id}-sprint-{NN}` | Travail du sprint N. Créée depuis `develop`. | R-5 (Albert Release Manager) |
| `hotfix/{project_id}-{date}-{description}` | Correctif urgent depuis `main`. | R-5 (Albert Release Manager) |

**Flux sprint** : feature→develop (merge R-5 (Albert Release Manager) après H4 (Sprint Review, CI verts) approuvé) → PR develop→main (CI 2 (develop→main)) → merge develop→main (gh pr merge, après CI 2 (develop→main) vert).

**Flux hotfix** : hotfix créée depuis `main`. CI 1 (feature→develop) sur PR hotfix→main. H4 (Sprint Review, CI verts) validation. R-5 (Albert Release Manager) merge hotfix→main (`gh pr merge`). Puis R-5 (Albert Release Manager) merge hotfix→develop directement (`git checkout develop && git merge --no-ff hotfix/... && git push`) — sans PR ni CI supplémentaire, le code ayant déjà été validé.

**H6 (résolution conflit Git) conflits** : s'applique aux merge feature→develop et develop→main. Après 2 tentatives auto : interrupt H6 (résolution conflit Git).

**Timing push R-5 (Albert Release Manager)** : push unique en fin de E4 (exécution code, sprint), après le dernier commit de ticket. Un seul trigger CI 1 (feature→develop).

---

##### E. Nœud sprint_complete — Deux phases

**Phase 1 — sprint_summary** :
1. Écriture `sprint_summary` dans BaseStore (mémoire long terme) (`project/{id}/sprints/sprint-{NN}`)
2. Déclenchement index_rag (ou traitement `pending_index.log` si `AGILE_DEFER_INDEX=true`)
3. Incrément `state.sprint_number` → N+1 et écriture BaseStore (mémoire long terme) **uniquement en mode dégradé** (github_repo absent)

**Phase 2 — merge_to_main** (si `github_repo` présent) :
1. R-5 (Albert Release Manager) merge `feature/{id}-sprint-{NN} → develop`
2. `gh pr create --base main --head develop --title "Release sprint {NN}"`
3. `gh pr checks {pr_number} --required --watch --interval 30` (CI 2 (develop→main))
4. CI 2 (develop→main) vert → `gh pr merge --merge --delete-branch=false`. Incrément `state.sprint_number` → N+1, écriture BaseStore (mémoire long terme)
5. CI 2 (develop→main) rouge → H5 (approbation escalade API payante) `reason="ci2_github_actions_failure"` **sans modifier sprint_number**

**Branch protection** :
- Sans protection (solo) : `gh pr merge` automatique après CI 2 (develop→main) vert
- Avec protection CI-only sur `develop` : `gh pr merge` passe si CI vert
- Avec protection stricte sur `main` (reviewer requis) : H5 (approbation escalade API payante) `reason="pr_review_required"`, opérateur approuve manuellement la PR, puis `Command(resume="merged")`

**auto_next_sprint** : si `projects[project_id].auto_next_sprint = true`, la boucle vers E3 (Sprint Backlog) (thread_id `{project_id}-sprint-{NN+1}`) se déclenche **après la phase 2** (mode complet) ou **après la phase 1** (mode dégradé).

---

##### F. GitHub Actions CI 1 (feature→develop) et CI 2 (develop→main)

| CI | PR cible | Déclencheur | Condition pour la suite |
|----|----------|-------------|------------------------|
| **CI 1 (feature→develop)** | `feature/{id}-sprint-{NN} → develop` | R-5 (Albert Release Manager) push fin E4 (exécution code, sprint) + `gh pr create` | Nécessaire pour déclencher H4 (Sprint Review, CI verts) |
| **CI 2 (develop→main)** | `develop → main` | sprint_complete phase 2 + `gh pr create` | Nécessaire pour merge develop→main |

**Polling** : R-6 (Albert QA & DevOps) utilise `gh pr checks {pr_number} --required --watch --interval 30`. Timeout `GITHUB_ACTIONS_TIMEOUT=600s` (défaut). Workflow GitHub Actions déclenché sur `pull_request` (pas seulement `push`).

**Mode dégradé** (github_repo absent dans projects.json) : CI 1 (feature→develop)/CI 2 (develop→main) skippés. H4 (Sprint Review, CI verts) déclenché sur CI local seul. Log WARNING. Merge develop→main : action manuelle.

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
- `github_repo` (optionnel) : requis pour CI 1 (feature→develop)/CI 2 (develop→main). Si absent → mode dégradé.
- `archived: true` : projet exclu des traitements actifs, gardé en référence.

**handle_interrupt.py** affiche les interrupts groupés par `project_id`, triés par H1 (validation Epic)→H6 (résolution conflit Git).

---

##### H. Articulation E4 (exécution code, sprint) : LangGraph pilote

E4 (exécution code, sprint) est piloté par les nœuds R-4 (Albert Dev Team) et R-5 (Albert Release Manager) du graphe. R-4 (Albert Dev Team) dispose de tools : `read_file`, `write_file`, `run_shell`. R-5 (Albert Release Manager) gère Git (`run_shell`). Les tools utilisent `state.project_root` comme répertoire de travail. Roo Code et Continue.dev restent l'interface humaine (hors flux automatisé). R-4 (Albert Dev Team) traite les tickets séquentiellement.

**Écriture atomique pour `write_file` (F9 (write_file atomique))** : Le tool `write_file` doit utiliser le pattern atomic write (écriture dans un fichier temporaire `.tmp`, puis `os.replace()`) pour garantir qu'une coupure d'électricité pendant l'écriture ne laisse pas de fichier partiellement écrit et corrompu. Implémentation Python :
```python
import os, tempfile, pathlib

def write_file(path: str, content: str) -> None:
    target = pathlib.Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        mode="w", dir=target.parent, delete=False, suffix=".tmp"
    ) as tmp:
        tmp.write(content)
        tmp_path = tmp.name
    os.replace(tmp_path, target)  # atomic sur Linux/macOS
```
`os.replace()` est atomique sur Linux (même système de fichiers). En cas de coupure pendant l'écriture du `.tmp`, le fichier cible reste intact dans son état précédent. R-6 (Albert QA & DevOps) n'obtiendra jamais un fichier source partiellement écrit.

---

##### I. Self-Healing (R-6 (Albert QA & DevOps)→R-4 (Albert Dev Team))

Seuil : `SELF_HEALING_MAX_ITERATIONS=3`. Au-delà → interrupt H5 (approbation escalade API payante) `reason="cost_escalation"` (approbation N2 (cloud payant)) ou arrêt avec rapport d'échec.

**Backoff HTTP 429** : 3 tentatives max, backoff exponentiel (2^attempt secondes). Variable `API_429_MAX_RETRIES=3`. Si 429 persiste → H5 (approbation escalade API payante) `reason="cost_escalation"` ou "pause et retry demain".

---

##### J. Stratégie GPU (Ollama)

Priorité : `qwen2.5-coder:14b` (E4 (exécution code, sprint), E5 (tests, CI local)) > `qwen2.5:14b` (Phase 0, E2 (architecture, DoD (Definition of Done))).

- Keep-alive (évite le déchargement après inactivité) : `export OLLAMA_KEEP_ALIVE=24h` (voir checklist 4.1).
- Warmup : précharger le modèle prioritaire (ex. `ollama run qwen2.5-coder:14b "warmup"`).
- Éviter les indexations embeddings lourdes (nomic-embed-text) pendant E4/E5 ; utiliser `AGILE_DEFER_INDEX=true` (défaut) si contention GPU.

**Legacy 12 Go (RTX 3060)** : Sur configuration 12 Go VRAM, `AGILE_DEFER_INDEX=true` et `AGILE_RAG_FILE_WATCHER=false` sont recommandés par défaut (Sim 014). Voir `docs/HARDWARE_GPU.md`.

**Continue.dev pendant E4 (exécution code, sprint)/E5 (tests, CI local)** : Si Continue.dev reste ouvert pendant l'exécution du graphe (E4 (exécution code, sprint), E5 (tests, CI local)), le configurer sur **qwen2.5-coder:14b** (aligné sur R-4 (Albert Dev Team)) pour éviter le swapping de modèles. Un modèle différent (ex. qwen2.5:14b) force Ollama à décharger qwen2.5-coder → latence et timeouts. Alternative : désactiver l'autocomplétion IA pendant E4 (exécution code, sprint)/E5 (tests, CI local).

---

##### K. Politique de traçage LangSmith

Si risque de dépassement 5 000 traces/mois (free tier) : `LANGCHAIN_TRACING_SAMPLING_RATE=0.2` (20 %) ou `LANGCHAIN_TRACING_ERRORS_ONLY=true`. Priorité : conserver les runs en erreur.

---

##### L. Politique de rétention et archivage

**Checkpoints** : purge `scripts/purge_checkpoints.py [--dry-run] [--max-age-days 90]`. "90 jours" = date du dernier step. Exclure les threads avec `__interrupt__` non résolu. Log des threads supprimés.

**Cas particulier — projet en pause longue (F4 (projet en pause, purge))** : Si un sprint est en cours (phase E3 (Sprint Backlog)–E6 (clôture sprint, merge), sans interrupt actif) au moment de la purge, ses checkpoints peuvent être supprimés. À la reprise, `load_context` retrouve `sprint_number` et `adr_counter` depuis le BaseStore (mémoire long terme) (qui persiste indéfiniment), mais la reprise exacte du step interrompu n'est plus possible : il faut relancer depuis `--start-phase E3 (Sprint Backlog)`. Pour éviter cela : (1) `purge_checkpoints.py` exclut par défaut les threads dont `sprint_number` est inférieur à la valeur courante en BaseStore (mémoire long terme) (sprint non clôturé) ; (2) option `--protect-active-sprints` (défaut : `true`) : un thread est "actif" si son `sprint_number` dans l'état correspond au `sprint_counter` en BaseStore (mémoire long terme). Documenter ce comportement dans le README du projet orchestration.

**Chroma** : une collection par projet. `scripts/export_chroma.py --project-id <id> --output <path>.json`. `scripts/import_chroma.py --project-id <id> --input <path>.json`. Exporter avant suppression.

**Logs** : rotation 7 jours, max 100 Mo. LangSmith : rétention 14 jours (free tier), export optionnel via `export_langsmith_traces.py`.

---

##### M. Procédure de clôture de projet

Checklist (manuelle par R-1 (Product Owner)/R-7 (Stakeholder) ou via nœud optionnel `project_close`) :
1. R-5 (Albert Release Manager) merge final `develop → main` (`git merge --no-ff`) si non déjà fait
2. `scripts/export_chroma.py --project-id <id> --output archives/<id>-<date>.json`
3. `projects.json` : `"archived": true`
4. `scripts/purge_checkpoints.py --dry-run` (vérification)
5. BaseStore (mémoire long terme) : `project/{id}/status = "archived"`
6. Documenter dans README ou Architecture.md

---

##### N. Génération de documentation (build_docs) et L21 Doc-as-code

Étape dans E5 (tests, CI local), avant les tests : R-6 (Albert QA & DevOps) exécute `sphinx-build` (Python) ou `npm run docs` (JS/TS). Si pas de `conf.py` / `jsdoc.json` : skip avec log. Variable `BUILD_DOCS_REQUIRED=false` (défaut : skip silencieux ; `true` : échec si absent).

**L21 Doc-as-code** : R-6 (Albert QA & DevOps) refuse tout commit de R-4 (Albert Dev Team) qui (1) ajoute du code sans docstrings sur les éléments publics (classes, fonctions exportées), ou (2) modifie l'API sans mise à jour de la documentation générée (JSDoc, Sphinx), lorsque `BUILD_DOCS_REQUIRED=true`. Règle appliquée dans le pipeline E5 (tests, CI local) : build_docs → unit → intégration → E2E.

---

##### O. Synchronisation Architecture.md (sync_artifacts)

**Activé par défaut** via cron hebdomadaire. Variable `SYNC_ARTIFACTS_CRON` (défaut : `"0 0 * * 0"` = dimanche minuit) : compare la structure du code à Architecture.md et génère un rapport de dérive dans `logs/sync_artifacts_<date>.log`. Si `SYNC_ARTIFACTS_CRON=""` (chaîne vide) : désactivé explicitement. `setup_project_hooks.sh` génère l'entrée cron correspondante par défaut — supprimer manuellement si non souhaité.

**Justification (F1 (sync_artifacts cron))** : Sans ce cron, la dérive entre code réel et Architecture.md peut s'accumuler silencieusement sur plusieurs sprints, sans que les agents ni les superviseurs ne la détectent. Le rapport hebdomadaire constitue un filet de sécurité contre les régressions documentaires long terme.

**Numérotation ADRs** : `state.adr_counter` (TypedDict, chargé depuis BaseStore (mémoire long terme) `project/{id}/adr_counter`). Incrémenté par R-2 (Albert System Architect) à chaque ADR (Architecture Decision Record) produit. Fichier : `docs/ADR (Architecture Decision Record)-{NNN:03d}-{date}-{slug}.md`.

**DoD (Definition of Done) versionnée** : namespace BaseStore (mémoire long terme) `project/{id}/dod/{sprint_number}`. Chaque sprint conserve sa DoD (Definition of Done). Chargée par load_context pour le sprint en cours.

**Re-déclenchement E2 (architecture, DoD (Definition of Done))** : Si `state.sprint_backlog.architectural_change = True` (champ Pydantic SprintBacklog, défaut `False`, positionné par R-3 (Scrum Master IA) ou forcé manuellement par R-1 (Product Owner) via H3 (validation Sprint Backlog)), sprint_complete met `needs_architecture_review = True` et boucle vers E2 (architecture, DoD (Definition of Done)) au lieu de E3 (Sprint Backlog).

---

##### P. Dashboard de statut multi-projets (status.py)

**Justification (F6 (status multi-projets))** : Avec plusieurs projets actifs en parallèle, un superviseur ne peut pas surveiller efficacement LangSmith + logs + handle_interrupt.py séparément pour chaque projet. Un script de statut unifié agrège toutes les informations critiques en une seule commande.

**Script `scripts/status.py`** — *à exécuter dans le **terminal intégré à VS Code*** :
- Signature : `python scripts/status.py [--project-id <id>] [--json]`
- Sans `--project-id` : affiche l'état de tous les projets listés dans `projects.json` (hors `archived: true`)
- Avec `--project-id` : vue détaillée d'un seul projet

**Informations affichées par projet** :

| Colonne | Source | Description |
|---------|--------|-------------|
| `project_id` | projects.json | Identifiant |
| `phase_courante` | Checkpointer | Dernier nœud exécuté (`sprint_number`, nœud LangGraph) |
| `interrupts_en_attente` | Checkpointer | Liste des H1 (validation Epic)–H6 (résolution conflit Git) non traités (thread_id, type, timestamp) |
| `derniere_indexation_rag` | `logs/index_rag_*.log` | Date/heure de la dernière indexation RAG (recherche sémantique) réussie |
| `pending_index` | `logs/pending_index.log` | Nombre de commits en attente d'indexation |
| `tokens_consommes_24h` | LangSmith API (optionnel) | Estimation consommation API (si `LANGCHAIN_API_KEY` défini) |
| `alertes` | `logs/pending_interrupts_alert.log` | Interrupts en attente > `AGILE_INTERRUPT_TIMEOUT_HOURS` |

**Variables** : `AGILE_PROJECTS_JSON` (chemin projects.json), `LANGCHAIN_API_KEY` (optionnel, pour métadonnées LangSmith).

**Exemple de sortie** :
```
PROJECT           PHASE           INTERRUPTS     LAST_INDEX     ALERTS
kanban            E4 (exécution code, sprint)/sprint-03    —              2h ago         —
api-meteo         H2 (validation Architecture + DoD) (attend)     H2 (validation Architecture + DoD) (18h)       5h ago         —
cli-tool          sprint-01       H1 (validation Epic) (52h!)      1j ago         ⚠ interrupt > 48h
```

setup_project_hooks.sh crée le script status.py dans le projet orchestration. Exécution manuelle ou via alias shell recommandé (alias agile-status pointant vers python et scripts/status.py).

---

##### Q. Structure nobles / opérationnels (lois Albert Core §3.4)

**Séparation stricte** : Les dossiers **nobles** (versionnés, source de vérité) : `/specs`, `/src`, `/docs`, `Architecture.md`, `Product Backlog.md`, ADRs (Architecture Decision Record). Les dossiers **opérationnels** (artefacts temporaires, logs, chroma local) : `/.operations` (artefacts IA, logs, chroma_db local au projet).

**Quarantaine des artefacts IA** : R-2 (System Architect IA) et R-4 (Dev Team IA) déposent les artefacts générés par l'IA en quarantaine (ex. `.operations/artifacts`) avant promotion. La promotion vers les nobles (commit dans `/src`, `/docs`) requiert la validation de R-1 (Product Owner) ou R-7 (Stakeholder). Documenter cette structure dans `specs/REGLES_AGENTS_AGILE.md`.

---

IV. Comptes de Services Cloud à Mettre en Place (Priorité Gratuit)

| Service | Compte | Free Tier (mars 2026) | Usage dans l'écosystème |
|---------|--------|------------------------|-------------------------|
| **Google AI Studio** | Compte Google | Gemini 2.5 Flash : 10 RPM, 250–500 RPD, 250K TPM | Fallback N1 (cloud gratuit) de la cascade |
| **Anthropic** | Compte API | Pay-as-you-go, pas d'abonnement minimum | Opus 4.6 / Sonnet 4.6 en dernier recours |
| **GitHub** | Compte personnel | 2000 min/mois Actions (privé), illimité (public) | CI/CD, dépôts, MCP (Model Context Protocol) |
| **LangSmith** | Compte free | 5000 traces/mois, 14 jours rétention | Traçage et débogage des workflows multi-agents (obligatoire pour production) |
| **Vercel** | Compte free | Déploiement frontend gratuit | À configurer uniquement si le projet livré est une application web frontend. Omettre pour librairies/CLI. |
| **Railway** | Compte free | Crédits mensuels limités | À configurer uniquement si le projet livré est une API backend à déployer. Omettre sinon. |

*Recommandation : privilégier les dépôts publics pour GitHub Actions illimité.*

#### 4.1 Checklist d'Installation (Ordre Recommandé)

1. **Ollama** : `curl -fsSL https://ollama.com/install.sh | sh` puis `ollama pull qwen2.5-coder:14b`, `ollama pull qwen2.5:14b`, `ollama pull nomic-embed-text`
   - Reco keep-alive (tous profils) : `export OLLAMA_KEEP_ALIVE=24h` (évite le déchargement après inactivité).
   - Reco warmup (E4/E5) : `ollama run qwen2.5-coder:14b "warmup"` (précharge le modèle prioritaire).
   - Legacy 12 Go (RTX 3060) : voir `docs/HARDWARE_GPU.md` + Simulation 014 (conflits VRAM/indexation).
2. **VS Code** : Installation standard
3. **Continue.dev** : Extension depuis le marketplace. Configurer Ollama (`http://localhost:11434`) et les modèles `qwen2.5-coder:14b`, `qwen2.5:14b` (option : `qwen3:14b` thinking). Modes manuel (choix explicite) ou routage automatique (LiteLLM) — voir `specs/plans/Plan_Configuration_VSCode_Ollama_Local.md`. Option RAG (recherche sémantique) partagé : configurer chroma-mcp dans Continue (mcpServers) et Roo Code (`.roo/mcp.json`) pour utiliser le même Chroma que les agents.
4. **Roo Code** : Extension depuis le marketplace. Même configuration Ollama. Modes manuel ou routage automatique (voir Plan_Configuration_VSCode_Ollama_Local.md).
5. **LangGraph + LangChain + Pydantic + Chroma** : pip install langgraph langchain langchain-ollama langchain-anthropic langchain-google-genai langchain-chroma pydantic chromadb. Créer le projet Python du graphe (III.5), configurer le checkpointer et le RAG (III.7, III.7-bis). État TypedDict : inclure dod, sprint_number, adr_counter, needs_architecture_review. Nœud load_context en entrée de thread. Voir III.8. Stratégie branches Git : feature depuis develop (III.8-D). Créer les scripts : handle_interrupt.py, index_rag.py, setup_project_hooks.sh, purge_checkpoints.py, export_chroma.py, import_chroma.py, notify_pending_interrupts.py, status.py (III.8-B, III.8-C, III.8-J, III.8-L, III.8-P). Créer graph/anonymizer.py, specs/REGLES_ANONYMISATION.md, config/anonymisation.yaml (III.5-ter L-ANON). Créer specs/REGLES_AGENTS_AGILE.md, graph/laws.py (lois Albert Core). Créer projects.json (format III.8-G). Variable AGILE_PROJECTS_JSON. API_429_MAX_RETRIES=3. GitHub Actions sur pull_request (III.8-F). Checklist de clôture (III.8-M). Voir III.8.
6. **chroma-mcp** (optionnel, pour RAG (recherche sémantique) partagé IDE) : `uvx chroma-mcp` ou `pip install chroma-mcp`. Configurer pour pointer vers la même Chroma que index_rag (client persistent ou HTTP). Ajouter à Continue (mcpServers), Roo Code (`.roo/mcp.json`) ou Cursor (`~/.cursor/mcp.json`) pour que l'IDE utilise le même RAG (recherche sémantique) que les agents. Voir III.7-bis.
6bis. **SearXNG** (optionnel, recherche web temps réel pour agents) : Conteneur `searxng/searxng` dans docker-compose, config format JSON. Intégration LangChain : `SearxSearchWrapper` passé aux nœuds R-2, R-4, R-6. Voir III.7-ter et `specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md` section 9.
6ter. **Microsoft Presidio** (optionnel, anonymisation via LiteLLM) : Moteur NLP pour masking/unmasking des prompts. Si LiteLLM est utilisé comme proxy : intégration Presidio pour flux bidirectionnel transparent. Voir III.5-ter option B et Strategie_Routage §10.
7. **LangSmith** : Compte sur https://smith.langchain.com. Clé API à définir dans `LANGCHAIN_TRACING_V2=true` et `LANGCHAIN_API_KEY=...` pour traçage.
8. **Google AI Studio** : Clé API sur https://aistudio.google.com. Provider de fallback N1 (cloud gratuit).
9. **Anthropic** : Clé API sur https://console.anthropic.com pour Opus/Sonnet en dernier recours.
10. **GitHub** : Compte + dépôt public (Actions illimité).
11. **GitHub CLI** : `gh` — `sudo apt install gh` puis `gh auth login` (une seule fois). Requis pour CI 1 (feature→develop)/CI 2 (develop→main) (`gh pr create`, `gh pr checks`). Requis pour CI 1 (feature→develop)/CI 2 (develop→main) (III.8-F).
12. **Docker** : Pour isolation des tests.
13. **Vercel / Railway** : Uniquement si le projet livré requiert un déploiement web (frontend ou API).

---

V. Les Flux Complets du Cycle de Vie (La Bascule Agile)

🛡️ **RÈGLE D'OR DE SÉCURITÉ ET DE CONFIDENTIALITÉ**

Avant toute escalade d'une tâche vers le Cloud (Gemini, Google AI Studio ou Claude API), le système ou l'opérateur doit garantir l'anonymisation absolue des données. **Il est formellement et absolument interdit d'envoyer des données privées, des informations confidentielles, des secrets industriels ou des clés d'API à une IA du Cloud.** Seul le contexte structurel anonymisé quitte la machine locale.

#### 5.0 Processus amont — De l'idée à l'Epic

Avant d'entrer dans le cycle Agile (sprints, program increment), un **processus amont** de Product Discovery transforme opportunités et idées en Epic validé :

1. **Discovery** — Exploration du problème, des utilisateurs, recherche, vision produit.
2. **Ideation** — le Product Owner et le Business Analyst IA échangent : hypothèses, proposition de valeur, opportunité.
3. **Cristallisation** — Albert (Business Analyst) structure l'initiative en Epic (cahier des charges, critères de haut niveau).
4. **Validation de l'Epic** — le Product Owner valide l'Epic (interrupt H1) avant injection dans le Product Backlog.

L'Epic validé est l'entrée du cycle E2 (Architecture) puis E3 (Sprint Backlog) et des sprints.

#### 5.1 PHASE 0 : La Fondation (Epic — hors cycle Agile)

Cette phase préliminaire se déroule en dehors de la rigueur et du coût du cycle Agile.

| Étape | Acteur | Input | Outil / Modèle | Livrable |
|-------|--------|-------|----------------|----------|
| Discovery & Ideation | R-1 (Nghia (Product Owner)) (humain) + R-0 (Albert Business Analyst) (IA) | Idée initiale, hypothèses | Cascade : qwen2.5:14b → Gemini 2.5 Flash (Web/API) → Opus 4.6 | Notes de Discovery |
| Cristallisation | R-0 (Albert Business Analyst) (IA) | Notes de Discovery | Idem | **Epic initial mature** (Epic) |

*Règle : privilégier qwen2.5:14b en local. Escalade uniquement si blocage ou limite 429. **H1 (validation Epic)** : R-1 (Nghia (Product Owner)) valide l'Epic avant passage en Phase 1.*

**Guide utilisateur** : Pour le guide pas-à-pas d'initiation d'un nouveau projet (déclaration dans projects.json, indexation RAG, lancement E1, validation des interrupts), voir specs/plans/Implementation_Ecosysteme_Agile_Calypso.md — section "Guide utilisateur basique — Initier un projet de développement".

#### 5.2 PHASE 1 à N : L'Usine Agile — Flux Détaillés et Livrables

| Étape | Acteur | Input | Outil / Modèle | Livrable | Qui délivre quoi | Human-in-the-Loop |
|-------|--------|-------|----------------|----------|------------------|-------------------|
| **E1 (idéation, Epic) – Initialisation** | R-1 (Nghia (Product Owner)) | Epic | VS Code, Continue.dev, `index_rag.py` | **Besoins - Product Backlog.md** | R-1 (Nghia (Product Owner)) injecte l'Epic validé (H1 (validation Epic)) dans le Backlog. Indexation RAG (recherche sémantique) (Backlog) déclenchée. Continue.dev indexe la codebase. | **H1 (validation Epic)** : R-1 (Nghia (Product Owner)) valide l'Epic avant E1 (idéation, Epic) |
| **E2 (architecture, DoD (Definition of Done)) – Backlog Refinement** | R-2 (Albert System Architect) | Backlog, Epic | Cascade : qwen2.5:14b → AI Studio → Opus 4.6 | **Architecture.md**, **DoD (Definition of Done)** (draft), **ADR (Architecture Decision Record)-{NNN}** | R-2 (Albert System Architect) produit Architecture.md + draft DoD (Definition of Done) (Pydantic) + ADR (Architecture Decision Record) (compteur adr_counter). Payload H2 (validation Architecture + DoD (Definition of Done)) : Architecture.md + draft DoD (Definition of Done). R-1 (Nghia (Product Owner)) amende DoD (Definition of Done), R-7 (Nghia (Stakeholder)) valide. Indexation RAG (recherche sémantique) (architecture + dod). BaseStore (mémoire long terme) : architecture_approved + DoD (Definition of Done). Si rejected : relance R-2 (Albert System Architect) avec feedback (max 3 cycles). Voir III.8-B et III.8-O. | **H2 (validation Architecture + DoD (Definition of Done))** : R-7 (Nghia (Stakeholder))/R-1 (Nghia (Product Owner)) valident architecture et finalisent DoD (Definition of Done) |
| **E3 (Sprint Backlog) – Sprint Planning** | R-3 (Albert Scrum Master) | Backlog, Architecture.md, DoD (Definition of Done) | Cascade : qwen2.5-coder:14b → AI Studio → Sonnet 4.6 | **Sprint Backlog** | R-3 (Albert Scrum Master) découpe en micro-tâches. Priorité local. Si rejected : relance R-3 (Albert Scrum Master) avec feedback (max 3 cycles). Voir III.8-B. | **H3 (validation Sprint Backlog)** : R-1 (Nghia (Product Owner)) valide le découpage avant E4 (exécution code, sprint) |
| **E4 (exécution code, sprint) – Sprint Execution** | R-4 (Albert Dev Team), R-5 (Albert Release Manager) | Sprint Backlog, DoD (Definition of Done) | LangGraph (nœuds R-4 (Albert Dev Team), R-5 (Albert Release Manager)) + tools (read_file, write_file, run_shell) | Code source, tests unitaires, feature branch | R-4 (Albert Dev Team) génère le code via tools. R-5 (Albert Release Manager) gère Git. Automatique. Hook post-commit : différé si AGILE_DEFER_INDEX=true (pending_index.log). En cas de conflit Git : H6 (résolution conflit Git). Voir III.8-C. | — |
| **E5 (tests, CI local) – CI/CD Pipeline (local)** | R-6 (Albert QA & DevOps) | Code, DoD (Definition of Done) | Docker, Jest/Pytest, Linters, Sphinx/JSDoc + Cascade | **Test Reports**, verdict Pass/Fail | R-6 (Albert QA & DevOps) exécute build_docs puis tests locaux. Self-Healing R-6 (Albert QA & DevOps)→R-4 (Albert Dev Team) si échec (max 3). CI vert → déclenche H4 (Sprint Review, CI verts). GitHub Actions = CI de validation PR (avant merge main). Voir III.8-F et III.8-N. | **H4 (Sprint Review, CI verts)** : CI vert déclenche H4 (Sprint Review, CI verts) (Sprint Review R-7 (Nghia (Stakeholder))). **H5 (approbation escalade API payante)** si escalade N2 (cloud payant). |
| **E6 (clôture sprint, merge) – Sprint Review & Retrofit** | R-7 (Nghia (Stakeholder)) | Incrément, DoD (Definition of Done) | VS Code, Continue.dev | **Go/No-Go**, mise à jour Backlog | E6 (clôture sprint, merge) = phase post-H4 (Sprint Review, CI verts). R-7 (Nghia (Stakeholder)) prononce Go/No-Go (via H4 (Sprint Review, CI verts) resume). Si rejected : nouveau cycle E4 (exécution code, sprint)→E5 (tests, CI local). Si approved : Retrofit Backlog (R-1 (Nghia (Product Owner))). Nœud sprint_complete : sprint_summary, sprint_number++, index_rag (traite pending_index.log si AGILE_DEFER_INDEX). Si auto_next_sprint : boucle E3 (Sprint Backlog). Voir III.8-E et III.8-M. | — (H4 (Sprint Review, CI verts) géré en E5 (tests, CI local)) |

###

* * *

Annexe A. Cartographie Financière et Technique de l'Écosystème

Cette cartographie répertorie les technologies selon leur impact financier, validant le modèle de déploiement "Cascade".

#### 🖥️ 1. Local & Gratuit (L'Infrastructure de Base & Exécution)

L'arsenal qui tourne sur votre machine, maximisant la rentabilité de votre matériel (0€ au-delà de l'électricité).

* **GPU NVIDIA (référence actuelle : RTX 5060 Ti 16G) :** Le cœur matériel de l'usine, offrant la VRAM nécessaire pour l'exécution d'IA locale (modèles Q4) sans latence réseau, sans coût par token, et avec une confidentialité absolue à 100%. *Legacy 12 Go (RTX 3060) : voir Simulation 014 + `docs/HARDWARE_GPU.md`.*
* **Ollama :** Moteur d'exécution des LLMs locaux. Modèles installés : `qwen2.5-coder:14b` (code) et `qwen2.5:14b` (idéation/architecture).
* **LangGraph + LangChain** : Backbone d'orchestration des agents. Voir section III.5.
* **Git & MCP (Model Context Protocol) :** Contexte structuré de la codebase. chroma-mcp pour RAG (recherche sémantique) partagé agents + IDE (voir III.7-bis).
* **Chroma + nomic-embed-text :** RAG (recherche sémantique) pour les agents (codebase, Architecture.md, Backlog, ADRs). Mémoire long terme via LangGraph BaseStore (mémoire long terme). Voir III.7.
* **Docker, Jest/Pytest, GitHub Actions :** Isolation, tests, CI/CD.

#### 💻 2. Local & Gratuit (L'Interface de Pilotage Open-Source)

L'interface de travail remplaçant les abonnements mensuels fixes (ex: Cursor).

* **VS Code + Continue.dev + Roo Code :** Cockpit central (Hub ENV-B). Continue.dev : autocomplétion alimentée par Ollama (GPU local). Roo Code : agents d'exécution autonomes. Deux modes : **manuel** (choix explicite du modèle) ou **routage automatique** (proxy LiteLLM, routage par tâche + cascade local→Gemini→Claude). **0€/mois** (hors API cloud si utilisées).

#### ☁️ 3. Cloud & Gratuit (La Maturation et le Fallback)

* **Google AI Studio (Free Tier API) :** Modèles `gemini-2.5-flash` ou `gemini-2.5-flash-lite`. Fallback Niveau 1 (N1 (cloud gratuit)) de la cascade. Limites : 10 RPM, 250–500 RPD, 250K TPM.
* **LangSmith (Free Tier) :** 5000 traces/mois, rétention 14 jours. Traçage obligatoire des workflows LangGraph pour débogage et optimisation.
* _Règle d'intégration :_ Exponential Backoff obligatoire sur **HTTP 429** pour absorber les limites du Free Tier.

#### 🌩️ 4. Cloud & Pay-as-you-go (L'Expertise Critique en Ultime Recours)

* **API Claude Opus 4.6 :** Décisions d'architecture majeures (R-2 (Albert System Architect)). ~5 $/M tokens input, ~25 $/M output.
* **API Claude Sonnet 4.6 :** Exécution complexe (R-4 (Albert Dev Team), R-6 (Albert QA & DevOps)). ~3 $/M input, ~15 $/M output. Utiliser le Prompt Caching pour réduire les coûts.

---

VI. Stratégies d'Optimisation des Coûts et des Ressources

| Stratégie | Description | Impact |
|-----------|-------------|--------|
| **Étalement des tâches** | Répartir les appels API sur la journée pour respecter les limites RPD (ex. Gemini 250–500 req/jour). Éviter les pics de consommation. | Réduction des 429, pas de surcoût cloud |
| **Prompt Caching (Anthropic)** | Réutiliser les contextes longs (Architecture.md, Backlog) via le cache. Cached reads : ~90 % de réduction sur Opus/Sonnet. | Jusqu'à 50 % d'économie sur les gros contextes |
| **Batch API (Anthropic)** | Regrouper les tâches non bloquantes (analyse de logs, génération de rapports, revues de code) et les soumettre en batch : 50 % de réduction. Utiliser systématiquement pour tout appel N2 (cloud payant) non synchrone. | Jusqu'à 50 % d'économie sur Opus/Sonnet |
| **Anonymisation systématique** | Avant toute escalade cloud : supprimer secrets, données personnelles, chemins locaux. Envoyer uniquement des structures anonymisées. | Confidentialité + évite les fuites |
| **Seuils d'escalade stricts** | N0 (local Ollama)→N1 (cloud gratuit) : après 2 échecs consécutifs ou HTTP 429. N1 (cloud gratuit)→N2 (cloud payant) : après 1 échec N1 (cloud gratuit) ou complexité > 500 lignes de contexte. H5 (approbation escalade API payante) obligatoire avant tout appel N2 (cloud payant) : approbation humaine. | Réduction des appels Opus/Sonnet, contrôle des coûts |
| **Backoff HTTP 429** | 3 tentatives max, backoff exponentiel (2^attempt s). Si 429 persiste : H5 (approbation escalade API payante) (approbation N2 (cloud payant)) ou "pause et retry demain". Variable `API_429_MAX_RETRIES=3`. Voir III.10 (S6). | Résilience face aux quotas Free Tier |
| **Tests et lint locaux en priorité** | R-6 (Albert QA & DevOps) exécute Jest/Pytest en local. L'IA ne sert qu'à l'analyse des logs en cas d'échec. | 0 € pour la majorité des cycles |
| **Dépôts publics GitHub** | Utiliser des dépôts publics pour GitHub Actions : minutes illimitées gratuites. | 0 € CI/CD |
| **Contexte minimal** | Limiter la taille du contexte envoyé aux API (extraits pertinents, pas la codebase complète). | Moins de tokens = moins de coût |

---

VII. Exigences Transversales : Testabilité, Tracabilité, Modularité

| Exigence | Implémentation | Acteur / Outil |
|----------|----------------|----------------|
| **Testabilité by design** | TDD obligatoire : tests écrits avant ou avec le code. Couverture minimale définie dans la DoD (Definition of Done). | R-4 (Albert Dev Team), R-6 (Albert QA & DevOps) (QA) |
| **Tracabilité** | Chaque ticket lié à un commit ; Architecture.md et Backlog versionnés dans Git. ADRs (Architecture Decision Records) obligatoires pour toute décision impactant l'architecture : traçabilité des choix, justifications, et alternatives écartées. | R-5 (Albert Release Manager), R-2 (Albert System Architect) (Architecte), Git |
| **Journalisation** | Logs structurés (JSON) dans les pipelines CI/CD. Conservation des outputs IA (prompts/réponses) pour audit et amélioration. | R-6 (Albert QA & DevOps), GitHub Actions, fichiers `logs/` |
| **Tests end-to-end** | Suite E2 (architecture, DoD (Definition of Done))E obligatoire pour projets web : **Playwright** (recommandé, multi-navigateur, stable). Déclenchée avant merge. Définie dans la DoD (Definition of Done). Pour projets non-web : tests d'intégration (Pytest, Jest) suffisants. | R-6 (Albert QA & DevOps), pipeline CI |
| **Documentation** | README, Architecture.md, DoD (Definition of Done) à jour. DoD (Definition of Done) co-construite en H2 (validation Architecture + DoD (Definition of Done)) : R-2 (Albert System Architect) draft + R-1 (Nghia (Product Owner)) amende + R-7 (Nghia (Stakeholder)) valide), versionnée dans Git et BaseStore (mémoire long terme). Génération auto : **JSDoc** (JS/TS) ou **Sphinx** (Python). build_docs dans E5 (tests, CI local) par R-6 (Albert QA & DevOps). Checklist de clôture (III.8-M). Voir III.8-B (DoD (Definition of Done)/H2 (validation Architecture + DoD (Definition of Done))) et III.8-N (build_docs). | R-2 (Albert System Architect) (DoD (Definition of Done) draft, ADRs), R-1 (Nghia (Product Owner)) (amende DoD (Definition of Done)), R-7 (Nghia (Stakeholder)) (valide), R-6 (Albert QA & DevOps) (E5 (tests, CI local)) |
| **Modularité** | Découpage en modules/bibliothèques réutilisables. Architecture.md impose les frontières. | R-2 (Albert System Architect) (Architecture), R-4 (Albert Dev Team) (implémentation) |

---

VIII. Rapports de Simulation

**Objectif** : Les simulations permettent de valider l'écosystème sur plusieurs semaines, d'identifier les problèmes et manques, puis d'intégrer les corrections. Chaque rapport est numéroté et daté pour permettre des itérations successives.

| Numéro | Date | Fichier | Corrections intégrées |
|--------|------|---------|------------------------|
| **001** | 2026-03-01 | `specs/Simulation_001_2026-03-01.md` | Procédures H1 (validation Epic)–H6 (résolution conflit Git), pipeline indexation RAG (recherche sémantique), articulation E4 (exécution code, sprint) (LangGraph + tools), seuil Self-Healing (3), flux BaseStore (mémoire long terme), stratégie GPU, politique LangSmith, politique rétention (section III.8) |
| **002** | 2026-03-02 | `specs/Simulation_002_2026-03-02.md` | R1–R5, N1 (cloud gratuit)–N2 (cloud payant) intégrés (section III.9) : handle_interrupt --thread-id, nœuds post_h1/post-H2 (validation Architecture + DoD (Definition of Done))/post-H4 (Sprint Review, CI verts), index_rag emplacement/paramètres, project_root/project_id dans état, multi-projets, résilience index_rag. |
| **003** | 2026-03-03 | `specs/Simulation_003_2026-03-03.md` | S1–S12 intégrés (section III.10). |
| **004** | 2026-03-04 | `specs/Simulation_004_2026-03-04.md` | T1–T8 intégrés (section III.11). |
| **005** | 2026-03-05 | `specs/Simulation_005_2026-03-05.md` | Validation T1–T8. Convergence déclarée — réexaminée par Sim 006. |
| **006** | 2026-03-06 | `specs/Simulation_006_2026-03-06.md` | U1–U8 intégrés (section III.12) : DoD (Definition of Done)/H2 (validation Architecture + DoD (Definition of Done)) flux, branches rejected H1 (validation Epic)–H4 (Sprint Review, CI verts), indexation différée GPU (AGILE_DEFER_INDEX), H4 (Sprint Review, CI verts) trigger clarifié, numérotation ADRs, sprint_number état TypedDict, GitHub Actions vs R-6 (Albert QA & DevOps), clôture projet. |
| **007** | 2026-03-07 | `specs/Simulation_007_2026-03-07.md` | V1–V7 intégrés (section III.13) : payload H5 (approbation escalade API payante) reason, nœud load_context, re-déclenchement E2 (architecture, DoD (Definition of Done)), stratégie branches Git (feature/sprint+develop+main), H4 (Sprint Review, CI verts) après H5 (approbation escalade API payante) clarifié, DoD (Definition of Done) versionnée par sprint, H4 (Sprint Review, CI verts)-rejected cycle correctif. |
| **008** | 2026-03-08 | `specs/Simulation_008_2026-03-08.md` | W1–W6 intégrés (section III.14) : start_phase E1 (idéation, Epic)/E3 (Sprint Backlog), architectural_change Pydantic, DoD (Definition of Done) fallback sprint N-1, H4 (Sprint Review, CI verts) conditionné GitHub Actions, workflow hotfix, AGILE_PROJECTS_JSON. |
| **009** | 2026-03-09 | `specs/Simulation_009_2026-03-09.md` | X1–X4 intégrés (section III.15) : CI 1 (feature→develop) feature→develop / CI 2 (develop→main) develop→main, push unique fin E4 (exécution code, sprint), polling GitHub Actions via gh run watch (GITHUB_ACTIONS_TIMEOUT), AGILE_BASESTORE_STRICT. |
| **010** | 2026-03-10 | `specs/Simulation_010_2026-03-10.md` | Y1–Y5 intégrés (section III.16) : branche develop init, gh pr create/checks, merge_to_main nœud, start_phase HOTFIX (correctif urgent), mode dégradé github_repo absent. |
| **011** | 2026-03-11 | `specs/Simulation_011_2026-03-11.md` | Z1–Z2 intégrés (section III.17) : sprint_complete en deux phases (sprint_summary puis merge_to_main avec incrément sprint_number après CI 2 (develop→main)), branch protection GitHub documentée. |
| **012** | 2026-03-12 | `specs/Simulation_012_2026-03-12.md` | AA1–AA2 intégrés (section III.18) : sprint_number mode dégradé (incrément phase 1 si github_repo absent), suppression notation H4 (Sprint Review, CI verts)' (→ H5 (approbation escalade API payante) reason=pr_review_required), catalogue complet reasons H5 (approbation escalade API payante). Convergence définitive atteinte. |
| **013** | 2026-03-13 | `specs/Simulation_013_2026-03-13.md` | BB1–BB4 intégrés (section III.19) : numérotation checklist, W5 start_phase HOTFIX (correctif urgent), hotfix→develop merge direct, auto_next_sprint boucle après phase 2. **Convergence définitive — zéro problème résiduel.** |
| **014** | 2026-03-14 | `specs/Simulation_014_2026-03-14.md` | CC1–CC3 (RTX 3060 12 Go) : OLLAMA_KEEP_ALIVE checklist, Continue.dev pendant E4 (exécution code, sprint)/E5 (tests, CI local), AGILE_DEFER_INDEX recommandation explicite. Validation flux sous contrainte VRAM. |

**Règle** : Simulations 001–014 validées et intégrées. Corrections consolidées en III.8. Historique détaillé en Annexe B. Spec **convergé et opérationnel** — prêt pour implémentation.


---

### Annexe B. Historique des Corrections par Simulation (001–013)

*Cette annexe conserve l'intégralité des listes de corrections incrémentales issues des simulations 001 à 014. Elle constitue la traçabilité complète des décisions de conception. Le document opérationnel de référence est la section III.8.*


#### B.1 Corrections Simulation 001 — Procédures opérationnelles initiales

*Source : Simulation_001_2026-03-01.*

**Procédure Human-in-the-Loop (interrupts H1 (validation Epic)–H6 (résolution conflit Git))** :
- Utiliser le endpoint LangServe `/playground` ou le script `scripts/handle_interrupt.py [--thread-id <id>]`. Si `--thread-id` est omis et plusieurs interrupts sont en attente : le script liste les threads **triés par project_id puis par type H (H1 (validation Epic) avant H2 (validation Architecture + DoD (Definition of Done))…)** — ou par timestamp — et demande de choisir. Si `--thread-id` est fourni mais le thread n'a pas d'interrupt en attente : message d'erreur explicite, exit code 1 (voir III.10 S1, III.11 T8). Puis : (1) lit l'état du graphe via l'API, (2) affiche le payload `__interrupt__`, (3) attend l'entrée (approved | rejected | feedback), (4) envoie `graph.invoke(Command(resume=...), config)`. Voir III.9 (R1).
- En absence de l'humain : le graphe reste en attente. Option "rejeter avec report" : `resume={"status":"rejected","resume_after":"2026-03-05"}` pour programmer une reprise différée. Notification optionnelle (email, script) si un interrupt reste non traité > 48h.
- **H6 (résolution conflit Git) (nouveau)** : Si R-5 (Albert Release Manager) échoue à résoudre un conflit Git après 2 tentatives → interrupt dédié. L'humain résout manuellement (VS Code, `git mergetool`), commit, puis `Command(resume="resolved")` pour reprendre.

**Pipeline d'indexation RAG (recherche sémantique)** :
- Déclencheurs : (1) **Nœud post_h1** (après H1 (validation Epic) resume) : `run_shell(index_rag.py --project-root {state.project_root} --project-id {state.project_id} --sources backlog)`. **Ordre obligatoire** : R-1 (Nghia (Product Owner)) doit avoir injecté l'Epic dans le Backlog et committé *avant* d'envoyer `Command(resume)` sur H1 (validation Epic), sinon post_h1 indexe un fichier vide ou inexistant (voir III.11 T1). **Hook et E4 (exécution code, sprint)** : Si `AGILE_DEFER_INDEX=true` dans `.agile-env`, le hook post-commit ne lance pas index_rag immédiatement mais enregistre un fichier `logs/pending_index.log` (timestamp + commit hash). L'indexation est ensuite déclenchée par sprint_complete (fin E6 (clôture sprint, merge)), éliminant les conflits GPU pendant E4 (exécution code, sprint)/E5 (tests, CI local). Voir III.12 (U3). (2) **Nœud post-H2 (validation Architecture + DoD (Definition of Done))** : idem `--sources architecture` ; (3) **Nœud post-H4 (Sprint Review, CI verts)** : idem `--sources all` ; (4) **Hook Git** post-commit : lit `$AGILE_ORCHESTRATION_ROOT` et `$AGILE_PROJECT_ID` (ou fichier `.agile-project-id`), appelle `python $AGILE_ORCHESTRATION_ROOT/scripts/index_rag.py --project-root $(pwd) --project-id $AGILE_PROJECT_ID`. **Bootstrap** : `scripts/setup_project_hooks.sh` (voir III.10 S2, III.11 T2, T3).
- Script `index_rag.py` : vit dans le projet orchestration. Signature : `--project-root <path> --project-id <id> [--sources backlog|architecture|code|all] [--strict]`. Résilience : try/except par fichier, skip en erreur, rapport final écrit dans `logs/index_rag_<timestamp>.log`. Si `--strict` et aucun fichier indexé avec succès : exit 1. Alerte si > 10 % de fichiers en erreur : log warning. Voir III.9 (R3, N2 (cloud payant)), III.10 (S5, S7).

**Articulation E4 (exécution code, sprint) : LangGraph pilote, tools filesystem/Git** : E4 (exécution code, sprint) est piloté par le nœud R-4 (Albert Dev Team) du graphe LangGraph. R-4 (Albert Dev Team) dispose de tools : `read_file`, `write_file`, `run_shell` (git, npm, etc.). Roo Code et Continue.dev restent l'interface humaine pour inspections et corrections manuelles ; le graphe n'attend pas de callback Roo Code. R-4 (Albert Dev Team) traite les tickets séquentiellement, écrit le code via `write_file`, et R-5 (Albert Release Manager) (nœud graphe) appelle `run_shell` pour git. Pour les tâches de code interactif (pair programming), Nghia peut utiliser Roo Code en dehors du flux automatisé.

**Seuil Self-Healing** : Configuration fixe : `SELF_HEALING_MAX_ITERATIONS = 3`. Au-delà de 3 cycles R-6 (Albert QA & DevOps)→R-4 (Albert Dev Team) sans succès → interrupt H5 (approbation escalade API payante) (approbation humaine pour escalade N2 (cloud payant) ou arrêt avec rapport d'échec).

**Stratégie GPU (Ollama)** : Un seul modèle chargé à la fois. Ordre de priorité : qwen2.5-coder (E4 (exécution code, sprint), E5 (tests, CI local)) > gemma3 (E0, E2 (architecture, DoD (Definition of Done))). Configurer `OLLAMA_KEEP_ALIVE` pour le modèle prioritaire du flux en cours. Éviter d'exécuter des indexations RAG (recherche sémantique) massives (nomic-embed-text) pendant E4 (exécution code, sprint)/E5 (tests, CI local) ; lancer l'indexation en fin de journée ou entre sprints.

**Politique de traçage LangSmith** : En cas de risque de dépassement 5000 traces/mois : configurer `LANGCHAIN_TRACING_SAMPLING_RATE=0.2` (20 % des runs) ou `LANGCHAIN_TRACING_ERRORS_ONLY=true` pour tracer uniquement les échecs. Priorité : conserver les traces des runs en erreur pour débogage.

**Politique de rétention** : Purge des checkpoints > 90 jours (script `scripts/purge_checkpoints.py`). Critères : "90 jours" = dernier step du thread. **Exclure** les threads ayant un `__interrupt__` non résolu. Signature : `purge_checkpoints.py [--dry-run] [--max-age-days 90]`. Voir III.10 (S8). Chroma : une collection par projet ; archiver (export) avant suppression. Procédure : `scripts/export_chroma.py --project-id <id> --output <path>` et `import_chroma.py` pour réimport. Limite logs : rotation 7 jours, max 100 Mo.

#### B.2 Corrections Simulation 002 (R1–R5, N1 (cloud gratuit)–N2 (cloud payant))

*Les éléments ci-dessous proviennent du rapport Simulation_002_2026-03-02 et corrigent les problèmes résiduels et nouveaux identifiés.*

**R1 — handle_interrupt.py : identification du thread_id**  
*Problème* : Lorsque plusieurs projets ou sprints ont un interrupt en attente, le script ne sait pas quel thread traiter.  
*Correction* : `handle_interrupt.py` accepte l'argument optionnel `--thread-id <id>`. S'il est omis, le script interroge l'API LangServe pour lister les threads dont l'état contient `__interrupt__`, affiche la liste (thread_id, type H1 (validation Epic)–H6 (résolution conflit Git), timestamp), et demande à l'utilisateur de choisir. Justification : permet de gérer plusieurs projets en parallèle sans confusion.

**R2 — Mécanisme de déclenchement indexation à E1 (idéation, Epic)**  
*Problème* : E1 (idéation, Epic) est une action humaine (R-1 (Nghia (Product Owner)) injecte le Backlog). L'indexation "Fin E1 (idéation, Epic)" n'était pas rattachée à un mécanisme explicite.  
*Correction* : Deux déclencheurs complémentaires. (1) **Hook Git post-commit** : lorsque le Backlog est committé, le hook lance `index_rag.py --project-root $(pwd) --project-id <id>`. (2) **Nœud graphe "post_h1"** : après `Command(resume=...)` sur H1 (validation Epic), un nœud exécute `run_shell(index_rag.py ...)` pour indexer le Backlog avant de passer à E2 (architecture, DoD (Definition of Done)). Le nœud post_h1 garantit l'indexation même si le hook Git n'est pas configuré. Justification : redondance pour fiabilité ; le hook couvre les mises à jour ultérieures du Backlog.

**R3 — Emplacement et paramètres de index_rag.py**  
*Problème* : Emplacement du script (orchestration vs projet) et paramètres non spécifiés.  
*Correction* : Le script vit dans le **projet orchestration** (répertoire du graphe LangGraph). Signature : `python scripts/index_rag.py --project-root <path> --project-id <id> [--sources backlog|architecture|code|all]`. `--project-root` : chemin absolu du projet cible (ex. dépôt kanban). `--project-id` : identifiant pour la collection Chroma (ex. `kanban`, `api-meteo`). `--sources` : limite l'indexation (défaut `all`). Justification : un seul script, réutilisable pour tous les projets ; les chemins sont passés explicitement, pas de configuration implicite.

**R4 — Ordre des opérations post-H2 (validation Architecture + DoD (Definition of Done)) et post-H4 (Sprint Review, CI verts)**  
*Problème* : Ordre flou entre écriture BaseStore (mémoire long terme), indexation et reprise du graphe.  
*Correction* : Pour tout interrupt H2 (validation Architecture + DoD (Definition of Done)), H4 (Sprint Review, CI verts) (et H1 (validation Epic)), le nœud qui reçoit le `resume` exécute dans cet ordre : (1) mise à jour de l'état avec le feedback utilisateur ; (2) écriture en BaseStore (mémoire long terme) si applicable (H2 (validation Architecture + DoD (Definition of Done)) → architecture_approved, H4 (Sprint Review, CI verts) → sprint_summary) ; (3) appel à `index_rag.py` avec les sources pertinentes ; (4) transition vers le nœud suivant. Justification : garantit que la mémoire et le RAG (recherche sémantique) sont à jour avant que le flux ne reprenne.

**R5 — project_root et project_id dans l'état du graphe**  
*Problème* : Les nœuds R-4 (Albert Dev Team), R-5 (Albert Release Manager) et les tools doivent connaître le chemin du projet.  
*Correction* : L'état TypedDict inclut obligatoirement `project_root: Path` et `project_id: str`. Initialisation : à l'entrée du flux (Phase 0 ou E1 (idéation, Epic)), l'invocation du graphe reçoit en config `{"configurable": {"thread_id": "...", "project_root": "/path/to/projet", "project_id": "kanban"}}`. Ces valeurs sont injectées dans l'état initial. Les tools `read_file`, `write_file`, `run_shell` utilisent `project_root` comme répertoire de travail. Justification : évite les chemins en dur ; un même graphe peut traiter plusieurs projets.

**N1 (cloud gratuit) — Gestion multi-projets**  
*Problème* : Plusieurs projets en parallèle : project_id, project_root, handle_interrupt.  
*Correction* : Convention `thread_id` : `{project_id}-phase-0` (Phase 0) ou `{project_id}-sprint-{NN}` (sprint N, padding 2 chiffres : 01, 02, …). Exemples : `kanban-phase-0`, `kanban-sprint-01`, `api-meteo-sprint-02`. Voir III.11 (T5). Une config `projects.json` associe `project_id` → `path` (et optionnellement `auto_next_sprint`). Format : `{"kanban": {"path": "/home/user/kanban", "auto_next_sprint": false}, "api-meteo": {"path": "..."}}`. `handle_interrupt.py` affiche les interrupts groupés par project_id. Justification : isolation, traçabilité, tri correct.

**N2 (cloud payant) — Résilience de index_rag.py**  
*Problème* : Un fichier ou un chunk problématique peut faire échouer toute l'indexation.  
*Correction* : Le script traite chaque fichier dans un try/except. En cas d'erreur sur un fichier (encoding, chunk trop long, embedding échoué) : log de l'erreur, skip du fichier, poursuite des autres. En fin d'exécution : rapport (fichiers indexés, fichiers en erreur, total). Option `--strict` : si aucun fichier n'a été indexé avec succès, exit code 1 (pour alerter les hooks). Justification : un fichier corrompu ou atypique ne bloque pas l'indexation du reste du projet ; le rapport permet de diagnostiquer.

#### B.3 Corrections Simulation 003 (S1–S12)

*Les éléments ci-dessous proviennent du rapport Simulation_003_2026-03-03 et corrigent les problèmes identifiés en conditions multi-projets et longue durée.*

**S1 — handle_interrupt.py : validation du thread_id**  
Si `--thread-id` est fourni mais le thread n'a pas d'interrupt en attente : message d'erreur explicite, exit code 1. Exit codes : 0=succès, 1=erreur (thread invalide, etc.), 2=usage (arguments invalides). Voir III.11 (T8).

**S2 — Bootstrap hooks Git pour nouveau projet**  
Script `scripts/setup_project_hooks.sh` : à exécuter lors de la création d'un nouveau dépôt. Signature : `--orchestration-root <path> --project-root <path> --project-id <id>`. Le script : (1) crée un fichier `.agile-project-id` à la racine du projet (contenu : project_id) ; (2) crée un fichier `.agile-env` ou configure le hook pour lire `AGILE_ORCHESTRATION_ROOT` et `AGILE_PROJECT_ID` au runtime (pas de chemin figé). Voir III.11 (T2, T3).

**S3 — Ordre d'affichage des interrupts**  
Quand `handle_interrupt.py` liste les threads sans `--thread-id`, tri par `project_id` puis par type H (H1 (validation Epic), H2 (validation Architecture + DoD (Definition of Done)), H3 (validation Sprint Backlog), H4 (Sprint Review, CI verts), H5 (approbation escalade API payante), H6 (résolution conflit Git)). Alternative : tri par timestamp (plus ancien en premier).

**S4 — Boucle E6 (clôture sprint, merge) → E3 (Sprint Backlog) pour le sprint N+1**  
Après E6 (clôture sprint, merge), le nœud "sprint_complete" : (a) écrit sprint_summary en BaseStore (mémoire long terme) (namespace `project/{id}/sprints`) et déclenche index_rag (ou traite `pending_index.log` si `AGILE_DEFER_INDEX=true`) ; (b) incrémente `state.sprint_number` et écrit la nouvelle valeur dans BaseStore (mémoire long terme) (`project/{id}/sprint_counter`) ; (c) consulte `projects.json` pour `projects[project_id].auto_next_sprint` (défaut : false). Si true : boucle vers E3 (Sprint Backlog) avec `thread_id={project_id}-sprint-{NN}` (N+1, padding 2 chiffres, calculé depuis `state.sprint_number`). **Timing** : la boucle E3 (Sprint Backlog) se déclenche après la phase 2 (merge_to_main complet, sprint_number incrémenté) ; en mode dégradé (github_repo absent), après la phase 1 (incrément immédiat). Voir III.19 (BB4). Si false : termine avec message pour invocation manuelle. Voir III.11 (T4, T5), III.12 (U6).

**S5 — Rapport index_rag consommé**  
Le script `index_rag.py` écrit son rapport dans `logs/index_rag_<timestamp>.log` (répertoire du projet orchestration). Le hook Git ou un wrapper peut rediriger stdout/stderr vers ce fichier. Permet un audit ultérieur.

**S6 — Backoff HTTP 429 et gestion quota**  
Stratégie retry sur HTTP 429 : 3 tentatives max, backoff exponentiel (2^attempt secondes). Configurer les connecteurs LangChain (Google, Anthropic) avec `max_retries=3` et backoff. Si 429 persiste après 3 retries : considérer "quota épuisé" → déclencher H5 (approbation escalade API payante) pour approbation N2 (cloud payant) (Sonnet/Opus) ou option "pause et retry demain". Variable `API_429_MAX_RETRIES=3`.

**S7 — Alerte sur échec index_rag**  
Si `index_rag.py` s'exécute avec `--strict` et exit 1 (aucun fichier indexé), ou si > 10 % des fichiers sont en erreur : écrire une entrée dans `logs/index_errors.log` avec timestamp, project_id, nombre d'erreurs. Option : notification (email, script) si ce fichier est consulté par un cron de monitoring.

**S8 — Purge checkpoints : critères détaillés**  
Script `purge_checkpoints.py` : `--max-age-days 90` (défaut), `--dry-run` (affiche sans supprimer). "90 jours" = date du dernier step du thread. **Exclure** les threads dont l'état contient `__interrupt__` (interrupt non traité). Log des threads supprimés.

**S9 — Rétention traces LangSmith**  
Rétention 14 jours (free tier). Pour audit long terme : option d'export périodique via API LangSmith vers stockage local (fichiers JSON) ou S3. Script `scripts/export_langsmith_traces.py` (optionnel, hors scope minimal). Documenter que la rétention courte est assumée.

**S10 — Archivage Chroma**  
Scripts `scripts/export_chroma.py --project-id <id> --output <path>.json` et `scripts/import_chroma.py --project-id <id> --input <path>.json`. Format : export JSON des vecteurs et métadonnées. Avant suppression d'un projet : exporter, puis supprimer la collection. Pour réactiver : importer.

**S11 — Sync Architecture.md et artefacts**  
Nœud optionnel "sync_artifacts" ou tâche cron : compare le code (structure des modules) à Architecture.md et génère un rapport de dérive. R-2 (Albert System Architect) produit un ADR (Architecture Decision Record) à la fin de E2 (architecture, DoD (Definition of Done)) pour les décisions d'architecture via template Pydantic ; numérotation : `ADR (Architecture Decision Record)-{NNN}-{date}-{slug}.md` où NNN provient du compteur `adr_counter` (état TypedDict, incrémenté par R-2 (Albert System Architect)). Voir III.12 (U5). Projets terminés dans `projects.json` : flag `"archived": true` pour les garder en référence sans les traiter comme actifs.

**S12 — Génération documentation (Sphinx/JSDoc)**  
Étape "build_docs" dans E5 (tests, CI local), avant les tests : R-6 (Albert QA & DevOps) exécute `sphinx-build` (Python) ou `npm run docs` (JS/TS). Si pas de `conf.py` (Python) ou `jsdoc.json` (JS/TS) : skip avec log. Variable `BUILD_DOCS_REQUIRED=false` (défaut) : si true, échec bloque. Voir III.11 (T6).

#### B.4 Corrections Simulation 004 (T1–T8)

*Les éléments ci-dessous proviennent du rapport Simulation_004_2026-03-04 et corrigent les derniers problèmes résiduels.*

**T1 — Ordre H1 (validation Epic) / E1 (idéation, Epic) / post_h1**  
R-1 (Nghia (Product Owner)) doit injecter l'Epic dans `Besoins - Product Backlog.md` et committer *avant* d'envoyer `Command(resume="approved")` sur H1 (validation Epic). Sinon, post_h1 indexe un fichier inexistant ou vide. Procédure : (1) valider l'Epic (H1 (validation Epic) affiché), (2) créer le dépôt projet si besoin, (3) créer le fichier Backlog avec le contenu du Epic, (4) commit, (5) lancer handle_interrupt et envoyer resume.

**T2 — project_id dans le hook**  
Le hook ne doit pas utiliser `$(basename $(pwd))` (peut différer de projects.json). Utiliser un fichier `.agile-project-id` à la racine du projet (contenu : project_id sur une ligne), ou la variable `AGILE_PROJECT_ID` définie par setup_project_hooks. setup_project_hooks reçoit `--project-id <id>` et écrit ce fichier ou configure l'env.

**T3 — ORCHESTRATION_ROOT non figé**  
Le hook lit `$AGILE_ORCHESTRATION_ROOT` au moment de l'exécution (pas de chemin absolu figé). setup_project_hooks crée un wrapper qui exporte cette variable avant d'appeler index_rag. Ou : fichier `.agile-env` à la racine du projet avec `AGILE_ORCHESTRATION_ROOT=/path`. Ce fichier est généré par setup_project_hooks.

**T4 — Config auto_next_sprint**  
Format `projects.json` étendu : `{"<project_id>": {"path": "/path", "auto_next_sprint": true|false}}`. Défaut : false. Le nœud sprint_complete consulte cette config pour décider de boucler vers E3 (Sprint Backlog).

**T5 — Format thread_id pour sprints**  
Convention : `{project_id}-sprint-{NN}` avec padding 2 chiffres (sprint-01, sprint-02, …). Évite les tri alphabétiques incorrects (sprint-10 avant sprint-2). Documenter dans N1 (cloud gratuit).

**T6 — build_docs si pas de config**  
Si aucun `conf.py` (Sphinx) ou `jsdoc.json` : skip avec log "No doc config, skipping build_docs". Variable `BUILD_DOCS_REQUIRED` : false (défaut) = skip silencieux ; true = échec si pas de config.

**T7 — Déclenchement sync_artifacts**  
Optionnel. Déclenchement : cron (ex. `SYNC_ARTIFACTS_CRON="0 0 * * 0"` = dimanche minuit) ou invocation manuelle du nœud. Si non configuré : désactivé.

**T8 — Exit codes handle_interrupt**  
Normalisation : 0 = succès ; 1 = erreur (thread sans interrupt, ou autre) ; 2 = usage (arguments invalides, ex. --thread-id manquant quand requis). Documenter dans la doc du script.

#### B.5 Corrections Simulation 006 (U1–U8)

*Les éléments ci-dessous proviennent du rapport Simulation_006_2026-03-06. Ils corrigent des ambiguïtés critiques non couvertes par les simulations 001–005.*

**U1 — Co-construction de la DoD (Definition of Done) dans H2 (validation Architecture + DoD (Definition of Done))**  
*Problème* : La DoD (Definition of Done) n'avait pas de flux de création explicite dans le graphe. R-1 (Nghia (Product Owner)) est humain, sans nœud dédié ; aucun interrupt H ne portait la DoD (Definition of Done).  
*Correction* : Le nœud R-2 (Albert System Architect) (E2 (architecture, DoD (Definition of Done))) génère un *draft* DoD (Definition of Done) via template Pydantic (critères basés sur Architecture.md). Le payload H2 (validation Architecture + DoD (Definition of Done)) contient Architecture.md **et** ce draft DoD (Definition of Done). Lors de la validation H2 (validation Architecture + DoD (Definition of Done)), R-1 (Nghia (Product Owner)) amende la DoD (Definition of Done) (critères d'acceptation métier) et R-7 (Nghia (Stakeholder)) valide l'ensemble. La DoD (Definition of Done) finalisée est stockée dans `state.dod` (TypedDict) et écrite en BaseStore (mémoire long terme) (`project/{id}/dod`). Elle est indexée dans le RAG (recherche sémantique) (nœud post-H2 (validation Architecture + DoD (Definition of Done)) : `--sources architecture,dod`). R-6 (Albert QA & DevOps) charge la DoD (Definition of Done) depuis l'état ou le BaseStore (mémoire long terme) en E5 (tests, CI local).

**U2 — Branches "rejected" sur interrupts H1 (validation Epic)–H4 (Sprint Review, CI verts)**  
*Problème* : `Command(resume={"status":"rejected"})` n'avait pas de comportement défini pour chaque interrupt. Sans boucle de correction, le pipeline se bloquait ou terminait en erreur.  
*Correction* : Chaque nœud qui reçoit un `resume` vérifie `status` :  
- H1 (validation Epic) rejected : injecter le feedback dans l'état (`state.h1_feedback`), reboucler vers R-0 (Albert Business Analyst) (R-0 (Albert Business Analyst) produit un nouveau Epic en tenant compte du feedback). Limite : 3 cycles, puis arrêt avec rapport.  
- H2 (validation Architecture + DoD (Definition of Done)) rejected : injecter le feedback dans `state.h2_feedback`, reboucler vers R-2 (Albert System Architect) (Architecture + DoD (Definition of Done) revisitées). Limite : 3 cycles.  
- H3 (validation Sprint Backlog) rejected : injecter dans `state.h3_feedback`, reboucler vers R-3 (Albert Scrum Master) (Sprint Backlog refait). Limite : 3 cycles.  
- H4 (Sprint Review, CI verts) rejected : injecter dans `state.h4_feedback`, R-4 (Albert Dev Team)/R-5 (Albert Release Manager) traitent le correctif (nouveau cycle E4 (exécution code, sprint)→E5 (tests, CI local)). Nouveau CI requis. H4 (Sprint Review, CI verts) se redéclenche après CI vert.  
Convention : si la limite de 3 cycles est atteinte pour H1 (validation Epic)/H2 (validation Architecture + DoD (Definition of Done))/H3 (validation Sprint Backlog) → interrupt H5 (approbation escalade API payante) (escalade humaine).

**U3 — Indexation différée pendant E4 (exécution code, sprint)/E5 (tests, CI local) (conflit GPU)**  
*Problème* : Le hook Git post-commit lance nomic-embed-text après chaque commit de R-5 (Albert Release Manager) en E4 (exécution code, sprint), provoquant un conflit GPU avec qwen2.5-coder.  
*Correction* : Variable `AGILE_DEFER_INDEX=true` dans `.agile-env` (configurée par `setup_project_hooks.sh`). Comportement hook modifié : si `AGILE_DEFER_INDEX=true`, le hook écrit une ligne dans `logs/pending_index.log` (format : `<timestamp> <commit_hash> <project_id>`) au lieu de lancer index_rag. Le nœud sprint_complete lit `pending_index.log`, lance index_rag une seule fois en fin de sprint (hors E4 (exécution code, sprint)/E5 (tests, CI local)), puis vide le fichier. Valeur par défaut : `AGILE_DEFER_INDEX=false` (comportement actuel inchangé si non configuré).

**U4 — H4 (Sprint Review, CI verts) : clarification du point de déclenchement**  
*Problème* : H4 (Sprint Review, CI verts) était décrit simultanément comme "fin E6 (clôture sprint, merge)" (tableau III.6) et "pipeline CI/CD au vert" (tableau V.5.2), créant une incohérence sur le moment exact de l'interrupt.  
*Correction* : H4 (Sprint Review, CI verts) est déclenché **à la fin de E5 (tests, CI local)** (pipeline CI/CD au vert, R-6 (Albert QA & DevOps) valide). Le graphe suspend. R-7 (Nghia (Stakeholder)) effectue alors le Sprint Review (inspecte l'incrément) et prononce le Go/No-Go via `Command(resume={"status":"approved"|"rejected"})`. E6 (clôture sprint, merge) = phase post-H4 (Sprint Review, CI verts) : Retrofit Backlog (si approuvé) + nœud sprint_complete. Cette séquence est désormais cohérente entre III.6 et V.5.2.

**U5 — Numérotation et compteur des ADRs**  
*Problème* : Les ADRs produits par R-2 (Albert System Architect) à la fin de E2 (architecture, DoD (Definition of Done)) n'avaient pas de convention de numérotation, risquant des collisions (ex. ADR (Architecture Decision Record)-0 (Business Analyst)01 créé deux fois).  
*Correction* : `adr_counter: int` dans l'état TypedDict (valeur initiale : 0). À chaque ADR (Architecture Decision Record) produit par R-2 (Albert System Architect) : incrémenter `state.adr_counter`, écrire la valeur dans BaseStore (mémoire long terme) (`project/{id}/adr_counter`). Nom de fichier : `docs/ADR (Architecture Decision Record)-{NNN:03d}-{date}-{slug}.md` (ex. `ADR (Architecture Decision Record)-0 (Business Analyst)01-2026-03-06-architecture-initiale.md`). La valeur est chargée depuis BaseStore (mémoire long terme) au démarrage d'un nouveau thread (pour éviter les collisions entre sessions).

**U6 — sprint_number dans l'état TypedDict**  
*Problème* : Le nœud sprint_complete dérivait N+1 en parsant le thread_id courant, fragile si le format du thread_id était non standard.  
*Correction* : `sprint_number: int` dans l'état TypedDict (valeur initiale : 1). sprint_complete est en deux phases : (1) sprint_summary — écriture BaseStore (mémoire long terme), index_rag, sprint_number reste N **sauf en mode dégradé** (github_repo absent) où sprint_number est incrémenté ici directement ; (2) merge_to_main — si github_repo présent, après CI 2 (develop→main) vert, incrément sprint_number → N+1 et écriture BaseStore (mémoire long terme). Voir III.17 (Z1), III.18 (AA1). Le thread_id suivant est `f"{project_id}-sprint-{state.sprint_number:02d}"`. Au démarrage d'un thread, `sprint_number` est chargé depuis BaseStore (mémoire long terme) si disponible.

**U7 — Relation GitHub Actions / nœud R-6 (Albert QA & DevOps)**  
*Problème* : GitHub Actions (CI/CD) et R-6 (Albert QA & DevOps) (nœud LangGraph) étaient deux pipelines CI distincts, sans relation documentée.  
*Correction* : Rôles complémentaires : (1) **R-6 (Albert QA & DevOps) (LangGraph)** = CI local sur feature branch avant merge (E5 (tests, CI local) : Docker, Jest/Pytest, lint, build_docs). Doit passer pour déclencher H4 (Sprint Review, CI verts). (2) **GitHub Actions** = CI de validation sur PR et merge main (tests d'intégration, tests E2 (architecture, DoD (Definition of Done))E Playwright). Doit passer avant que R-5 (Albert Release Manager) ne merge la feature branch dans main. En cas de divergence (R-6 (Albert QA & DevOps) passe, GitHub Actions échoue) : priorité GitHub Actions ; R-4 (Albert Dev Team) corrige et relance.

**U8 — Procédure de clôture de projet**  
*Problème* : Aucune procédure décrite pour clore un projet terminé (archivage Chroma, merge final, mise à jour projects.json).  
*Correction* : Checklist de clôture (exécutée manuellement par R-1 (Nghia (Product Owner))/R-7 (Nghia (Stakeholder)) ou via nœud optionnel "project_close") :  
1. R-5 (Albert Release Manager) effectue le merge final de la branche develop dans main (`git merge --no-ff`).  
2. Exécuter `scripts/export_chroma.py --project-id <id> --output archives/<id>-<date>.json`.  
3. Mettre `"archived": true` dans `projects.json` (le projet est exclu des traitements actifs).  
4. Exécuter `scripts/purge_checkpoints.py --dry-run` pour vérifier les threads sans interrupt.  
5. Documenter la clôture dans le BaseStore (mémoire long terme) (`project/{id}/status = "archived"`).  
Cette checklist est ajoutée à la documentation du projet (README ou Architecture.md).

#### B.6 Corrections Simulation 007 (V1–V7)

*Les éléments ci-dessous proviennent du rapport Simulation_007_2026-03-07.*

**V1 — Payload H5 (approbation escalade API payante) : distinction reason**  
H5 (approbation escalade API payante) est réutilisé pour deux cas : (a) escalade N2 (cloud payant) (coût), (b) limite de rejections H1 (validation Epic)/H2 (validation Architecture + DoD (Definition of Done))/H3 (validation Sprint Backlog)/H4 (Sprint Review, CI verts) atteinte. Pour éviter la confusion, le payload `interrupt()` de H5 (approbation escalade API payante) inclut obligatoirement un champ `reason` : `"cost_escalation"` (cas habituel d'escalade N2 (cloud payant)) ou `"max_rejections_H{n}"` (ex. `"max_rejections_H2 (validation Architecture + DoD (Definition of Done))"` après 3 H2 (validation Architecture + DoD (Definition of Done))-rejected), ou `"max_h4_rejections"`. Le script `handle_interrupt.py` affiche un message différent selon `reason`. Aucun nouveau type H7 requis.

**V2 — Nœud "load_context" en entrée de thread**  
Nœud "load_context" exécuté en premier à chaque démarrage de thread (avant E1 (idéation, Epic) pour un nouveau projet, avant E3 (Sprint Backlog) pour un sprint suivant) :  
1. Lit `adr_counter` depuis BaseStore (mémoire long terme) (`project/{id}/adr_counter`). Si absent : 0.  
2. Lit `sprint_number` depuis BaseStore (mémoire long terme) (`project/{id}/sprint_counter`). Si absent : 1.  
3. Lit la dernière DoD (Definition of Done) depuis BaseStore (mémoire long terme) (`project/{id}/dod/{sprint_number}`). Si absente : `None` (E2 (architecture, DoD (Definition of Done)) déclenchera la création).  
4. Injecte les valeurs dans l'état initial du thread.  
Ce nœud garantit la continuité entre sessions et évite les collisions de compteurs.

**V3 — Re-déclenchement de E2 (architecture, DoD (Definition of Done)) sur changement architectural**  
Le nœud sprint_complete (fin E6 (clôture sprint, merge)) positionne `state.needs_architecture_review = True` si le Sprint Backlog contient des tickets taggués `#architectural-change` ou si R-3 (Albert Scrum Master) l'a signalé. Dans ce cas, la boucle sprint_complete redirige vers E2 (architecture, DoD (Definition of Done)) au lieu de E3 (Sprint Backlog). H2 (validation Architecture + DoD (Definition of Done)) se re-déclenche (R-2 (Albert System Architect) amende Architecture.md + DoD (Definition of Done)). Après H2 (validation Architecture + DoD (Definition of Done)) approuvé : retour à E3 (Sprint Backlog). Si aucun changement architectural : boucle directe E6 (clôture sprint, merge)→E3 (Sprint Backlog) (comportement par défaut).

**V4 — Stratégie de branches Git (modèle défini)**  
Modèle retenu : **feature branch par sprint** (pas par ticket). Topologie :  
- `main` : branche de production. R-5 (Albert Release Manager) ne merge dans main qu'après H4 (Sprint Review, CI verts) approuvé + GitHub Actions vert (V5).  
- `develop` : branche d'intégration continue. R-5 (Albert Release Manager) crée `feature/{project_id}-sprint-{NN}` depuis `develop`.  
- R-4 (Albert Dev Team) génère les commits sur la feature branch. R-5 (Albert Release Manager) merge feature→develop après H4 (Sprint Review, CI verts) approuvé.  
- GitHub Actions déclenché sur la PR develop→main.  
- H6 (résolution conflit Git) (conflit Git) s'applique aux merge feature→develop et develop→main.

**V5 — H4 (Sprint Review, CI verts) toujours déclenché après CI vert dans E5 (tests, CI local)**  
H4 (Sprint Review, CI verts) est l'interrupt de *sortie* de E5 (tests, CI local). H5 (approbation escalade API payante) est un interrupt *intra-E5 (tests, CI local)* (bloquant temporaire pour escalade N2 (cloud payant) ou max_rejections). Séquence garantie : E5 (tests, CI local) → [0 ou N interrupts H5 (approbation escalade API payante)] → CI vert → interrupt H4 (Sprint Review, CI verts). Le nœud E5 (tests, CI local) vérifie CI vert avant de déclencher H4 (Sprint Review, CI verts), quelle que soit l'historique H5 (approbation escalade API payante). Si CI reste rouge après H5 (approbation escalade API payante) et N2 (cloud payant) : le nœud peut relancer Self-Healing ou escalader à nouveau.

**V6 — DoD (Definition of Done) versionnée par sprint dans BaseStore (mémoire long terme)**  
Namespace BaseStore (mémoire long terme) : `project/{id}/dod/{sprint_number}` (ex. `project/cli/dod/1`, `project/cli/dod/2`). À la fin de H2 (validation Architecture + DoD (Definition of Done)), le nœud post-H2 (validation Architecture + DoD (Definition of Done)) écrit la DoD (Definition of Done) finalisée sous `project/{id}/dod/{sprint_number}`. Le nœud load_context charge `project/{id}/dod/{sprint_number}` ; si absent (premier sprint), charge `project/{id}/dod/1` ou crée. En lecture, R-6 (Albert QA & DevOps) utilise la DoD (Definition of Done) de `state.dod` (chargée à l'init du thread). Les DoDs passées sont conservées pour audit.

**V7 — H4 (Sprint Review, CI verts) rejected : cycle correctif sur même feature branch**  
H4 (Sprint Review, CI verts) rejected → R-4 (Albert Dev Team) génère des commits correctifs sur la *même* feature branch (suffixe `fix-attempt-N`). Nouveau cycle E5 (tests, CI local) obligatoire (CI local R-6 (Albert QA & DevOps), puis GitHub Actions si feature branch pushée). H4 (Sprint Review, CI verts) se redéclenche après nouveau CI vert. Limite : 3 cycles H4 (Sprint Review, CI verts)-rejected → H5 (approbation escalade API payante) avec `reason="max_h4_rejections"`. La feature branch conserve l'historique complet (développement + corrections).

#### B.7 Corrections Simulation 008 (W1–W6)

*Les éléments ci-dessous proviennent du rapport Simulation_008_2026-03-08.*

**W1 — Entry point du graphe : start_phase**  
L'invocation du graphe accepte un paramètre de config `start_phase: "E1 (idéation, Epic)" | "E3 (Sprint Backlog)"` (via `{"configurable": {"start_phase": "E3 (Sprint Backlog)", ...}}`). Le nœud load_context route vers E1 (idéation, Epic) (nouveau projet : création Backlog) ou vers E3 (Sprint Backlog) (nouveau sprint : Sprint Planning) selon ce paramètre. Commandes types :  
- Nouveau projet : `python run_graph.py --project-id cli --start-phase E1 (idéation, Epic) --thread-id cli-phase-0`  
- Nouveau sprint : `python run_graph.py --project-id cli --start-phase E3 (Sprint Backlog) --thread-id cli-sprint-02`  
Valeur par défaut : `E1 (idéation, Epic)` (fail-safe pour les nouveaux projets).

**W2 — needs_architecture_review : champ Pydantic Sprint Backlog**  
Le schéma Pydantic `SprintBacklog` (sortie de R-3 (Albert Scrum Master)) inclut `architectural_change: bool` (défaut : false). R-3 (Albert Scrum Master) positionne ce champ à true si les nouveaux tickets impliquent des changements de modules, de contrats d'API, ou de dépendances non prévus dans Architecture.md (détection via RAG (recherche sémantique) + comparaison). sprint_complete lit `state.sprint_backlog.architectural_change` et positionne `state.needs_architecture_review` en conséquence.

**W3 — DoD (Definition of Done) manquante avant re-E2 (architecture, DoD (Definition of Done)) : fallback version précédente**  
load_context : si `project/{id}/dod/{sprint_number}` absent dans BaseStore (mémoire long terme) → charger `project/{id}/dod/{sprint_number - 1}`. Si sprint_number=1 et aucune DoD (Definition of Done) disponible : `state.dod = None` (normal : E2 (architecture, DoD (Definition of Done)) créera la DoD (Definition of Done)). Règle : `state.dod` n'est jamais `None` dès que sprint_number > 1, sauf si le BaseStore (mémoire long terme) est corrompu ou vide (alerte dans les logs).

**W4 — H4 (Sprint Review, CI verts) conditionné à CI local ET GitHub Actions**  
Nouveau flux E5 (tests, CI local)→H4 (Sprint Review, CI verts) : R-5 (Albert Release Manager) pousse la feature branch vers le remote *avant* que H4 (Sprint Review, CI verts) soit déclenché. GitHub Actions tourne sur la PR feature→develop. Si GitHub Actions passe : H4 (Sprint Review, CI verts) est déclenché (Sprint Review R-7 (Nghia (Stakeholder))). Si GitHub Actions échoue : retour Self-Healing (R-4 (Albert Dev Team) corrige, nouveau cycle E5 (tests, CI local)). H4 (Sprint Review, CI verts) n'est jamais déclenché si GitHub Actions est rouge. Cette approche élimine le cas "H4 (Sprint Review, CI verts)-approved puis merge impossible". Voir III.13 (V4).

**W5 — Workflow hotfix**  
Branche `hotfix/{project_id}-{date}-{description}` créée depuis `main` par R-5 (Albert Release Manager). Invocation graphe : `--start-phase HOTFIX (correctif urgent) --thread-id {project_id}-hotfix-{date}` (voir III.16 Y4 pour le Sprint Backlog synthétique). R-4 (Albert Dev Team) applique le correctif. R-6 (Albert QA & DevOps) lance E5 (tests, CI local) (CI local + GitHub Actions sur PR hotfix→main). R-5 (Albert Release Manager) merge hotfix→main + hotfix→develop après H4 (Sprint Review, CI verts). Aucun Sprint Review : le merge hotfix→main est la validation. Documenter dans Architecture.md (ADR (Architecture Decision Record) de hotfix).

**W6 — Variable AGILE_PROJECTS_JSON**  
Variable d'environnement `AGILE_PROJECTS_JSON` (défaut : `$AGILE_ORCHESTRATION_ROOT/config/projects.json`). Définie dans `.agile-env` ou en variable système. `setup_project_hooks.sh` génère la valeur par défaut. Les nœuds load_context, sprint_complete, et handle_interrupt.py lisent projects.json via cette variable. Si la variable est absente et le chemin par défaut inexistant : erreur explicite avec message d'aide.

#### B.8 Corrections Simulation 009 (X1–X4)

*Les éléments ci-dessous proviennent du rapport Simulation_009_2026-03-09.*

**X1 — Deux PR GitHub Actions distinctes (CI 1 (feature→develop) et CI 2 (develop→main))**  
Clarification de la stratégie CI :  
- **CI 1 (feature→develop)** (pré-H4 (Sprint Review, CI verts), obligatoire) : GitHub Actions déclenché sur PR `feature/{project_id}-sprint-{NN} → develop`. Condition nécessaire au déclenchement de H4 (Sprint Review, CI verts). Valide l'intégration du sprint dans develop.  
- **CI 2 (develop→main)** (post-E6 (clôture sprint, merge), obligatoire avant merge main) : GitHub Actions déclenché sur PR `develop → main`. R-5 (Albert Release Manager) ouvre cette PR après sprint_complete (post-H4 (Sprint Review, CI verts)). Merge develop→main conditionné à CI 2 (develop→main) vert. Effectué par R-5 (Albert Release Manager) (nœud "merge_to_main" post-sprint_complete, ou action manuelle).  
Les deux CI partagent la même configuration GitHub Actions mais s'exécutent sur des PRs différentes.

**X2 — Push R-5 (Albert Release Manager) en fin de E4 (exécution code, sprint) (timing unique)**  
R-5 (Albert Release Manager) effectue un push unique à la fin de E4 (exécution code, sprint), après le dernier commit de ticket. Ce push ouvre la PR feature→develop sur GitHub. GitHub Actions CI 1 (feature→develop) démarre. R-6 (Albert QA & DevOps) (CI local) démarre en parallèle dans le même nœud E5 (tests, CI local). Pas de push intermédiaire pendant E4 (exécution code, sprint) (évite les triggers répétés de GitHub Actions et les conflits AGILE_DEFER_INDEX).

**X3 — Polling GitHub Actions par R-6 (Albert QA & DevOps) (gh run watch)**  
R-6 (Albert QA & DevOps) (nœud E5 (tests, CI local)) attend le résultat de CI 1 (feature→develop) via `run_shell("gh run watch --repo {repo} --exit-status --interval 30")`. Variable `GITHUB_ACTIONS_TIMEOUT=600` secondes (défaut 10 min). Si le run CI 1 (feature→develop) n'est pas terminé dans ce délai : interrupt H5 (approbation escalade API payante) avec `reason="github_actions_timeout"` (L'opérateur peut étendre ou relancer le CI). `gh run watch` nécessite GitHub CLI (`gh`) installé et authentifié. Ajouter `gh` à la checklist d'installation. `repo` = valeur `projects[project_id].github_repo` dans projects.json (nouveau champ optionnel).

**X4 — AGILE_BASESTORE_STRICT : résilience load_context**  
Variable `AGILE_BASESTORE_STRICT=false` (défaut) : si BaseStore (mémoire long terme) inaccessible, load_context utilise les valeurs par défaut (adr_counter=0, sprint_number=1, dod=None) et log WARNING. Si `AGILE_BASESTORE_STRICT=true` : load_context lève une exception explicite avec message d'aide (vérifier la connexion BaseStore (mémoire long terme)). Recommandé en production : `AGILE_BASESTORE_STRICT=true`.

#### B.9 Corrections Simulation 010 (Y1–Y5)

*Les éléments ci-dessous proviennent du rapport Simulation_010_2026-03-10.*

**Y1 — Création de la branche develop**  
`setup_project_hooks.sh` crée la branche `develop` depuis `main` si elle n'existe pas : `git checkout -b develop main && git push -u origin develop`. Ajouté à la checklist d'installation (étape "init_branches"). Si `develop` existe déjà : skip silencieux.

**Y2 — gh pr create et gh pr checks**  
Après le push de la feature branch en fin de E4 (exécution code, sprint) (X2), R-5 (Albert Release Manager) exécute `gh pr create --base develop --head feature/{project_id}-sprint-{NN} --title "Sprint {NN}" --body "Sprint automatisé"`. Le workflow GitHub Actions doit être déclenché sur `pull_request` (et non seulement `push`). R-6 (Albert QA & DevOps) surveille CI 1 (feature→develop) via `gh pr checks {pr_number} --required --watch --interval 30`. Ajouter à la checklist : `gh auth login` (une seule fois, jeton persisté dans `~/.config/gh`).

**Y3 — Nœud merge_to_main dans sprint_complete**  
sprint_complete, après écriture BaseStore (mémoire long terme) sprint_summary, exécute le nœud R-5 (Albert Release Manager) "merge_to_main" : (1) `gh pr create --base main --head develop --title "Release sprint {NN}"`. (2) `gh pr checks {pr_number} --required --watch --interval 30` (CI 2 (develop→main)). (3) Si CI 2 (develop→main) vert : `gh pr merge --merge --delete-branch=false` (merge develop→main). (4) Si CI 2 (develop→main) rouge : interrupt H5 (approbation escalade API payante) avec `reason="ci2_github_actions_failure"`. R-4 (Albert Dev Team) corrige sur feature branch, nouveau cycle E5 (tests, CI local)/CI 1 (feature→develop), puis re-push develop, CI 2 (develop→main) se relance.

**Y4 — start_phase HOTFIX (correctif urgent)**  
Nouveau `start_phase: "HOTFIX (correctif urgent)"`. Invocation : `python run_graph.py --project-id webhook --start-phase HOTFIX (correctif urgent) --thread-id webhook-hotfix-2026-03-10 --hotfix-description "Fix NPE in X"`. load_context crée un Sprint Backlog synthétique : `SprintBacklog(tickets=[Ticket(id="HF-001", description=hotfix_description)], architectural_change=False)`. Le reste du flux E4 (exécution code, sprint)→E5 (tests, CI local)→H4 (Sprint Review, CI verts) s'applique normalement. Merge : (1) CI 1 (feature→develop) et H4 (Sprint Review, CI verts) valident hotfix→main. (2) R-5 (Albert Release Manager) merge hotfix→develop directement (`git checkout develop && git merge --no-ff hotfix/... && git push`) sans PR ni CI supplémentaire — le code a déjà été validé sur main. Voir III.19 (BB3).

**Y5 — Mode dégradé si github_repo absent**  
Si `projects[project_id].github_repo` est absent ou vide : le nœud E5 (tests, CI local) ne lance pas `gh pr create` ni `gh pr checks`. CI 1 (feature→develop) est skippé. Log WARNING : `"[E5 (tests, CI local)] github_repo non configuré pour {project_id} — CI GitHub Actions skippé. H4 (Sprint Review, CI verts) déclenché sur CI local seul."` H4 (Sprint Review, CI verts) déclenché uniquement sur CI local (R-6 (Albert QA & DevOps)) vert. Merge develop→main : action manuelle (pas de nœud merge_to_main). Documenter dans le README du projet.

#### B.10 Corrections Simulation 011 (Z1–Z2)

*Les éléments ci-dessous proviennent du rapport Simulation_011_2026-03-11.*

**Z1 — sprint_complete : incrément sprint_number après CI 2 (develop→main) seulement**  
sprint_complete est restructuré en deux phases atomiques :  
1. **Phase sprint_summary** : écriture du sprint_summary dans BaseStore (mémoire long terme) (`project/{id}/sprints/sprint-{NN}`), déclenchement index_rag (ou traitement pending_index.log si AGILE_DEFER_INDEX). `sprint_number` reste à N.  
2. **Phase merge_to_main** : exécution du nœud R-5 (Albert Release Manager) merge_to_main (gh pr create develop→main, gh pr checks CI 2 (develop→main), gh pr merge). **Seulement si CI 2 (develop→main) vert** : incrémenter `state.sprint_number` → N+1 et écrire dans BaseStore (mémoire long terme) (`project/{id}/sprint_counter`). Si CI 2 (develop→main) rouge → H5 (approbation escalade API payante) `reason="ci2_github_actions_failure"` sans modification de sprint_number. La correction s'applique sur develop (commits sur feature branch → merge feature→develop) ; une fois CI 2 (develop→main) vert → incrément.

**Z2 — Branch protection et merge automatique**  
Documentation dans le README du projet orchestration :  
- **Cas sans branch protection** (recommandé pour usage solo) : `gh pr merge` s'exécute automatiquement après CI 2 (develop→main) vert.  
- **Cas avec branch protection sur develop** : ne pas activer de required reviewer sur `develop`. Seule la vérification CI (status checks) est requise. `gh pr merge` passe si CI vert.  
- **Cas avec branch protection stricte sur main** (requis reviewer) : le nœud merge_to_main ouvre la PR develop→main et attend. Interrupt H5 (approbation escalade API payante) (`reason="pr_review_required"`) : l'opérateur approuve manuellement la PR sur GitHub, puis `Command(resume="merged")`. R-5 (Albert Release Manager) ne merge pas automatiquement.  
Recommandation : activer uniquement la vérification CI sur `develop` ; garder la décision de merge main aux humains si souhaité (configurable).

#### B.11 Corrections Simulation 012 (AA1–AA2)

*Les éléments ci-dessous proviennent du rapport Simulation_012_2026-03-12. Ce sont les dernières corrections avant convergence.*

**AA1 — sprint_number incrément en mode dégradé**  
Règle de clôture du sprint_number (deux cas mutuellement exclusifs) :  
- Si `projects[project_id].github_repo` est présent et non vide : incrément sprint_number dans la **phase 2** (merge_to_main), après CI 2 (develop→main) vert.  
- Si `github_repo` est absent ou vide (mode dégradé) : incrément sprint_number dans la **phase 1** (sprint_summary), immédiatement après écriture BaseStore (mémoire long terme) sprint_summary.  
Le nœud sprint_complete vérifie `github_repo` en début d'exécution pour choisir la règle d'incrément.

**AA2 — Suppression de la notation H4 (Sprint Review, CI verts)' : H5 (approbation escalade API payante) avec reason**  
La notation "H4 (Sprint Review, CI verts)'" introduite en III.17 est supprimée. Le cas "PR develop→main requiert un reviewer humain" est géré par H5 (approbation escalade API payante) avec `reason="pr_review_required"`. Conformément à la convention V1 (III.13), H5 (approbation escalade API payante) est le seul interrupt d'escalade humaine, distingué par son champ `reason` :  
- `"cost_escalation"` : escalade N2 (cloud payant) (coût)  
- `"max_rejections_H{n}"` : limite de cycles rejected atteinte  
- `"max_h4_rejections"` : limite H4 (Sprint Review, CI verts)-rejected atteinte  
- `"github_actions_timeout"` : timeout polling CI 1 (feature→develop) ou CI 2 (develop→main)  
- `"ci2_github_actions_failure"` : CI 2 (develop→main) rouge après merge_to_main  
- `"pr_review_required"` : branch protection stricte sur main, merge nécessite approbation humaine  

#### B.12 Corrections Simulation 013 (BB1–BB4)

*Les éléments ci-dessous proviennent du rapport Simulation_013_2026-03-13 — simulation finale 3 mois.*

**BB1 — Checklist 4.1 : numérotation corrigée**  
Deux étapes étaient numérotées "11". Correction : 10=GitHub CLI, 11=Docker, 12=Vercel/Railway.

**BB2 — W5 (hotfix) : start_phase E4 (exécution code, sprint) obsolète remplacé par HOTFIX (correctif urgent)**  
La section W5 (III.14) utilisait `--start-phase E4 (exécution code, sprint)` introduit avant que Y4 (III.16) ne crée `start_phase HOTFIX (correctif urgent)`. W5 est mis à jour pour utiliser `--start-phase HOTFIX (correctif urgent)` (conforme à Y4 qui crée le SprintBacklog synthétique HF-001). Plus d'ambiguïté sur l'entry point hotfix.

**BB3 — Hotfix merge develop→ : direct sans PR**  
Le merge hotfix→develop est un merge direct (`git merge --no-ff`) sans PR ni CI supplémentaire : le code a déjà été validé par CI 1 (feature→develop) (PR hotfix→main) et H4 (Sprint Review, CI verts) (Sprint Review). Évite une double validation inutile sur develop pour un correctif d'urgence. Documenter dans Architecture.md (ADR (Architecture Decision Record) de hotfix si besoin).

**BB4 — auto_next_sprint : boucle E3 (Sprint Backlog) après phase 2 (ou phase 1 en dégradé)**  
Si `auto_next_sprint=true`, la boucle vers E3 (Sprint Backlog) pour le sprint N+1 se déclenche :  
- Après **phase 2** (merge_to_main vert, sprint_number incrémenté) si `github_repo` présent.  
- Après **phase 1** (sprint_summary, incrément immédiat) si mode dégradé (github_repo absent).  
Cela garantit que E3 (Sprint Backlog) du sprint N+1 démarre avec un sprint_number et un develop à jour.

#### B.13 Corrections Simulation 014 (CC1–CC3)

*Les éléments ci-dessous proviennent du rapport Simulation_014_2026-03-14 — validation flux sous RTX 3060 12 Go.*

**CC1 — OLLAMA_KEEP_ALIVE dans checklist 4.1**  
Ajout dans l'étape 1 (Ollama) : pour RTX 3060 12 Go, activer un keep-alive long (ex. `export OLLAMA_KEEP_ALIVE=24h`) pour éviter le déchargement après inactivité, et précharger le modèle prioritaire par warmup (ex. `ollama run qwen2.5-coder:7b "warmup"`). En legacy 12 Go, garder `AGILE_DEFER_INDEX=true` pour éviter la contention embeddings (nomic-embed-text) pendant E4/E5.

**CC2 — Continue.dev pendant E4 (exécution code, sprint)/E5 (tests, CI local)**  
Documenter dans III.8-J : si Continue.dev reste ouvert pendant E4 (exécution code, sprint)/E5 (tests, CI local), le configurer sur qwen2.5-coder:14b (aligné sur R-4 (Albert Dev Team)). Un modèle différent provoque swapping → latence et timeouts. Alternative : désactiver l'autocomplétion IA.

**CC3 — AGILE_DEFER_INDEX recommandation RTX 3060**  
Renforcer dans III.8-C : sur RTX 3060 12 Go, `AGILE_DEFER_INDEX=true` fortement recommandé. nomic-embed-text et qwen2.5-coder partagent le GPU ; indexation pendant E4 (exécution code, sprint)/E5 (tests, CI local) = conflit.

---

IX. Layout Architectural Senior

*Note : E4 (exécution code, sprint) piloté par LangGraph (nœuds R-4 (Albert Dev Team), R-5 (Albert Release Manager) + tools), cf. Simulation 001.*



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
R1\_Init(("R-1 (Nghia (Product Owner)): Product Owner<br/>Nghia (PM)<br/>(Porteur de la vision initiale)")):::humain
R0\["R-0 (Albert Business Analyst): Business Analyst<br/>Cascade: qwen2.5:14b -> Gemini -> Opus 4.6"\]:::aiFree
R1\_Init <-->|Iterations illimitees| R0
end

%% --- LE POINT DE BASCULE ---
subgraph BASCULE \[FRONTIERE DE FACTURATION ET ENTREE EN AGILE\]
GrosTicket\[/"Epic Initial Mature<br/>(Livrable fondateur hors cycle)"/\]:::artifact
R0 -.->|Cristallise| GrosTicket
end

%% --- L'USINE AGILE (API PAYANTES & OUTILS LOCAUX) ---
subgraph USINE \[ ⚙️ USINE AGILE ITERATIVE ET STRUCTUREE \]
direction TB

%% COUCHE STRATÉGIQUE
subgraph ENV\_C \[ENV-C : EXPERTISE INTELLIGENCE EN CASCADE\]
R2\["R-2 (Albert System Architect): System Architect<br/>Cascade: qwen2.5:14b -> AI Studio -> Opus 4.6"\]:::aiPaid
R4\["R-4 (Albert Dev Team): Dev Team<br/>Cascade: qwen2.5-coder:14b -> AI Studio -> Sonnet 4.6"\]:::aiPaid
end

%% COUCHE PILOTAGE
subgraph ENV\_B \[ENV-B : HUB VS CODE HYBRIDE\]
direction LR
R1\_Agile(("R-1 (Nghia (Product Owner)): Product Owner<br/>Nghia (PM)<br/>(Gratuit / Open-Source)")):::humain
Backlog\[/"Besoins - Product Backlog.md<br/>(Vivant et Iteratif)"/\]:::artifact
ArchDoc\[/"Architecture.md<br/>(Specifications)"/\]:::artifact
DoD (Definition of Done)\[/"Definition of Done (DoD (Definition of Done))<br/>(Contrat d'acceptation)"/\]:::artifact
R7(("R-7 (Nghia (Stakeholder)): Stakeholder<br/>Nghia (Dir)<br/>(Gratuit / Open-Source)")):::humain
end

%% COUCHE EXÉCUTION
subgraph ENV\_D \[ENV-D : FACTORY LOCALE GRATUITE\]
direction TB
R3\["R-3 (Albert Scrum Master): Scrum Master<br/>Cascade: qwen2.5-coder:14b -> AI Studio -> Sonnet"\]:::localNode
SprintBacklog\[/"Sprint Backlog<br/>(Tickets Atomiques)"/\]:::artifact
R5\[("R-5 (Albert Release Manager): Release Manager<br/>Git + Cascade qwen2.5-coder/Sonnet")\]:::localNode
R6{"R-6 (Albert QA & DevOps): QA et DevOps<br/>Docker, Jest + Cascade qwen2.5-coder/Sonnet"}:::localNode
end
end

%% --- LIAISONS LOGIQUES DU CYCLE AGILE ---
GrosTicket -->|E1 (idéation, Epic): Initialise l'Usine| Backlog

%% Activité de R-1 (Nghia (Product Owner)) dans le Hub
R1\_Agile <-->|Gere et Priorise| Backlog
R1\_Agile -.->|Co-construit| DoD (Definition of Done)
R2 -.->|Co-construit| DoD (Definition of Done)
R7 -.->|Valide| DoD (Definition of Done)

Backlog -->|Input pour Refinement| R2
R2 -->|E2 (architecture, DoD (Definition of Done)): Construit| ArchDoc

ArchDoc -->|E3 (Sprint Backlog): Validation| R7

%% R-3 (Albert Scrum Master) est mis en évidence ici
Backlog & ArchDoc -->|Fournit le contexte| R3
R3 -->|Genere| SprintBacklog

SprintBacklog -->|E4 (exécution code, sprint): Assigne Ticket| R4
R4 -->|E4 (exécution code, sprint): Code via API| R5
R5 -->|E5 (tests, CI local): Trigger CI-CD| R6

%% La DoD (Definition of Done) devient la grille de lecture de la QA
DoD (Definition of Done) -->|Criteres de validation| R6

R6 -- "REJECT: Self-Healing" --> R4
R6 ==>|E6 (clôture sprint, merge): Valide et Deploie| R7

%% Rétrofit cible directement le Backlog vivant
R7 -.->|Retrofit - Mise a jour iterative| Backlog

%% =========================================================
%% CONTRAINTES INVISIBLES POUR ÉCRASER LA HAUTEUR DE L'USINE
%% =========================================================
%% Ces liens n'affichent rien, ils forcent R-1 (Nghia (Product Owner)) et R-7 (Nghia (Stakeholder)) à se
%% rapprocher du centre, raccourcissant drastiquement les flèches.
R1\_Agile ~~~ ArchDoc
R7 ~~~ ArchDoc
GrosTicket ~~~ Backlog