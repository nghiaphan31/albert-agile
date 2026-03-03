# Graphe Agile — Vue enrichie (nœuds et arêtes)

Diagramme Mermaid avec le contenu détaillé des nœuds et des conditions des arêtes.

```mermaid
flowchart TD
    subgraph Entry [Entrée]
        __start__([Démarrage])
    end

    subgraph LoadCtx [Chargement contexte]
        load_context["load_context<br/>────────────<br/>• Lit config/projects.json<br/>• Charge BaseStore: adr_counter, sprint_number, dod<br/>• SprintBacklog synthétique si HOTFIX<br/>• Route selon start_phase"]
    end

    subgraph Agents [Agents IA — Albert]
        r0["r0 — R-0 Albert Business Analyst<br/>────────────<br/>• Produit Epic (CDC)<br/>• Cascade: gemma → Gemini → Claude Opus<br/>• Interrupt H1 (validation Product Owner)<br/>• L1 Anti-précipitation, L4 Gabarit CDC"]
        r2["r2 — R-2 Albert System Architect<br/>────────────<br/>• Architecture + Definition of Done<br/>• RAG: contexte Backlog/Architecture<br/>• L18 spec_contradiction si contradiction<br/>• Interrupt H2 (validation Stakeholder)"]
        r3["r3 — R-3 Albert Scrum Master<br/>────────────<br/>• Découpe Sprint Backlog<br/>• RAG: Backlog, Architecture<br/>• Interrupt H3 (validation Product Owner)"]
        r4["r4 — R-4 Albert Dev Team<br/>────────────<br/>• Exécution code (phase E4)<br/>• Tools: read_file, write_file, run_shell<br/>• RAG: contexte code<br/>• Cascade: qwen → Gemini → Claude Sonnet"]
        r5["r5 — R-5 Albert Release Manager<br/>────────────<br/>• Git: checkout, add, commit, merge<br/>• gh pr create, gh pr merge<br/>• Cascade qwen/Gemini/Claude"]
        r6["r6 — R-6 Albert QA et DevOps<br/>────────────<br/>• Pipeline E5: build_docs → unit → intégration → E2E<br/>• L21 Doc-as-code<br/>• Interrupt H4 (Sprint Review Stakeholder)<br/>• Self-Healing: si tests fail, → r4 (max 3x puis H5)"]
    end

    subgraph EndNode [Sortie]
        __end__([Fin])
    end

    __start__ --> load_context

    load_context -.->|"start_phase=E1<br/>→ E1 Idéation"| r0
    load_context -.->|"start_phase=E3<br/>→ E3 Sprint Backlog"| r3
    load_context -.->|"start_phase=HOTFIX<br/>→ Correctif urgent"| r4

    r0 -.->|"H1 approved<br/>Epic validé par R-1"| r2
    r0 -.->|"H1 rejected<br/>Feedback → reboucle"| r0

    r2 -.->|"H2 approved<br/>Architecture validée par R-7"| r3
    r2 -.->|"H2 rejected<br/>Feedback → reboucle"| r2

    r3 -.->|"H3 approved<br/>Sprint Backlog validé par R-1"| r4
    r3 -.->|"H3 rejected<br/>Feedback → reboucle"| r3

    r4 -->|"Direct"| r5
    r5 -->|"Direct"| r6

    r6 -.->|"H4 approved<br/>Sprint Review OK"| __end__
    r6 -.->|"H4 rejected<br/>Self-Healing → correction"| r4
    r6 -.->|"h5_rejected<br/>Escalade API refusée"| __end__

    classDef loadStyle fill:#e6f3ff
    classDef agentStyle fill:#f2f0ff
    class load_context loadStyle
    class r0,r2,r3,r4,r5,r6 agentStyle
```

## Légende

| Code | Signification |
|------|---------------|
| **R-0** | Albert Business Analyst |
| **R-2** | Albert System Architect |
| **R-3** | Albert Scrum Master |
| **R-4** | Albert Dev Team |
| **R-5** | Albert Release Manager |
| **R-6** | Albert QA & DevOps |
| **R-1** | Nghia Product Owner (humain) |
| **R-7** | Nghia Stakeholder (humain) |
| **H1** | Validation Epic |
| **H2** | Validation Architecture + DoD |
| **H3** | Validation Sprint Backlog |
| **H4** | Sprint Review |
| **H5** | Approbation escalade API payante |

## Arêtes

- **Plein (→)** : arête directe, pas de condition
- **Pointillé (-.->)** : arête conditionnelle (routing selon l'état)
