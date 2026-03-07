# Écosystème Agile Agent IA — L'associé IA de votre équipe

> **Un collaborateur IA polyvalent qui accompagne l'équipe de l'idéation au déploiement.**
> Il n'a pas un rôle fixe — il porte toutes les casquettes non-humaines du cycle de développement Agile.

---

## Vue d'ensemble

L'écosystème est une entité IA multi-rôles construite sur un socle open-source (LangGraph, Ollama, VS Code). Il change de casquette selon la phase du projet, tout en restant le même collaborateur de confiance.

| Phase | Casquette IA | Modèle utilisé |
|-------|--------------|----------------|
| Idéation | R-0 (Business Analyst IA) | qwen2.5:14b → Gemini → Opus |
| Architecture | R-2 (System Architect IA) | qwen2.5:14b → Gemini → Opus |
| Sprint Planning | R-3 (Scrum Master IA) | qwen2.5-coder:14b → Gemini → Sonnet |
| Développement | R-4 (Dev Team IA) | qwen2.5-coder:14b → Gemini → Sonnet |
| Versioning | R-5 (Release Manager IA) | qwen2.5-coder:14b → Gemini → Sonnet |
| Qualité | R-6 (QA & DevOps IA) | qwen2.5-coder:14b → Gemini → Sonnet |

**Rôles humains :** R-1 (Product Owner) + R-7 (Stakeholder) — la vision et le Go/No-Go final.

---

## Principe fondateur

```
L'IA propose.
Le superviseur décide.
```

L'IA ne fait rien sans validation explicite aux jalons critiques (H1 (validation Gros Ticket)–H6 (résolution conflit Git) : Gros Ticket, Architecture, Sprint Backlog, Sprint Review, escalade API, conflit Git). Tout est tracé dans Git, LangSmith, et les ADRs.

---

## Stack technique

| Composant | Technologie | Coût |
|-----------|-------------|------|
| Orchestration multi-agents | LangGraph + LangChain | 0 € |
| Modèles locaux (80% des cas) | Ollama — `qwen2.5-coder:14b` + `qwen2.5:14b` | 0 € |
| Fallback cloud gratuit | Google AI Studio — `gemini-2.5-flash` | 0 € |
| Expertise critique (dernier recours) | Anthropic — `claude-opus-4-6` / `claude-sonnet-4-6` | Pay-as-you-go |
| IDE & autocomplétion | VS Code + Continue.dev + Roo Code | 0 € |
| RAG (recherche sémantique) | Chroma + `nomic-embed-text` (Ollama) + chroma-mcp (partage IDE) | 0 € |
| Traçage | LangSmith (free tier) | 0 € |
| CI/CD | GitHub Actions (dépôts publics) | 0 € |

**Règle de cascade :** N0 (local Ollama) → N1 (cloud gratuit) (Gemini gratuit) → N2 (cloud payant) (Claude payant). On n'escalade que si le niveau inférieur échoue ou renvoie HTTP 429.

**GPU / VRAM :** voir `docs/HARDWARE_GPU.md` (profil recommandé VRAM ≥ 16 Go, legacy 12 Go, checklist swap RTX 3060 → RTX 5060 Ti 16G).

---

## Cycle de vie d'un projet avec l'écosystème Agile Agent IA

```
PHASE 0 — IDÉATION (hors Agile, gratuite)
  Product Owner + R-0 (Business Analyst IA) → itérations libres → Gros Ticket mature
  ↓ H1 (validation Gros Ticket) : validation humaine

CYCLE AGILE (sprints itératifs)
  E1 (idéation) → Product Backlog         (R-1 (Product Owner))
  E2 (architecture) → Architecture + DoD  (R-2 (System Architect IA)) ← H2 (validation Architecture) : validation humaine
  E3 (Sprint Backlog) → Sprint Backlog    (R-3 (Scrum Master IA)) ← H3 (validation Sprint Backlog) : validation humaine
  E4 (exécution code) → Code + Git        (R-4 (Dev Team IA) + R-5 (Release Manager IA))
  E5 (tests CI) → Tests + CI              (R-6 (QA & DevOps IA))  ← H4 (Sprint Review) : validation humaine
  E6 (clôture sprint) → Retrofit + Release (R-5 (Release Manager IA))
  E6bis → chroma-mcp           (optionnel)   ← RAG partagé IDE (Continue.dev/Roo Code/Cursor/Cline)
  ↓ Boucle vers sprint N+1
```

