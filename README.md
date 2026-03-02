# Albert — L'associé IA de Nghia

> **Albert est le collaborateur IA polyvalent qui accompagne Nghia de l'idéation au déploiement.**
> Il n'a pas un rôle fixe — il porte toutes les casquettes non-humaines du cycle de développement Agile.

---

## Qui est Albert ?

Albert est une entité IA multi-rôles construite sur un écosystème open-source (LangGraph, Ollama, VS Code). Il change de casquette selon la phase du projet, tout en restant le même collaborateur de confiance.

| Phase | Casquette d'Albert | Modèle utilisé |
|-------|--------------------|----------------|
| Idéation | Business Analyst (R-0) | gemma3:12b → Gemini → Opus |
| Architecture | System Architect (R-2) | gemma3:12b → Gemini → Opus |
| Sprint Planning | Scrum Master (R-3) | qwen2.5-coder:7b → Gemini → Sonnet |
| Développement | Dev Team (R-4) | qwen2.5-coder:7b → Gemini → Sonnet |
| Versioning | Release Manager (R-5) | qwen2.5-coder:7b → Gemini → Sonnet |
| Qualité | QA & DevOps (R-6) | qwen2.5-coder:7b → Gemini → Sonnet |

**Nghia reste :** Product Owner (R-1) + Stakeholder (R-7) — la vision et le Go/No-Go final.

---

## Principe fondateur

```
Albert propose.
Nghia décide.
```

Albert ne fait rien sans validation explicite de Nghia aux jalons critiques (H1–H6). Tout est tracé dans Git, LangSmith, et les ADRs.

---

## Stack technique

| Composant | Technologie | Coût |
|-----------|-------------|------|
| Orchestration multi-agents | LangGraph + LangChain | 0 € |
| Modèles locaux (80% des cas) | Ollama — `qwen2.5-coder:7b` + `gemma3:12b` | 0 € |
| Fallback cloud gratuit | Google AI Studio — `gemini-2.5-flash` | 0 € |
| Expertise critique (dernier recours) | Anthropic — `claude-opus-4-6` / `claude-sonnet-4-6` | Pay-as-you-go |
| IDE & autocomplétion | VS Code + Continue.dev + Roo Code | 0 € |
| RAG (mémoire sémantique) | Chroma + `nomic-embed-text` (Ollama) + chroma-mcp (partage IDE) | 0 € |
| Traçage | LangSmith (free tier) | 0 € |
| CI/CD | GitHub Actions (dépôts publics) | 0 € |

**Règle de cascade :** N0 (local Ollama) → N1 (Gemini gratuit) → N2 (Claude payant). On n'escalade que si le niveau inférieur échoue ou renvoie HTTP 429.

---

## Cycle de vie d'un projet avec Albert

```
PHASE 0 — IDÉATION (hors Agile, gratuite)
  Nghia + Albert (R-0) → itérations libres → Gros Ticket mature
  ↓ H1 : Nghia valide le Gros Ticket

CYCLE AGILE (sprints itératifs)
  E1 → Product Backlog         (Nghia / R-1)
  E2 → Architecture + DoD      (Albert R-2) ← H2 : Nghia valide
  E3 → Sprint Backlog          (Albert R-3) ← H3 : Nghia valide
  E4 → Code + Git              (Albert R-4 + R-5)
  E5 → Tests + CI              (Albert R-6)  ← H4 : Nghia Sprint Review
  E6 → Retrofit + Release      (Albert R-5)
  E6bis → chroma-mcp           (optionnel)   ← RAG partagé IDE (Continue.dev/Cursor/Cline)
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
│   └── albert/                                       ← Implémentation LangGraph
├── config/
│   └── projects.json                                 ← Registre des projets
├── scripts/
│   ├── handle_interrupt.py                           ← Gestion des interrupts H1–H6
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
export AGILE_RAG_FILE_WATCHER=1     # Déclenche index_rag à la sauvegarde (hors E4/E5)
export AGILE_RAG_INCREMENTAL=1      # Indexation incrémentale (fichiers modifiés uniquement)
```

### 4. RAG partagé avec l'IDE (optionnel)

Pour que Cursor, Continue.dev ou Cline accèdent au même index Chroma qu'Albert :

- **chroma-mcp** (recommandé) : expose Chroma via MCP
- Un seul index = alignement agents + humains

*Règle GPU : pas d'indexation pendant E4/E5 (conflit avec qwen2.5-coder).*

Voir `specs/Specifications Ecosysteme Agile Agent IA.md` § III.7-bis.

### 5. Nouveau projet

```bash
python scripts/setup_project_hooks.sh \
  --orchestration-root $AGILE_ORCHESTRATION_ROOT \
  --project-root /chemin/du/projet \
  --project-id mon-projet

python src/albert/run_graph.py \
  --project-id mon-projet \
  --start-phase E1 \
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
