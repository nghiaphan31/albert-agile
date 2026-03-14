# Debug : Pourquoi Gemini répond au lieu de qwen2.5-coder local

## Symptôme

Avec « Smart Semantic Routing to LiteLLM » activé, Roo affiche :
`Chemin de routage : worker-free-gemini-2.5-flash (réponse générée)` au lieu de `worker-local-qwen2.5-coder:14b`.

## Cause

Le fallback vers Gemini indique que **worker-local (Ollama) échoue** avant que la réponse ne soit envoyée. Le routage vers worker-local est bien effectué, mais l’appel à Ollama provoque une erreur → fallback automatique vers worker-free-gemini-2.5-flash.

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
| Erreur de parsing JSON en streaming (Ollama) | Vérifier que `fake_stream: true` est bien défini pour worker-local (déjà fait). Mettre à jour LiteLLM et Ollama. |
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
