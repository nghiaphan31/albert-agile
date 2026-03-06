# Règles et Lois pour les Agents Agile — Synthèse opérationnelle

Référence : [NOMENCLATURE_R_H_E.md](NOMENCLATURE_R_H_E.md), [SYNTHESE_REGLES_ET_LOIS_ISSUS_DE_ALBERT_CORE_JUST_FOR_REFERENCE](../SYNTHESE_REGLES_ET_LOIS_ISSUS_DE_ALBERT_CORE_JUST_FOR_REFERENCE).

## 1. Mapping Lois → Agents (R-x)

### Lois transverses (tous les agents)


| Code   | Nom                     | Principe                                                                                            |
| ------ | ----------------------- | --------------------------------------------------------------------------------------------------- |
| L0     | Auto-application        | Ces lois s'appliquent à tout projet et à la conception des agents.                                  |
| L3     | Rétrofit permanent      | Toute découverte technique majeure → d'abord mettre à jour `/specs`, valider, puis adapter le code. |
| L7     | Transparence            | Logs exhaustifs, attribution du modèle IA dans les manifestes.                                      |
| L8     | Non-destruction         | Interdiction de `eval`, `exec`, `rm -rf` hors périmètre.                                            |
| L9     | Zéro-hardcode           | Aucun chemin absolu ni secret en dur. Variables d'environnement ou `project.json`.                  |
| L11    | Env explicite           | `load_dotenv()` obligatoire AVANT toute utilisation d'API ou `os.environ`.                          |
| L18    | Arrêt sur contradiction | Si deux specs se contredisent : citer les deux, expliquer l'impact, proposer, attendre Sign-off.    |
| L-ANON | Anonymisation cloud     | Aucune donnée personnelle ne quitte Calypso vers le cloud sans anonymisation.                       |


### Lois par rôle


| Rôle                               | Codes            | Application                                                             |
| ---------------------------------- | ---------------- | ----------------------------------------------------------------------- |
| R-0 (Business Analyst IA)         | L1, L4           | Anti-précipitation, Gabarit CDC (Cahier des charges)                    |
| R-2 (System Architect IA)         | L2, L5, L18      | Traçabilité verticale, Confinement spatial, Arrêt sur contradiction     |
| R-3 (Scrum Master IA)             | L6               | V.A.R. — Plans exécutables, nomenclature 4D                             |
| R-4 (Dev Team IA)                 | L8, L9, L19, L21 | Non-destruction, Zéro-hardcode, Idempotence, Doc-as-code + Règles Tests |
| R-5 (Release Manager IA)          | L7, L8           | Transparence, Non-destruction (git allowlist)                           |
| R-6 (QA & DevOps IA)              | L15, L21         | Intégration E2E, Doc-as-code + Règles Tests                             |


## 2. Règles de mise en forme


| Règle | Objet                     | Format                                                                                            |
| ----- | ------------------------- | ------------------------------------------------------------------------------------------------- |
| **A** | Commandes / scripts       | Code fence ````bash` — une commande par ligne, bouton Copy GitHub.                                |
| **B** | Tableaux / spécifications | Markdown standard avec pipes `|`. Backlog, Architecture, Sprint Backlog en **tableaux Markdown**. |
| **C** | Prompts IA                | Templates en bloc texte avec frontmatter YAML (config/prompts/ ou graph/prompts/).                |
| **D** | Doc-in-code               | Docstrings obligatoires sur éléments publics ; doc générée (sphinx-build) si API modifiée.        |


## 3. Règles Tests

- **Ordre pipeline E5** : build_docs → unit → intégration → E2E
- **L21 Doc-as-code** : R-6 refuse tout commit R-4 sans docstrings sur éléments publics, ou modification API sans mise à jour doc générée (si `BUILD_DOCS_REQUIRED=true`)
- **Self-Healing** : premier échec → rebouclage R-6→R-4 ; max 3 itérations (`SELF_HEALING_MAX_ITERATIONS=3`)

## 4. Validation rôles humains R-1 (Product Owner) / R-7 (Stakeholder)

- **R-1** : Valide Epic (H1), Sprint Backlog (H3), escalade API payante (H5)
- **R-7** : Valide Architecture + DoD (H2), Sprint Review (H4), conflits Git (H6), contradictions (L18)

## 5. Structure nobles / opérationnels (plan lois §3.4)

### Nobles (versionnés)

- `/specs`, `/src`, `/docs`
- `Architecture.md`, `Product Backlog.md`
- ADRs (Architecture Decision Record)

### Opérationnels (non versionnés)

- `/.operations` : artefacts temporaires, logs, chroma_db local au projet

### Quarantaine IA

- R-2 (System Architect IA) et R-4 (Dev Team IA) : artefacts IA en `.operations/artifacts` avant promotion par R-1 (Product Owner) / R-7 (Stakeholder).

