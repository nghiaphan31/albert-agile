# Modèles plus performants sur RTX 5060 Ti 16G

*Plan de test et adoption de modèles Ollama compatibles 16 Go VRAM.*

---

## Contexte actuel

| Usage | Modèle actuel | VRAM | Remarque |
|-------|---------------|------|----------|
| Code (R3-R6) | `qwen2.5-coder:3b` | ~2 Go | Défaut en prod (7b instable avec structured output) |
| Idéation (R0-R2) | `qwen2.5-coder:3b` | ~2 Go | gemma3:12b provoque panic Ollama avec Pydantic |
| Specs | qwen2.5-coder:7b, gemma3:12b | ~8 Go | Non utilisés en prod |

Avec 16 Go VRAM, on peut monter en gamme tout en gardant de la marge pour nomic-embed-text (~1 Go) et le système.

---

## Recommandations par usage

### Tier 2 (code) — R3, R4, R5, R6

| Modèle | VRAM estimée | Intérêt | Risque |
|--------|--------------|---------|--------|
| **deepseek-coder-v2:16b** | ~9 Go | MoE, niveau GPT-4 Turbo en code, 160K context | Tester structured output |
| **qwen2.5-coder:14b** | ~9–10 Go | Meilleur que 7b, même famille | Stable avec Pydantic |
| **qwen2.5-coder:7b** | ~8 Go | Baseline actuelle spec | Déjà connu |

**Recommandé en premier** : `qwen2.5-coder:14b` (stabilité Pydantic) puis `deepseek-coder-v2:16b` (perf max).

### Tier 1 (idéation / architecture) — R0, R2

| Modèle | VRAM estimée | Intérêt | Risque |
|--------|--------------|---------|--------|
| **qwen2.5:14b** | ~9 Go | Raisonnement, multi-langue | Compatible structured output |
| **qwen3:14b** | ~9.3 Go | Thinking natif, structured output validé | Plus lent (~2×) |
| **qwen2.5:32b** (Q4) | ~18–20 Go | Forte montée en gamme | OOM probable sur 16 Go |
| **gemma3:12b-it-q4_K_M** | ~8 Go | Spécifié dans les specs | Panic Ollama connu (llm_factory) |

**Recommandé** : `qwen2.5:14b` (défaut). Option thinking : `qwen3:14b` — voir [Strategie_Modeles_LLM_Thinking_Albert_Agile.md](Strategie_Modeles_LLM_Thinking_Albert_Agile.md).

---

## Tests CLI (minimum)

### 1. Pull et vérification

```bash
# Modèles à tester
ollama pull qwen2.5-coder:14b
ollama pull deepseek-coder-v2:16b
ollama pull qwen2.5:14b
ollama pull qwen2.5:14b-instruct-q4_K_M   # si disponible
```

### 2. Test direct Ollama (CLI)

```bash
# Code (Tier 2)
ollama run qwen2.5-coder:14b "Écris une fonction Python qui calcule le n-ième nombre de Fibonacci (récursif puis itératif)."
ollama run deepseek-coder-v2:16b "Écris une fonction Python qui calcule le n-ième nombre de Fibonacci."

# Idéation (Tier 1)
ollama run qwen2.5:14b "En 3 bullet points, résume les risques d'une migration monolithe vers microservices."
```

### 3. Test avec structured output (comme le graphe)

Utiliser `scripts/test_structured_cli.py` et les variables d'environnement. Depuis la racine du projet, avec venv activé et `PYTHONPATH=.` (ou `./scripts/test_models_cli.sh structured`).

