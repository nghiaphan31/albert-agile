# SearXNG — Recherche web pour agents (spec §9)

Métamoteur de recherche auto-hébergé pour contourner le knowledge cutoff des LLM et fournir un accès web temps réel aux agents (R-2, R-4, R-6).

## Architecture

- **Docker** : conteneur `searxng/searxng` exposé sur le port 8080
- **LangChain** : `SearxSearchWrapper` → tool `search_web` dans `create_tools_r4`
- **API** : format JSON activé dans `config/searxng/settings.yml`

## Prérequis

- Docker
- `langchain-community` (voir `requirements.txt`)

## Démarrage

### 1. Lancer SearXNG

```bash
docker compose up -d searxng
```

### 2. Variables d'environnement

Dans `.env` :

```
SEARXNG_BASE_URL=http://localhost:8080
```

### 3. Vérification

```bash
curl -s "http://localhost:8080/search?q=langchain&format=json" | head -c 500
```

Doit retourner du JSON avec des résultats.

## Intégration

Le tool `search_web` est ajouté automatiquement à `create_tools_r4()` quand `SEARXNG_BASE_URL` ou `SEARXNG_HOST` est défini. Pour les nœuds R-2 et R-6, l’intégration nécessite que ces nœuds utilisent des tools (refactoring futur du graphe).

## Références

- [SearXNG Documentation](https://docs.searxng.org/)
- [LangChain SearXNG integration](https://python.langchain.com/docs/integrations/providers/searx)
