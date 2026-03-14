# Guide : Test Tool Calling qwen3:14b via LiteLLM Proxy

*Dernière mise à jour : 2026-03-14*

Référence : [`scripts/test_qwen3_tool_calling.py`](../scripts/test_qwen3_tool_calling.py)

## Contexte

Roo Code utilise le proxy LiteLLM en mode streaming (`stream: true`). Pour les modèles Ollama locaux, `fake_stream: true` est activé dans `config/litellm_config.yaml` : LiteLLM fait une requête non-streaming en interne, puis simule un flux SSE.

Des boucles anormales ont été observées dans Roo avec `worker-local-qwen3:14b`. Ce script diagnostique les causes potentielles à travers 3 couches d'abstraction et 5 scénarios représentatifs (S1-S4 : prompts courts ; S5 : contexte long ~30K tokens + historique multi-turn).

## Architecture du test

```
  3 couches × 5 scénarios (4 courts + 1 contexte long)
  ┌─────────────────────────────────────────────────────────┐
  │ L0 — Ollama direct   :11434/v1   stream=false (baseline)│
  │ L1 — Proxy LiteLLM   :4000       stream=false           │
  │ L2 — Proxy LiteLLM   :4000       stream=true  ← Roo     │
  └─────────────────────────────────────────────────────────┘
  ┌─────────────────────────────────────────────────────────┐
  │ S1 — Tâche simple       → attempt_completion             │
  │ S2 — Tâche ambiguë      → ask_followup_question          │
  │ S3 — Stress think tokens (prompt anti-XML)              │
  │ S4 — Suite complète tools Roo (5 outils disponibles)    │
  │ S5 — Contexte long ~30K tokens + historique multi-turn  │
  └─────────────────────────────────────────────────────────┘
```

Pour chaque test, 6 checks sont appliqués :

| Check | Ce qui est vérifié |
|---|---|
| `think_tokens_absent` | Aucun `<think>...</think>` dans `content` ou `arguments` |
| `tool_calls_json_valid` | Arguments de chaque tool_call parseable en JSON |
| `follow_up_array` | `ask_followup_question.follow_up` est un array `len >= 2` |
| `finish_reason_valid` | `finish_reason` ∈ `{stop, tool_calls, length}` |
| `expected_tool_called` | Le bon outil est appelé (quand une attente est définie) |
| `signature_present` | Signature de routage présente (L1, L2 uniquement) |
| `h3_finish_reason_in_chunks` | `finish_reason` trouvé dans les chunks SSE (L2 uniquement) |

## Prérequis

```bash
# 1. Ollama avec qwen3:14b
ollama pull qwen3:14b

# 2. Proxy LiteLLM sur :4000
./scripts/run_litellm_proxy.sh 4000
```

## Utilisation rapide

```bash
# Toutes les couches, 3 répétitions par test (durée ~3min)
.venv/bin/python scripts/test_qwen3_tool_calling.py

# Stress test L2 (chemin exact Roo) — 10 répétitions (durée ~3min)
.venv/bin/python scripts/test_qwen3_tool_calling.py --layer 2 --repeat 10

# Scénario isolé
.venv/bin/python scripts/test_qwen3_tool_calling.py --scenario 2 --repeat 5

# Contexte long ~30K tokens + historique multi-turn (S5)
.venv/bin/python scripts/test_qwen3_tool_calling.py --layer 2 --scenario 5 --repeat 5

# Afficher les réponses JSON brutes pour inspection manuelle
.venv/bin/python scripts/test_qwen3_tool_calling.py --layer 2 --scenario 1 --repeat 1 --verbose

# Tester un autre modèle
.venv/bin/python scripts/test_qwen3_tool_calling.py --proxy-model worker-local-qwen2.5-coder:14b

# Paramètres complets
.venv/bin/python scripts/test_qwen3_tool_calling.py --help
```

## Résultats de référence (2026-03-14)

Run de référence : 3 couches × 4 scénarios × 3 répétitions + stress L2 × 10 répétitions.

| Couche | Tests | Résultat |
|---|---|---|
| L0 — Ollama direct | 12/12 | ✅ 100% |
| L1 — Proxy non-streaming | 20/20 | ✅ 100% |
| L2 — Proxy fake_stream (Roo) | 40/40 | ✅ 100% |
| L2 — S5 contexte long ~30K tokens + multi-turn | 5/5 | ✅ 100% |

### Hypothèses diagnostiquées

| Hypothèse | Statut | Détail |
|---|---|---|
| H1 — `_fix_tool_calls` absent du chemin streaming | **INFIRMÉE** | `tool_calls_json_valid` et `follow_up_array` à 100% sur L1 et L2. Pas de différence. |
| H2 — tokens `<think>` contaminent content/arguments | **INFIRMÉE** | 0/52 tests avec fuite de tokens `<think>`. Ollama filtre les reasoning tokens via l'API `/v1`. |
| H3 — `finish_reason` incorrect dans les chunks fake_stream | **INFIRMÉE** | `finish_reason` présent sur 100% des runs, toujours sur le bon chunk (`fr='tool_calls'`, 1 chunk). |