```bash
# Depuis la racine, venv activé
source .venv/bin/activate

# Tier 2 — code (sprint backlog)
PYTHONPATH=. AGILE_TIER2_N0_MODEL=qwen2.5-coder:14b python scripts/test_structured_cli.py sprint-backlog --tier tier2 \
  -p "Prépare un sprint backlog d'une semaine pour une API REST de gestion de tâches."

# Puis deepseek
PYTHONPATH=. AGILE_TIER2_N0_MODEL=deepseek-coder-v2:16b python scripts/test_structured_cli.py sprint-backlog --tier tier2 \
  -p "Prépare un sprint backlog d'une semaine pour une API REST de gestion de tâches."

# Tier 1 — idéation (epic)
PYTHONPATH=. AGILE_TIER1_N0_MODEL=qwen2.5:14b python scripts/test_structured_cli.py epic --tier tier1 \
  -p "Propose une Epic pour un système de gestion de tâches avec priorisation."

# Architecture
PYTHONPATH=. AGILE_TIER1_N0_MODEL=qwen2.5:14b python scripts/test_structured_cli.py architecture --tier tier1 \
  -p "Décris l'architecture logique pour une app de notes collaborative."
```

Ou : `./scripts/test_models_cli.sh structured`

---

## Prompts de validation

### Code (Tier 2)

| ID | Prompt | Critère |
|----|--------|---------|
| C1 | "Écris une fonction Python `def fib(n: int) -> int` avec docstring et type hints. Pas de récursif." | Code valide, typé |
| C2 | "Génère un test pytest pour une fonction `def add(a: int, b: int) -> int`. Utilise des parametrize pour 3 cas." | Structure pytest correcte |
| C3 | "Découpe en tickets atomiques (titre + description courte) le développement d'une API REST CRUD pour des 'projects'." | JSON structuré exploitable |

### Idéation / architecture (Tier 1)

| ID | Prompt | Critère |
|----|--------|---------|
| I1 | "Propose une Epic (titre, problème, solution en 2 phrases, critères d'acceptation) pour une app de suivi de dépenses personnelles." | Cohérence Epic Agile |
| I2 | "Décris en 5 composants l'architecture d'un backend Python (FastAPI) avec base PostgreSQL et cache Redis." | Composants logiques clairs |
| I3 | "Liste 3 risques techniques d'un passage de monolithe à microservices, avec une mitigation par risque." | Raisonnement structuré |

---

## Script de test automatisable (optionnel)

Créer `scripts/test_models_cli.sh` qui :

1. Pour chaque modèle recommandé : `ollama run <model> "<prompt C1>"` et vérifier que la sortie contient `def fib` ou équivalent
2. Pour les schemas structurés : lancer `test_structured_cli.py` avec `AGILE_TIER*_N0_MODEL=<model>` et vérifier un exit code 0 + JSON valide

---

## Ordre d'exécution conseillé

1. Pull `qwen2.5-coder:14b` + tests C1, C2, C3 en CLI directe
2. Test structured : `AGILE_TIER2_N0_MODEL=qwen2.5-coder:14b` + `test_structured_cli.py sprint-backlog`
3. Si OK : pull `deepseek-coder-v2:16b` et répéter
4. Pull `qwen2.5:14b` + tests I1, I2, I3 en CLI
5. Test structured : `AGILE_TIER1_N0_MODEL=qwen2.5:14b` + `test_structured_cli.py epic` et `architecture`
6. Documenter les résultats (quel modèle garde structured output sans panic) avant de modifier les specs

---

## Résultats des tests (2026-03-06)

| Modèle | Usage | Structured output | Statut |
|--------|-------|-------------------|--------|
| qwen2.5-coder:14b | Tier2 (sprint-backlog) | OK | Validé |
| deepseek-coder-v2:16b | Tier2 (sprint-backlog) | OK | Validé |
| qwen2.5:14b | Tier1 (epic, architecture) | OK | Validé |

Tous les modèles recommandés fonctionnent sans panic Ollama avec `with_structured_output` (Pydantic).

---

## Fichiers impactés (si adoption)

- `graph/llm_factory.py` : valeurs par défaut de `AGILE_TIER1_N0_MODEL` et `AGILE_TIER2_N0_MODEL`
- `docs/HARDWARE_GPU.md` : section "Profil recommandé" — modèles conseillés
- `specs/Specifications Ecosysteme Agile Agent IA.md` : section 3.2 (après validation terrain)
