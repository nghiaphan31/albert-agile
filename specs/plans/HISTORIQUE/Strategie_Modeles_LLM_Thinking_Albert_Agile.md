# Stratégie modèles LLM — Thinking / Chain of Thought (albert-agile)

*Document de stratégie pour l’adoption de modèles avec thinking natif ou CoT dans l’écosystème albert-agile. Plan d’action à exécuter, conclusions à documenter après validation.*

**Références** : [Modeles_Performants_RTX5060_16G.md](Modeles_Performants_RTX5060_16G.md), [HARDWARE_GPU.md](../../docs/HARDWARE_GPU.md), [graph/llm_factory.py](../../graph/llm_factory.py).

---

## 1. Contexte

### 1.1 Pourquoi un modèle thinking / CoT ?

| Phase / Rôle | Tâche | Intérêt du thinking |
|--------------|-------|---------------------|
| R-0 (Business Analyst) | Produire l’Epic | Raisonnement structuré, besoins → critères d’acceptation |
| R-2 (System Architect) | Architecture + DoD | Raisonnement explicite, détection d’incohérences |
| R-3 (Scrum Master) | Sprint Backlog | Priorisation et découpage plus logiques |
| R-4 (Dev Team) | Code | Décomposition du problème avant implémentation |

Pour les décisions importantes (Epic, architecture, backlog), une chaîne de raisonnement explicite améliore la qualité et la traçabilité.

### 1.2 Thinking natif vs CoT par prompt

- **Thinking natif (Ollama)** : bloc `thinking` séparé de la réponse finale (qwen3, deepseek-r1, gpt-oss)
- **CoT par prompt** : demander "Réfléchis étape par étape" — qwen2.5 le fait, mais tout est dans un seul bloc

### 1.3 État actuel (2026-03)

| Tier | Modèles utilisés | Thinking natif |
|------|------------------|----------------|
| Tier 1 (R-0, R-2) | qwen2.5:14b | Non |
| Tier 2 (R-3 à R-6) | qwen2.5-coder:14b | Non |

---

## 2. Contraintes techniques

| Contrainte | Impact |
|------------|--------|
| **Structured output (Pydantic)** | EpicOutput, ArchitectureOutput, SprintBacklogOutput. Le modèle doit produire du JSON valide. Avec thinking natif, la réponse "content" doit être parsable ; le bloc thinking est ignoré par LangChain. |
| **langchain-ollama** | Vérifier si `ChatOllama` supporte le paramètre `think` et comment la réponse est exposée (champ `thinking` vs `content`). |
| **Latence** | Thinking = plus de tokens générés = réponses plus lentes. |
| **VRAM (RTX 5060 Ti 16G)** | qwen3:14b ~9.3 GB, deepseek-r1:14b ~9 GB → OK. |

---

## 3. Options stratégiques

### Option A — Modèle unique thinking par défaut

- **Modèle** : qwen3:14b ou deepseek-r1:14b (thinking natif) pour tous les rôles
- **Avantages** : Raisonnement cohérent partout, traçabilité
- **Inconvénients** : Plus lent, structured output à valider, qwen3-coder moins validé pour le code que qwen2.5-coder

### Option B — Par tier (recommandé à valider)

| Tier | Rôles | Modèle proposé | Raison |
|------|-------|----------------|--------|
| Tier 1 | R-0, R-2 | qwen3:14b ou deepseek-r1:14b | Raisonnement structuré pour Epic / architecture |
| Tier 2 | R-3 à R-6 | qwen2.5-coder:14b | Vitesse + structured output validé pour le code |

- **Avantages** : Chaque rôle utilise le modèle le plus adapté
- **Inconvénients** : Configuration plus complexe, possible swapping de modèles (garder OLLAMA_KEEP_ALIVE)

### Option C — Configuration flexible (env + fallback)

Variables d’environnement :

- `AGILE_TIER1_N0_MODEL` — défaut : `qwen3:14b` (ou `qwen2.5:14b` si thinking non supporté)
- `AGILE_TIER2_N0_MODEL` — défaut : `qwen2.5-coder:14b`
- `AGILE_USE_THINKING` — activer/désactiver le mode thinking (si supporté par langchain-ollama)

