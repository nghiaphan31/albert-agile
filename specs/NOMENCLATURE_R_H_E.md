# Nomenclature R-x, H-x, E-x

Référence pour la lecture des documents. À utiliser systématiquement à côté des codes.

## R-x — Rôles Agile

| Code | Rôle Agile |
|------|------------|
| R-0 | Albert Business Analyst |
| R-1 | Nghia Product Owner |
| R-2 | Albert System Architect |
| R-3 | Albert Scrum Master |
| R-4 | Albert Dev Team |
| R-5 | Albert Release Manager |
| R-6 | Albert QA & DevOps |
| R-7 | Nghia Stakeholder |

## H-x — Points d'interruption (Human-in-the-Loop)

| Code | Signification |
|------|---------------|
| H1 | validation Gros Ticket par Product Owner |
| H2 | validation Architecture + DoD par Stakeholder |
| H3 | validation Sprint Backlog par Product Owner |
| H4 | Sprint Review (CI verts, validation R-7) |
| H5 | approbation escalade API payante |
| H6 | résolution conflit Git (intervention manuelle) |

## E-x — Phases du flux Agile

| Code | Signification |
|------|---------------|
| E1 | idéation, Gros Ticket |
| E2 | architecture, DoD |
| E3 | Sprint Backlog |
| E4 | exécution code, sprint |
| E5 | tests, CI local |
| E6 | clôture sprint, merge |
| HOTFIX | correctif urgent depuis main |

## N0, N1, N2 — Niveaux de cascade IA

| Code | Niveau |
|------|--------|
| N0 | local Ollama |
| N1 | cloud gratuit (Gemini) |
| N2 | cloud payant (Claude) |

## CI 1, CI 2 — Pipelines d'intégration

| Code | Cible |
|------|-------|
| CI 1 | feature→develop (GitHub Actions) |
| CI 2 | develop→main (GitHub Actions) |

## Acronymes

| Acronyme | Signification |
|----------|---------------|
| DoD | Definition of Done (critères d'acceptation) |
| ADR | Architecture Decision Record (décision d'architecture) |
| RAG | Recherche sémantique (contexte code + docs) |
| MCP | Model Context Protocol (partage contexte IDE) |
| BaseStore | Mémoire long terme partagée (décisions, sprints) |
| CDC | Cahier des charges (gabarit Gros Ticket) |
| V.A.R. | Valeur Ajoutée Rétrospective |

## F1–F10 — Règles fonctionnelles

| Code | Règle |
|------|-------|
| F1 | sync_artifacts cron (dérive Architecture.md) |
| F2 | détection changement architectural (force_architectural_change) |
| F4 | projet en pause (purge checkpoints, protect-active-sprints) |
| F5 | notification interrupt > 48h |
| F6 | status.py multi-projets |
| F7 | AGILE_DEFER_INDEX (indexation différée, conflit GPU) |
| F8 | cascade échec N0 → escalade N1/N2 |
| F9 | write_file atomique |
| F10 | AGILE_BASESTORE_STRICT (résilience BaseStore) |

## Références sections (III.8)

| Code | Contenu |
|------|---------|
| III.8-A | load_context, init thread |
| III.8-B | Human-in-the-Loop, procédure interrupts |
| III.8-C | Pipeline indexation RAG, AGILE_DEFER_INDEX |
| III.8-D | Branches Git (feature, develop, hotfix) |
| III.8-E | sprint_complete, merge_to_main |
| III.8-F | CI 1, CI 2, GitHub Actions |
| III.8-H | E4, tools R-4/R-5 |
| III.8-I | Self-Healing R-6→R-4 |
| III.8-J | Stratégie GPU, OLLAMA_KEEP_ALIVE |
| III.8-K | LangSmith |
| III.8-L | Purge checkpoints, rétention |
| III.8-M | Clôture projet |
| III.8-N | build_docs |
| III.8-O | sync_artifacts, ADRs, DoD versionnée |
| III.8-P | status.py |

*Note : Dans les rapports de simulation, N1/N2 peuvent désigner des corrections (ex. N1 multi-projets) et non les niveaux de cascade.*

## Corrections simulations (référence Annexe B)

Codes des problèmes identifiés et corrections intégrées dans le spec. Voir `specs/simulations/` et Annexe B.

| Simulation | Codes | Thème |
|------------|-------|-------|
| 006 | U1–U8 | DoD, rejected, indexation GPU, H4 trigger, ADRs, sprint_number, GitHub Actions, clôture |
| 007 | V1–V7 | H5 sémantique, load_context, E2, branches Git, DoD versionnée, H4 rejected |
| 008 | W1–W6 | Entry point, needs_architecture_review, BaseStore DoD, CI failure, hotfix, projects.json |
| 009 | X1–X4 | PR target, push timing, gh run watch, BaseStore strict |
| 010 | Y1–Y5 | Branche develop, gh pr create/checks, merge_to_main, start_phase HOTFIX, mode dégradé |
| 011 | Z1–Z2 | sprint_number ordre CI 2, branch protection |
| 012 | AA1–AA2 | sprint_number mode dégradé, notation H4 |
| 013 | BB1–BB4 | Checklist, W5 vs Y4 hotfix, merge develop, auto_next_sprint timing |
| 014 | CC1–CC3 | OLLAMA_KEEP_ALIVE, recommandations RTX 3060 |
