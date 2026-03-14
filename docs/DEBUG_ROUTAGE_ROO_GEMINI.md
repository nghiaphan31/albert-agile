# Debug : Pourquoi Gemini répond au lieu de qwen2.5-coder local

## Symptôme

Avec « Smart Semantic Routing to LiteLLM » activé, Roo affiche :
`Chemin de routage : worker-free-gemini-2.5-flash (réponse générée)` au lieu de `worker-local-qwen2.5-coder:14b`.

## Cause identifiée (2026-03-14)

**OllamaError 404** : LiteLLM appelle `get_model_info()` et construit une URL incorrecte :
`http://localhost:11434/api/chat/api/show` → 404 Not Found → fallback vers Gemini.

**Correction** : Utiliser l’API OpenAI-compatible d’Ollama (`openai/` + `api_base: http://localhost:11434/v1`) au lieu de `ollama_chat/` pour les modèles qwen3 et worker-local. Cela évite l’appel `get_model_info()` défaillant.

## Procédure de diagnostic

### 1. Capturer les logs du proxy

```bash
# Arrêter le proxy actuel
pkill -f "litellm.*litellm_config"

# Relancer avec debug complet
cd /home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile
LITELLM_DEBUG=1 ./scripts/run_litellm_proxy.sh 4000 2>&1 | tee logs/proxy_debug.log
```

### 2. Lancer une requête depuis Roo

Depuis Roo Code, envoyez une question simple (ex. « code une fonction racine carrée »).

### 3. Examiner les logs

Dans `logs/proxy_debug.log`, cherchez :

- `JSONDecodeError`, `Extra data` : problème de parsing du streaming Ollama
- `timeout`, `TimeoutError` : délai dépassé (timeout actuel : 120s, stream_timeout : 60s)
- `Connection refused` : Ollama injoignable
- toute traceback Python

## Causes probables et pistes de correction

| Cause | Piste de correction |
|-------|---------------------|
| api_key manquant (openai/) | LiteLLM exige `api_key` pour le provider `openai/`. Ajouter `api_key: "ollama"` dans litellm_params (Ollama l'ignore). |
| Erreur de parsing JSON en streaming (Ollama) | Vérifier que `fake_stream: true` est bien défini pour worker-local (et qwen3). Mettre à jour LiteLLM et Ollama. |
| Timeout (contexte long, tools nombreux) | Augmenter `timeout` et `stream_timeout` dans `litellm_config.yaml` pour worker-local. |
| Conflit nomic-embed-text | Le routage sémantique appelle `ollama.embed()`. Si nomic-embed-text charge en même temps que qwen2.5-coder, risque de timeout ou de saturation. |
| Roo pointe ailleurs | Vérifier que Roo utilise bien `http://localhost:4000` (SSH Remote = localhost sur la machine distante). |

## Test direct

```bash
# Test sans Roo — doit fonctionner
curl -s -X POST http://localhost:4000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-1234" \
  -d '{"model":"worker-local-qwen2.5-coder:14b","messages":[{"role":"user","content":"1+1=?"}],"stream":true}' | head -5
```

Si ce test réussit mais Roo obtient Gemini, la différence vient du format ou du volume des requêtes Roo (tools, contexte long).