---

## Structure du dépôt

```
albert-agile/
├── specs/
│   ├── Specifications Ecosysteme Agile Agent IA.md   ← Spec de référence (convergée)
│   └── simulations/                                  ← 13 simulations de validation
├── src/
│   └── albert/                                       ← Implémentation LangGraph (hérite d'un projet historique "albert-core")
├── config/
│   └── projects.json                                 ← Registre des projets
├── scripts/
│   ├── handle_interrupt.py                           ← Gestion H1 (validation Gros Ticket)–H6 (résolution conflit Git) (validation Gros Ticket → conflit Git)
│   ├── index_rag.py                                  ← Pipeline Chroma (--incremental, file watcher)
│   ├── setup_project_hooks.sh                        ← Bootstrap d'un nouveau projet
│   └── purge_checkpoints.py                          ← Maintenance LangGraph
└── logs/                                             ← Logs runtime (hors Git)
```

---

## Démarrage rapide

### 1. Installation des modèles locaux

```bash
ollama pull qwen2.5-coder:7b
ollama pull gemma3:12b-it-q4_K_M
ollama pull nomic-embed-text
```

### 2. Installation des dépendances Python

```bash
pip install langgraph langchain langchain-ollama langchain-anthropic \
            langchain-google-genai langchain-chroma pydantic chromadb
```

### 3. Variables d'environnement

```bash
export LANGCHAIN_TRACING_V2=true
export LANGCHAIN_API_KEY=...        # LangSmith
export ANTHROPIC_API_KEY=...        # Claude (dernier recours)
export GOOGLE_API_KEY=...           # Gemini (fallback N1)
export AGILE_ORCHESTRATION_ROOT=/home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile

# RAG temps réel (optionnel)
export AGILE_RAG_FILE_WATCHER=1     # Déclenche index_rag à la sauvegarde (hors E4 (exécution code)/E5 (tests CI), conflit GPU)
export AGILE_RAG_INCREMENTAL=1      # Indexation incrémentale (fichiers modifiés uniquement)
```

### 4. RAG (recherche sémantique) partagé avec l'IDE (optionnel)

Pour que Continue.dev, Roo Code, Cursor ou Cline accèdent au même index Chroma que les agents IA :

- **chroma-mcp** (recommandé) : expose Chroma via MCP (Model Context Protocol)
- Un seul index = alignement agents + humains

*Règle GPU : pas d'indexation pendant E4 (exécution code) / E5 (tests CI) — conflit avec qwen2.5-coder.*

Voir `specs/Specifications Ecosysteme Agile Agent IA.md` § III.7-bis.

### 5. Nouveau projet

```bash
python scripts/setup_project_hooks.sh \
  --orchestration-root $AGILE_ORCHESTRATION_ROOT \
  --project-root /chemin/du/projet \
  --project-id mon-projet

python src/albert/run_graph.py \
  --project-id mon-projet \
  --start-phase E1 (idéation) \
  --thread-id mon-projet-phase-0
```

---

## Spec de référence

La spécification complète de l'Ecosystème Agile est dans :
`specs/Specifications Ecosysteme Agile Agent IA.md`

Ce document est **convergé et opérationnel** — validé par 13 simulations (001–013).
Il est la source de vérité pour l'implémentation.

---

## Philosophie

Albert n'est pas un abonnement SaaS. Albert est un écosystème **local-first**, **open-source**, **coût marginal proche de zéro**. La puissance du cloud (Claude Opus) est réservée aux décisions qui le méritent vraiment.

> *"80% du travail en local. 15% avec le cloud gratuit. 5% avec l'expertise critique payante."*
