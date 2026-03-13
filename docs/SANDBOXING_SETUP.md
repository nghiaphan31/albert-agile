# Sandboxing run_shell (spec §7.1)

Exécution des commandes `pytest` dans un conteneur Docker éphémère pour éviter toute modification de la machine hôte.

## Prérequis

- Docker
- Projet configuré avec `AGILE_SANDBOX_RUN_SHELL=true`

## Build de l'image

```bash
docker compose build sandbox
```

Ou directement :

```bash
docker build -t albert-sandbox docker/sandbox
```

## Activation

Dans `.env` :

```
AGILE_SANDBOX_RUN_SHELL=true
```

Quand cette variable est définie et que l'image `albert-sandbox` existe, les commandes `pytest` lancées via `run_shell` sont exécutées dans le conteneur. Sinon, exécution locale (comportement par défaut).

## Sécurité

- Réseau désactivé (`--network none`)
- Volume monté en lecture-écriture limité au `project_root`
- Timeout configurable (300 s par défaut)
- Conteneur supprimé après exécution (`--rm`)