Matrice de choix documentée pour guider la configuration selon le profil (vitesse vs qualité de raisonnement).

---

## 4. Matrice de choix (pros / cons)

| Modèle | Thinking natif | Structured output | Code | Vitesse | 16 Go VRAM | Recommandation |
|--------|----------------|-------------------|------|---------|------------|----------------|
| qwen2.5:14b | Non (CoT par prompt) | OK | OK | Rapide | OK | Actuel Tier 1, stable |
| qwen2.5-coder:14b | Non | OK (validé) | Très bon | Rapide | OK | Actuel Tier 2, garder |
| qwen3:14b | Oui | À valider | OK | Plus lent | OK | Candidat Tier 1 thinking |
| deepseek-r1:14b | Oui | À valider | OK | Plus lent | OK | Alternative Tier 1 |
| gpt-oss:20b | Oui (low/med/high) | À valider | OK | Lent | Limite (14 GB) | Option avancée |

---

## 5. Plan d’action (exécuté)

- [x] **5.1** Vérifier si `langchain-ollama` / `ChatOllama` supporte le paramètre `think` (Ollama API)
- [x] **5.2** Tester qwen3:14b en Tier 1 avec structured output (EpicOutput, ArchitectureOutput) — valider que le parsing Pydantic fonctionne
- [ ] **5.3** Tester deepseek-r1:14b en Tier 1 (non exécuté : modèle non pull sur Calypso)
- [x] **5.4** Documenter les résultats
- [x] **5.5** Mettre à jour `graph/llm_factory.py` — qwen3:14b documenté comme option
- [x] **5.6** Mettre à jour les docs avec les conclusions

---

## 6. Conclusions (2026-03)

### 6.1 Résultats des tests

| Test | Modèle | Résultat | Latence |
|------|--------|----------|---------|
| 5.1 langchain-ollama | — | OK | ChatOllama expose `reasoning` (maps to `think`) |
| 5.2 EpicOutput | qwen3:14b | OK | ~68 s |
| 5.2 ArchitectureOutput | qwen3:14b | OK | ~38 s |
| 5.3 EpicOutput | deepseek-r1:14b | Non testé | Modèle non installé (404) |

**langchain-ollama** : Le paramètre `reasoning` (équivalent Ollama `think`) est supporté. Passer `reasoning=True` à `ChatOllama` pour activer le bloc thinking séparé.

### 6.2 Recommandations justifiées

| Tier | Modèle par défaut | Alternative (thinking) | Justification |
|------|-------------------|------------------------|---------------|
| Tier 1 | qwen2.5:14b | qwen3:14b | qwen3:14b validé avec EpicOutput/ArchitectureOutput. Plus lent (~2×) mais thinking natif. |
| Tier 2 | qwen2.5-coder:14b | — | Garder : structured output validé, vitesse, pas de modèle thinking coder validé. |

**Variables d’environnement** :

- `AGILE_TIER1_N0_MODEL=qwen2.5:14b` — défaut (rapide, stable)
- `AGILE_TIER1_N0_MODEL=qwen3:14b` — option thinking pour Epic / architecture
- `AGILE_TIER2_N0_MODEL=qwen2.5-coder:14b` — inchangé
- `AGILE_TIER1_USE_THINKING` — à implémenter si activation du bloc thinking séparé (reasoning=True)

### 6.3 Décisions

- **Tier 1** : Conserver `qwen2.5:14b` par défaut pour la vitesse. `qwen3:14b` est une option validée pour les utilisateurs souhaitant un modèle thinking.
- **Tier 2** : Inchangé (`qwen2.5-coder:14b`).
- **deepseek-r1:14b** : Non testé (non pull). À valider ultérieurement avec `ollama pull deepseek-r1:14b` si besoin.

---

## 7. Références

- [Ollama Thinking](https://docs.ollama.com/capabilities/thinking)
- [Modeles_Performants_RTX5060_16G.md](Modeles_Performants_RTX5060_16G.md)
- [HARDWARE_GPU.md](../../docs/HARDWARE_GPU.md)
- [graph/llm_factory.py](../../graph/llm_factory.py)
- [Specifications Ecosysteme Agile Agent IA.md](../Specifications%20Ecosysteme%20Agile%20Agent%20IA.md)