### Observation : signature absente en non-streaming + tool_calls

La fonction `_append_model_signature` (non-streaming) ne peut pas injecter dans `content=None` quand la réponse contient uniquement des `tool_calls`. **Ce n'est pas une cause de boucle** — c'est une limitation cosmétique connue. En streaming (L2), la signature est injectée dans le `delta.content` du dernier chunk, ce qui fonctionne toujours.

## Workflow de diagnostic lors d'une boucle Roo

Si tu observes une boucle dans Roo avec qwen3:14b, voici les étapes :

### Étape 1 — Capturer la requête exacte

```bash
# Relancer le proxy avec le log de routage activé
ROO_DEBUG_LOG="$(pwd)/logs/roo_debug.log" ./scripts/run_litellm_proxy.sh 4000
```

Dans `logs/roo_debug.log`, chaque échange Roo → proxy → modèle est tracé avec le modèle entrant (`model_in`) et le modèle réel utilisé (`model_out`).

Pour capturer la requête HTTP complète, activer le debug LiteLLM :

```bash
LITELLM_DEBUG=1 ./scripts/run_litellm_proxy.sh 4000 2>&1 | tee logs/proxy_debug.log
```

Dans `logs/proxy_debug.log`, chercher `LiteLLM completion()` pour trouver les paramètres envoyés au modèle au moment de la boucle.

### Étape 2 — Ajouter un scénario S5 reproduisant la boucle

Ouvrir `scripts/test_qwen3_tool_calling.py` et ajouter dans le dictionnaire `SCENARIOS` :

```python
5: {
    "name": "S5 - Reproduction boucle (issu logs Roo)",
    "messages": [
        {"role": "system", "content": "<system_prompt_depuis_logs>"},
        {"role": "user", "content": "<message_utilisateur>"},
        # Ajouter l'historique complet si présent dans les logs
    ],
    "tools": [TOOL_READ_FILE, TOOL_WRITE_FILE, TOOL_ATTEMPT_COMPLETION, TOOL_ASK_FOLLOWUP],
    "tool_choice": "required",
    "expect_tool": None,
},
```

### Étape 3 — Exécuter en mode verbose sur L2

```bash
.venv/bin/python scripts/test_qwen3_tool_calling.py --layer 2 --scenario 5 --repeat 5 --verbose
```

La sortie verbose affiche le JSON brut de chaque réponse pour inspection.

### Étape 4 — Interpréter le rapport

```
[PASS/FAIL] [L2-Proxy-FakeStream] S5 #01 — S5 - Reproduction boucle
  ✓ think_tokens_absent
  ✗ tool_calls_json_valid  → attempt_completion: Expecting value: ... ← JSON invalide
  ✓ follow_up_array        → skipped
  ✓ finish_reason_valid    → finish_reason='tool_calls'
  ✗ expected_tool_called   → expected 'attempt_completion', got []
  ✓ signature_present      → found in content
  ✓ h3_finish_reason_in_chunks
```

Un `✗` sur `tool_calls_json_valid` indique que le modèle a émis des arguments malformés → les tool_calls sont filtrés par `_fix_tool_calls` → Roo reçoit un message vide sans outil → boucle.

## Causes probables non couvertes par ces tests

S1-S4 utilisent des prompts courts (< 500 tokens) ; S5 couvre le contexte long (~30K tokens). Les boucles Roo réelles impliquent souvent :

| Cause | Signature dans les tests | Piste |
|---|---|---|
| Contexte long (> 28K tokens) | **Couvert par S5** (5/5 au 2026-03-14) — augmenter `--repeat` pour plus de confiance | Si échecs : augmenter `num_ctx` ou raccourcir le contexte Roo |
| Historique multi-turn profond (> 6 tours) | S5 couvre 3 tours — insuffisant pour reproduire une session Roo longue | Ajouter S6 avec 6-8 turns tool_call→résultat→tool_call |
| Outil Roo inconnu du modèle | `expected_tool_called` renvoie un nom d'outil inattendu | Vérifier que `TOOL_SCHEMA_PROMPT` couvre bien l'outil |
| Compétition GPU (nomic-embed-text + qwen3) | Timeouts L0 uniquement | Surveiller `nvidia-smi` pendant les tests |

## Scripts de test associés

| Script | Usage |
|---|---|
| `scripts/test_qwen3_tool_calling.py` | Ce guide — test structuré 3 couches × 5 scénarios (S5 = contexte long ~30K tokens) |
| `scripts/test_litellm_hooks_integration.py` | Test HTTP ad-hoc du proxy (1 requête, output console) |
| `scripts/test_worker_local_curl.sh` | Test curl minimal (`worker-local-qwen2.5-coder:14b`, non-streaming) |
| `tests/test_litellm_hooks.py` | Tests unitaires des hooks (pytest, sans proxy ni Ollama) |
