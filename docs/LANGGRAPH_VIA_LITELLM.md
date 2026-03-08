# LangGraph via LiteLLM Proxy

## Vue d'ensemble

Lorsque `AGILE_USE_LITELLM_PROXY=true`, le graphe LangGraph (R0–R6) utilise le proxy LiteLLM (`localhost:4000`) au lieu d'appeler directement Ollama, Gemini et Claude. Un seul appel HTTP suffit : le proxy gère la cascade et les fallbacks.

## Architecture

```
┌─────────────────┐     ChatOpenAI          ┌─────────────────────┐
│   LangGraph     │  base_url=localhost:4000│  LiteLLM Proxy      │
│  R0 R2 R3 R4... │ ──────────────────────> │  tier1-n0 / tier2-n0│
└─────────────────┘                         └──────────┬──────────┘
                                                      │
                        ┌─────────────────────────────┼─────────────────────────────┐
                        │                             │                             │
                        ▼                             ▼                             ▼
                  ┌──────────┐                 ┌──────────┐                 ┌──────────┐
                  │  Ollama  │                 │  Gemini  │                 │  Claude  │
                  │ qwen2.5  │                 │ 2.5-flash│                 │ Opus/Sonnet│
                  └──────────┘                 └──────────┘                 └──────────┘
```

## Activation

1. **Lancer le proxy LiteLLM** (port 4000) :
   ```bash
   ./scripts/run_litellm_proxy.sh
   # ou : litellm --config config/litellm_config.yaml --port 4000
   ```

2. **Activer le mode proxy** :
   ```bash
   export AGILE_USE_LITELLM_PROXY=true
   ```

3. **Variables optionnelles** :
   - `AGILE_LITELLM_BASE_URL` : URL du proxy (défaut : `http://localhost:4000/v1`)

## Alias modèles

| Alias      | Primaire        | Fallbacks                |
|-----------|-----------------|---------------------------|
| tier1-n0  | qwen2.5:14b     | gemini → claude-opus      |
| tier2-n0  | qwen2.5-coder:14b| gemini → claude-sonnet   |

## Tests

Exécuter le test structuré avec le proxy :

```bash
export AGILE_USE_LITELLM_PROXY=true
python scripts/test_structured_cli.py
```

Vérifier que le proxy est bien sollicité (logs LiteLLM).

## Limitations

- **Latence** : un appel supplémentaire via le proxy (vs direct).
- **Presidio** : pas intégré au niveau LiteLLM ; L-ANON (anonymisation) reste géré côté cascade si N1/N2 sont utilisés. En mode proxy, un seul niveau est appelé (LiteLLM gère les fallbacks).
- **Ollama warmup** : désactivé en mode proxy (le proxy gère les appels à Ollama).

## Fichiers modifiés

- `graph/llm_factory.py` : `get_llms_tier1()` et `get_llms_tier2()` retournent `(ChatOpenAI, None, None)` si le proxy est activé
- `graph/cascade.py` : skip du warmup Ollama si `AGILE_USE_LITELLM_PROXY`
- `config/litellm_config.yaml` : alias `tier1-n0`, `tier2-n0`, `claude-opus`
- `requirements.txt` : `langchain-openai`
