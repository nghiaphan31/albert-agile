# Presidio — PII Masking pour LiteLLM (spec §10.1)

Microsoft Presidio détecte et masque les PII (Personally Identifiable Information) avant envoi aux modèles cloud via le proxy LiteLLM.

## Architecture

- **Flux sortant** : prompt utilisateur → Presidio Analyzer (détection) → Presidio Anonymizer (remplacement) → modèle cloud
- **Flux entrant** : réponse modèle → parsing optionnel (`output_parse_pii: true`) → restitution des valeurs masquées au graphe

## Prérequis

- Docker
- LiteLLM avec proxy (`pip install 'litellm[proxy]'`)

## Démarrage

### 1. Lancer Presidio

```bash
docker compose up -d presidio-analyzer presidio-anonymizer
```

Ports : Analyzer `5002`, Anonymizer `5001`.

### 2. Variables d'environnement

Ajouter dans `.env` :

```
PRESIDIO_ANALYZER_API_BASE=http://localhost:5002
PRESIDIO_ANONYMIZER_API_BASE=http://localhost:5001
```

### 3. Configuration LiteLLM

Le callback `presidio` est déjà présent dans `config/litellm_config.yaml` et `config/litellm_config_cascade_complete.yaml`.

Pour **désactiver** Presidio (si les conteneurs ne tournent pas), retirer `presidio` de la liste `litellm_settings.callbacks`.

### 4. Vérification

```bash
curl -X POST http://localhost:5002/analyze \
  -H "Content-Type: application/json" \
  -d '{"text": "My email is john@example.com", "language": "en"}'
```

Réponse attendue : `[{"entity_type": "EMAIL_ADDRESS", "start": 12, "end": 28, "score": 1.0}]`

## Coexistence avec L-ANON

L-ANON (`graph/anonymizer.py`) reste actif pour les appels directs LangGraph (cascade N1/N2). Presidio s'applique aux flux passant par le proxy LiteLLM (`AGILE_USE_LITELLM_PROXY=true`).

## Références

- [Presidio Docker + LiteLLM](https://microsoft.github.io/presidio/samples/docker/litellm/)
- [LiteLLM PII Masking v2](https://docs.litellm.ai/docs/proxy/guardrails/pii_masking_v2)
