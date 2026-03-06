# GPU / VRAM — Profils & checklist (RTX 5060 Ti 16G)

Ce dépôt est **GPU-agnostique**. Les réglages ci-dessous servent à éviter les problèmes de **swapping de modèles**, **OOM VRAM** et **contention GPU** (LLM vs embeddings) quand on utilise Ollama + indexation RAG.

## Configuration actuelle (Calypso)

Calypso est équipée de **RTX 5060 Ti 16G** (swap effectué). Profil appliqué : `AGILE_GPU_PROFILE=vram_16gb`.

## Profil recommandé (VRAM ≥ 16 Go) — RTX 5060 Ti 16G

### Objectif
- Garder un workflow fluide (E4/E5) avec **un modèle prioritaire** en mémoire.
- Autoriser davantage de confort (moins de contraintes “un seul modèle à la fois”).

### Recommandations
- **Profil**: `AGILE_GPU_PROFILE=vram_16gb`
- **Modèle prioritaire (E4/E5)**: `qwen2.5-coder` (ex. `qwen2.5-coder:7b` ou `qwen2.5-coder:3b` selon ta stabilité/perf)
- **Keep-alive Ollama** (évite le déchargement automatique du modèle) :

```bash
export OLLAMA_KEEP_ALIVE=24h
```

- **Warmup (précharger le modèle prioritaire)** :

```bash
ollama run qwen2.5-coder:7b "warmup"
```

- **Indexation RAG** :
  - **Par défaut**: conserver `AGILE_DEFER_INDEX=true` (évite d’indexer au mauvais moment).
  - Si tu veux indexer plus souvent avec 16 Go: activer **incrémental** (`AGILE_RAG_INCREMENTAL=true`) et lancer l’indexation hors exécution E4/E5.

## Profil legacy (VRAM ≈ 12 Go) — RTX 3060 12G (historique)

Ce profil existe uniquement pour conserver le retour d’expérience (cf. `specs/simulations/Simulation_014_2026-03-14.md`).

### Contraintes typiques
- **Un seul “gros” modèle en VRAM** à la fois.
- `nomic-embed-text` (embeddings) + `qwen2.5-coder` en parallèle = conflits très probables.

### Recommandations
- **Profil**: `AGILE_GPU_PROFILE=legacy_12gb`
- **Toujours**: `AGILE_DEFER_INDEX=true`
- **File watcher RAG**: `AGILE_RAG_FILE_WATCHER=false` (sinon indexation intempestive pendant E4/E5)
- **Keep-alive** (E4/E5):

```bash
export OLLAMA_KEEP_ALIVE=24h
```

## Variables d’environnement (résumé)

| Variable | Rôle | Valeur conseillée (16 Go) | Valeur conseillée (legacy 12 Go) |
|---|---|---:|---:|
| `AGILE_GPU_PROFILE` | Trace le profil choisi | `vram_16gb` | `legacy_12gb` |
| `OLLAMA_KEEP_ALIVE` | Garde les modèles en mémoire (durée) | `24h` (E4/E5) | `24h` (E4/E5) |
| `AGILE_DEFER_INDEX` | Décale l’indexation RAG | `true` (par défaut) | `true` (obligatoire) |
| `AGILE_RAG_FILE_WATCHER` | Watcher indexation | `false` (par défaut) | `false` (recommandé) |
| `AGILE_RAG_INCREMENTAL` | Indexation incrémentale | `true` (optionnel) | `false` (souvent) |

## Checklist “terrain propre” — remplacement RTX 3060 → RTX 5060 Ti 16G (Linux)

### 1) Avant le swap (préparation)
- **Arrêter les services liés au GPU** (Ollama, outils d’indexation en cours).
- **Noter l’état actuel** :
  - version driver NVIDIA (via `nvidia-smi`)
  - versions kernel / distro
  - modèles Ollama installés (via `ollama list`)

### 2) Swap matériel
- Arrêt complet (power off), remplacement de la carte.
- Vérifier :
  - câbles d’alimentation PCIe correctement branchés (et adaptés)
  - capacité PSU suffisante

### 3) Après le swap (vérifs système)
- **Détection GPU** : `lspci | grep -i nvidia`
- **Driver + VRAM** : `nvidia-smi`
  - attendu : nom RTX 5060 Ti et VRAM ~16 Go (≈ 16384 MiB)

Si `nvidia-smi` échoue :
- Mettre à jour/installer le driver NVIDIA via la méthode de ta distro (Ubuntu : `ubuntu-drivers devices` puis installer le driver recommandé), puis redémarrer et re-tester.

### 4) Ollama (remise en route)
- Vérifier qu’Ollama tourne et répond :
  - `curl http://localhost:11434/api/tags`
- Tester un run rapide (modèle déjà présent) :
  - `ollama run qwen2.5-coder:3b "ping"`

### 5) Nettoyage Ollama (optionnel)
Objectif : repartir “propre” si tu suspectes un état incohérent (modèles, cache, corruption).

- **Option soft (recommandée)** : supprimer uniquement les modèles non nécessaires.

```bash
ollama list
ollama rm gemma3:12b-it-q4_K_M   # exemple (si tu n'en as plus besoin)
```

- **Option hard (reset)** : repartir d’une installation vide (impose de re-pull les modèles).
  - Emplacement par défaut : `~/.ollama` (à vérifier selon ton installation).

```bash
# 1) Arrêter Ollama (selon ta configuration : service systemd ou process)
# 2) Supprimer le répertoire de données
rm -rf ~/.ollama
```

Je te conseille de faire le soft d’abord, et de réserver le hard si tu observes des erreurs répétées (crash du runner, modèles impossibles à charger, etc.).

