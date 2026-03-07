# Plan — Configuration VS Code, Continue.dev et Roo Code

**Objectif** : Configurer VS Code + Continue.dev + Roo Code avec le choix entre :
- **Ollama local** (Calypso) — 0 €, aligné avec le graphe LangGraph
- **Gemini** (free tier) — clé API Google
- **Anthropic Claude Sonnet 4.6** — clé API Anthropic

**Références** : [Phase 7 Implementation](../specs/plans/Implementation_Ecosysteme_Agile_Calypso.md#phase-7--installation-de-lide-cible-vs-code--continuedev--roo-code), [Phase7_Instructions_IDE_Cible](../../docs/Phase7_Instructions_IDE_Cible.md), [HARDWARE_GPU](../../docs/HARDWARE_GPU.md).

**Modèles Ollama** (alignés avec `graph/llm_factory.py`) :
- Tier 1 (idéation, architecture) : `qwen2.5:14b` (défaut) ou `qwen3:14b` (thinking natif, plus lent)
- Tier 2 (code, sprint backlog) : `qwen2.5-coder:14b`

Voir [Strategie_Modeles_LLM_Thinking_Albert_Agile.md](Strategie_Modeles_LLM_Thinking_Albert_Agile.md) pour les recommandations thinking/CoT.

---

## Modes d'utilisation : manuel vs routage automatique

Deux modes sont proposés, à l'instar de Cursor Pro (Smart / manuel) :

### Mode manuel — choix explicite

Tu sélectionnes directement le modèle dans Continue ou Roo Code à chaque requête.

| Avantage | Usage typique |
|----------|---------------|
| Contrôle total, débogage, coût maîtrisé | Tester un modèle précis, comparer les réponses, forcer le local ou le cloud |
| Aucune dépendance à un proxy | Configuration simple (section 3 et 4) |

**Activation** : utiliser la config Continue / Roo Code classique (sections 3 et 4) et choisir le modèle dans la liste.

### Mode automatique — routage comme albert-agile

Un proxy (ex. LiteLLM) route les requêtes selon la tâche et applique une cascade en cas d'échec.

| Étape | Comportement |
|-------|--------------|
| 1. Routage par tâche | Code → coder (qwen2.5-coder), idéation → qwen2.5 ou qwen3, raisonnement complexe → qwen3 (thinking) |
| 2. Cascade | Local (Ollama) → Gemini (gratuit) → Claude Sonnet voire Opus si besoin |

**Activation** : configurer Continue / Roo Code pour pointer vers le proxy LiteLLM (base_url du provider OpenAI) et sélectionner le modèle virtuel (ex. `auto-router` ou `smart-router`). Voir [section 10](#10-optionnel--routage-automatique-via-litellm).

---

## 1. Prérequis

| Élément | Vérification |
|---------|--------------|
| Ollama actif sur Calypso | `ollama list` — `qwen2.5:14b`, `qwen2.5-coder:14b`, `nomic-embed-text` présents (option : `qwen3:14b`) |
| Modèles pull | `ollama pull qwen2.5:14b`, `ollama pull qwen2.5-coder:14b` ; si thinking : `ollama pull qwen3:14b` |
| Connexion SSH à Calypso | `ssh nghia-phan@calypso` fonctionnel |
| VS Code installé sur le PC | https://code.visualstudio.com/ |

---

## 2. VS Code — Installation et Remote-SSH

### 2.1 Installer VS Code

1. Télécharger la version stable : https://code.visualstudio.com/
2. Installer (Windows, Linux ou macOS selon ton OS)
3. Lancer VS Code

### 2.2 Extension Remote-SSH

1. **Extensions** (Ctrl+Shift+X / Cmd+Shift+X)
2. Rechercher **Remote - SSH** (éditeur : Microsoft)
3. Installer

### 2.3 Connexion à Calypso

1. **Ctrl+Shift+P** (ou Cmd+Shift+P) → **Remote-SSH: Connect to Host**
2. Sélectionner ou ajouter `nghia-phan@calypso` (ou ton hôte SSH configuré)
3. VS Code ouvre une nouvelle fenêtre connectée à Calypso
4. Le **terminal intégré à VS Code** (panneau Terminal, Ctrl+`) exécute les commandes **sur Calypso** (contexte Remote-SSH). Ce n'est pas un terminal externe (ex. SSH dans une autre fenêtre).

### 2.4 Convention terminal pour la suite

Toutes les commandes décrites dans ce plan (vérifications, `ollama list`, éventuellement LiteLLM, etc.) sont à exécuter dans le **terminal intégré à VS Code**. Pour l'exécution du graphe Agile (`run_graph.py`, `handle_interrupt.py`, `status.py`), voir [Modes_Bootstrap_et_Runtime_Cible.md](Modes_Bootstrap_et_Runtime_Cible.md) (ou [Plan_Reste_Calypso_E2E_Optionnels.md](Plan_Reste_Calypso_E2E_Optionnels.md)).

**Important — où Continue lit sa config** : Continue v1.x est une extension **locale** (UI extension). Même connecté à Calypso via Remote-SSH, Continue lit sa config depuis le **PC client** (pas depuis Calypso) :
- Windows → `C:\Users\<user>\.continue\config.yaml`
- macOS/Linux client → `~/.continue/config.yaml` sur ce client

Le fichier `~/.continue/config.yaml` sur Calypso n’est **pas lu** dans ce setup (Calypso headless). Les appels aux modèles Ollama transitent malgré tout par le composant distant, donc `http://localhost:11434` dans la config = port 11434 sur Calypso.

---

## 3. Continue.dev — Configuration multi-providers

### 3.1 Installer l’extension

1. Une fois connecté à Calypso : **Extensions** → rechercher **Continue** (continue.dev)
2. Installer

### 3.2 Ouvrir la configuration

- **Ctrl+Shift+P** → **Continue: Open Config**
- Ou créer / éditer : `~/.continue/config.json` (ou `config.yaml`)

### 3.3 Configuration : Ollama + Gemini + Anthropic (YAML)

Fichier `~/.continue/config.yaml` (sur Calypso) — tu peux choisir le modèle à tout moment dans l’interface :

```yaml
name: Calypso (Ollama + Gemini + Anthropic)
version: 1.0.0
schema: v1

models:
  # --- Ollama local (0 €) ---
  - name: qwen2.5-coder:14b (Ollama)
    provider: ollama
    model: qwen2.5-coder:14b
    apiBase: http://localhost:11434

  - name: qwen2.5:14b (Ollama)
    provider: ollama
    model: qwen2.5:14b
    apiBase: http://localhost:11434

  - name: qwen3:14b (Ollama, thinking)
    provider: ollama
    model: qwen3:14b
    apiBase: http://localhost:11434

  # --- Gemini (free tier) — GOOGLE_API_KEY ---
  - name: gemini-2.0-flash (Gemini)
    provider: gemini
    model: gemini-2.0-flash
    apiKey: ${{ secrets.GOOGLE_API_KEY }}

  # --- Anthropic Claude Sonnet 4.6 — ANTHROPIC_API_KEY ---
  - name: claude-sonnet-4-6 (Anthropic)
    provider: anthropic
    model: claude-sonnet-4-6
    apiKey: ${{ secrets.ANTHROPIC_API_KEY }}
```

**Clés API** : à définir dans `~/.continue/.env` (lu automatiquement par Continue v1.x) :
```
GOOGLE_API_KEY=ta-clé-google
ANTHROPIC_API_KEY=ta-clé-anthropic
```
Continue résout `${{ secrets.NOM_CLE }}` depuis ce fichier. Les variables d’environnement système (`export`) ne sont **pas** lues par Continue pour les secrets.

### 3.4 Modèle par défaut

Dans Continue, sélectionner le modèle actif selon le contexte :
- **Ollama code** : `qwen2.5-coder:14b` — alignement E4/E5, 0 €
- **Ollama idéation** : `qwen2.5:14b` (rapide) ou `qwen3:14b` (thinking natif, plus lent)
- **Gemini** : free tier, rapide
- **Anthropic** : Claude Sonnet 4.6 pour les tâches plus complexes

---

## 4. Roo Code — Configuration multi-providers

### 4.1 Installer l’extension

1. **Extensions** → rechercher **Roo Code** (RooVeterinaryInc)
2. Installer

### 4.2 Choix du provider (Provider Settings)

Roo Code permet de choisir entre **Ollama**, **Gemini** et **Anthropic** dans les paramètres (icône engrenage). Un seul provider actif à la fois.

**Ollama (local, 0 €)** :
- API Provider : **Ollama**
- Base URL : `http://localhost:11434`
- Model ID : `qwen2.5-coder:14b` (code), `qwen2.5:14b` (idéation) ou `qwen3:14b` (thinking natif)
- Context Window : 32K minimum

**Gemini (free tier)** :
- API Provider : **Google Gemini**
- API Key : depuis [Google AI Studio](https://aistudio.google.com/)
- Model : `gemini-2.0-flash` (ou équivalent free tier)

**Anthropic Claude Sonnet 4.6** :
- API Provider : **Anthropic**
- API Key : depuis [Anthropic Console](https://console.anthropic.com/)
- Model : `claude-sonnet-4-6`

### 4.3 Profils (optionnel)

Roo Code propose des **API Configuration Profiles** : tu peux créer plusieurs profils (ex. « Ollama local », « Gemini », « Claude ») et basculer selon le contexte.

---

## 5. Vérification

| Étape | Action | Résultat attendu |
|-------|--------|------------------|
| 5.1 | Dans VS Code connecté à Calypso, ouvrir Continue | Chat Continue disponible |
| 5.2 | Continuer avec Ollama sélectionné, poser une question | Réponse générée (pas d’erreur 404/500) |
| 5.3 | Continuer avec Gemini puis Anthropic | Les deux répondent si les clés API sont configurées |
| 5.4 | Ouvrir Roo Code, lancer une tâche | Roo Code répond selon le provider actif |
| 5.5 | (Ollama) Vérifier les logs | Dans le **terminal intégré à VS Code** connecté à Calypso : `ollama ps` montre le modèle chargé lors des requêtes |

---

## 6. Recommandations (GPU / contention)

Voir [HARDWARE_GPU.md](../../docs/HARDWARE_GPU.md).

- **Pendant E4/E5** (graphe LangGraph actif) : utiliser le **même modèle prioritaire** (`qwen2.5-coder:14b`) dans Continue et Roo Code pour limiter le swapping Ollama.
- **Alternative** : désactiver l’autocomplétion IA pendant E4/E5.
- **Keep-alive** (optionnel) : `export OLLAMA_KEEP_ALIVE=qwen2.5-coder:14b` avant de lancer le graphe (cf. `scripts/test_e2e_manual.py`).

---

## 7. Optionnel — RAG partagé (chroma-mcp)

Pour que Continue utilise le même index RAG que les agents LangGraph :

1. Installer chroma-mcp : `pip install chroma-mcp` (dans le venv du projet)
2. Configurer dans Continue (MCP) : pointer vers `$AGILE_ORCHESTRATION_ROOT/chroma_db`
3. Référer à la doc Continue pour les serveurs MCP

---

## 8. Résumé — Choix de provider

| Provider | Coût | Clé API | Modèles recommandés |
|----------|------|---------|---------------------|
| **Ollama** | 0 € | — | `qwen2.5-coder:14b`, `qwen2.5:14b`, `qwen3:14b` (thinking) |
| **Gemini** | Free tier | `GOOGLE_API_KEY` | `gemini-2.0-flash` |
| **Anthropic** | Pay-as-you-go | `ANTHROPIC_API_KEY` | `claude-sonnet-4-6` |

Continue : tous les modèles sont listés dans la config ; tu choisis celui à utiliser à la volée.  
Roo Code : un seul provider actif ; tu peux définir plusieurs profils pour basculer.

---

## 9. URLs et chemins

| Composant | URL / Chemin |
|-----------|--------------|
| Ollama API | `http://localhost:11434` (Calypso = localhost en Remote-SSH) |
| Config Continue | `~/.continue/config.yaml` ou `config.json` |
| Config Roo Code | Paramètres in-app (Provider Settings / Profiles) |
| Chroma (optionnel) | `$AGILE_ORCHESTRATION_ROOT/chroma_db` |
| LiteLLM Proxy (optionnel) | `http://localhost:4000` (si mode automatique) |

---

## 10. Optionnel — routage automatique via LiteLLM

Pour le **mode automatique** (routage par tâche + cascade), installer et configurer LiteLLM Proxy :

### 10.1 Installation

```bash
pip install 'litellm[proxy]'
```

### 10.2 Configuration (exemple)

Fichier `config.yaml` pour LiteLLM avec routage par complexité et cascade :

```yaml
model_list:
  - model_name: qwen2.5-coder
    litellm_params:
      model: ollama/qwen2.5-coder:14b
      api_base: http://localhost:11434
  - model_name: qwen3-thinking
    litellm_params:
      model: ollama/qwen3:14b
      api_base: http://localhost:11434
  - model_name: qwen2.5
    litellm_params:
      model: ollama/qwen2.5:14b
      api_base: http://localhost:11434
  - model_name: gemini
    litellm_params:
      model: gemini/gemini-2.0-flash
  - model_name: claude-sonnet
    litellm_params:
      model: anthropic/claude-sonnet-4-6
  # Routeur complexité + fallbacks
  - model_name: smart-router
    litellm_params:
      model: auto_router/complexity_router
      complexity_router_config:
        tiers:
          SIMPLE: qwen2.5
          MEDIUM: qwen2.5-coder
          COMPLEX: qwen2.5-coder
          REASONING: qwen3-thinking
      complexity_router_default_model: qwen2.5-coder
      fallbacks:
        - qwen2.5-coder
        - gemini
        - claude-sonnet
```

### 10.3 Lancer le proxy

```bash
litellm --config config.yaml
```

Le proxy écoute par défaut sur `http://0.0.0.0:4000`.

### 10.4 Configurer Continue pour le mode automatique

Ajouter un modèle pointant vers LiteLLM (provider OpenAI avec base_url) :

```yaml
  - title: Smart Router (auto)
    provider: openai
    model: smart-router
    apiBase: http://localhost:4000
    apiKey: "sk-1234"  # ou variable d'env
```

Sélectionner « Smart Router (auto) » pour activer le routage automatique.
