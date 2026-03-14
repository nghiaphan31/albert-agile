# Plan : Signature modèle en mode streaming via `async_post_call_streaming_iterator_hook`

## 1. Contexte

| Élément | Détail |
|---------|--------|
| **Problème** | La signature `— *généré par {model}*` n'apparaît pas dans les réponses Roo car elle est ajoutée dans `async_post_call_success_hook` (post-call non-streaming), alors que Roo consomme le stream en temps réel — la signature est appliquée trop tard. |
| **Objectif** | Injecter la signature dans le flux streaming pour qu'elle soit visible dans Roo. |
| **Approche** | Utiliser `async_post_call_streaming_iterator_hook` de LiteLLM pour modifier le dernier chunk avant envoi au client. |

---

## 2. Architecture LiteLLM — Hooks streaming

| Hook | Rôle | Paramètres |
|------|------|------------|
| `async_post_call_streaming_hook` | Appelé par chunk (chaîne) | `user_api_key_dict`, `response: str` |
| `async_post_call_streaming_iterator_hook` | Reçoit tout le flux, on peut modifier chaque chunk | `user_api_key_dict`, `response` (async generator), `request_data: dict` → on yield des chunks modifiés |

**Choix** : `async_post_call_streaming_iterator_hook` — permet d'itérer sur tous les chunks, détecter le dernier, et y ajouter la signature avant de le renvoyer au client.

---

## 3. Structure des chunks streaming

Format OpenAI-compatible (ce que LiteLLM stream) :

```
choices[0].delta.content  →  texte du chunk (ou "" si pas de contenu)
choices[0].finish_reason  →  null | "stop" | "length" | ...
```

Le dernier chunk contient typiquement `finish_reason == "stop"`. Ce chunk peut avoir du `content` ou non.

---

## 4. Phases d'implémentation

### Phase 1 — Vérifier la disponibilité du hook

1. Vérifier la version LiteLLM utilisée (correction bug hook streaming dans PR #8627).
2. Confirmer que `async_post_call_streaming_iterator_hook` est bien appelé en mode streaming (doc officielle + test manuel).

---

### Phase 2 — Implémenter la logique dans `litellm_hooks.py`

1. **Ajouter `async_post_call_streaming_iterator_hook`** à la classe `ToolSchemaEnforcer` :
   - Signature : `async def async_post_call_streaming_iterator_hook(self, user_api_key_dict, response, request_data) -> AsyncGenerator`
   - Imports : `from typing import AsyncGenerator` ; `from litellm.types.utils import ModelResponseStream` si nécessaire.

2. **Obtenir le nom du modèle** :
   - Utiliser `request_data.get("model")` (modèle déjà routé par `custom_roo_hook`).
   - Réutiliser `_normalize_to_convention()` si besoin.
   - Créer une fonction utilitaire `_get_model_from_request_data(request_data) -> str` si nécessaire.

3. **Logique d'itération** :
   - `async for chunk in response:`
   - Détecter le **dernier chunk** : `finish_reason in ("stop", "length", "content_filter")`.
   - Sur ce chunk : récupérer `choices[0].delta.content`, y concaténer `MODEL_SIGNATURE.format(model=model_name)`, mettre à jour le chunk.
   - `yield chunk`.

4. **Cas particuliers** :
   - Pas de `choices` ou liste vide → ne pas modifier.
   - Réponse avec tool calls uniquement (pas de content texte) → pas de signature (optionnel).
   - Gérer le format des chunks (objets Pydantic vs dict selon version LiteLLM).

---

### Phase 3 — Cohérence avec post-call non-streaming

1. Conserver `async_post_call_success_hook` pour les réponses **non-streaming** (signature déjà en place).
2. En streaming : seul `async_post_call_streaming_iterator_hook` ajoute la signature.
3. Pas de double signature : les deux chemins sont mutuellement exclusifs.

---

### Phase 4 — Tests

1. **Test manuel** :
   - `curl` avec `"stream": true` sur `/chat/completions`. URL : `http://localhost:PORT/v1/chat/completions` (PORT = `LITELLM_PORT` ou 4000).
   - Vérifier que la signature apparaît à la fin du flux.
2. **Test via Roo** :
   - Demander une réponse longue (ex. explication détaillée).
   - Vérifier que la signature s'affiche en bas de la réponse dans l'UI Roo.
3. **Tests unitaires** (optionnel) :
   - Simuler un flux de chunks et vérifier que la signature n'est ajoutée qu'au dernier chunk pertinent.

---

### Phase 5 — Documentation

1. **`specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md`** :
   - Documenter l'injection de signature en streaming via `async_post_call_streaming_iterator_hook`.
   - Préciser la version LiteLLM minimale requise (correction du bug streaming).

2. **`docs/STATUS_SPEC_STRATEGIE_ROUTAGE.md`** :
   - Mettre à jour la ligne sur la signature modèle : préciser qu'elle s'applique aussi en streaming via `async_post_call_streaming_iterator_hook` dans `litellm_hooks.py`.

3. **`docs/LOG_CONFORMITE_STRATEGIE_ROUTAGE.md`** :
   - Ajouter une entrée pour cette évolution (date, libellé « Signature modèle en streaming »).
   - Fichiers modifiés : `config/litellm_hooks.py`, `specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md`, `docs/STATUS_SPEC_STRATEGIE_ROUTAGE.md`.

4. **`docs/LANGGRAPH_VIA_LITELLM.md`** (optionnel) :
   - Mentionner que la signature est injectée en streaming via le hook dédié.

5. **Version LiteLLM** :
   - Vérifier / fixer la version dans `requirements*.txt` ou `pyproject.toml` pour inclure le correctif du hook streaming.

---

## 5. Récapitulatif des fichiers à modifier

| Fichier | Phase | Action |
|---------|-------|--------|
| `config/litellm_hooks.py` | 2 | Ajouter `async_post_call_streaming_iterator_hook`, logique d'injection sur dernier chunk |
| `specs/plans/Strategie_Routage_Intelligent_Proposition_Gemini.md` | 5 | Documenter la signature en streaming |
| `docs/STATUS_SPEC_STRATEGIE_ROUTAGE.md` | 5 | Mettre à jour conformité (signature streaming) |
| `docs/LOG_CONFORMITE_STRATEGIE_ROUTAGE.md` | 5 | Ajouter entrée d'évolution |
| `docs/LANGGRAPH_VIA_LITELLM.md` | 5 | Mention optionnelle |
| `requirements*.txt` / `pyproject.toml` | 5 | Vérifier version LiteLLM |

---

## 6. Risques et précautions

| Risque | Mitigation |
|--------|------------|
| Bug LiteLLM : le hook n'est jamais appelé | Vérifier version LiteLLM (PR #8627), tester en local. |
| Format des chunks variable (dict vs objet) | Gérer les deux cas (accès par attribut ou clé) pour `delta.content`. |
| Signature dupliquée (streaming + non-streaming) | Les deux hooks sont exclusifs ; le success hook ne s'exécute que pour non-streaming. |
| `request_data` sans `model` | Fallback : pas de signature ou modèle par défaut. |

---

## 7. Ordre d'exécution suggéré

1. Phase 1 — Vérifier version LiteLLM et que le hook est bien invoqué.
2. Phase 2 — Implémenter `async_post_call_streaming_iterator_hook` dans `litellm_hooks.py`.
3. Phase 4 — Tester manuellement en streaming.
4. Phase 5 — Mettre à jour la documentation.
5. Phase 3 — Vérifier qu'il n'y a pas de régression sur le mode non-streaming.
