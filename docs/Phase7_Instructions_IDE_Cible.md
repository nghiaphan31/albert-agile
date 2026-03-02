# Phase 7 — Installation de l'IDE cible (actions manuelles sur ton PC)

Ces étapes s'exécutent **sur ton PC** (pas sur Calypso). L'agent ne peut pas les automatiser.

---

## 7.1 Installer VS Code

1. Ouvre https://code.visualstudio.com/
2. Télécharge la version stable pour ton OS (ex. Windows)
3. Installe VS Code (exécute l'installateur)

---

## 7.2 Extension Remote-SSH

1. Dans VS Code : Extensions (Ctrl+Shift+X)
2. Recherche **Remote - SSH** (Microsoft)
3. Installe

---

## 7.3 Se connecter à Calypso

1. Ctrl+Shift+P → **Remote-SSH: Connect to Host**
2. Sélectionne ou ajoute `nghia-phan@calypso` (ou ton hôte SSH)
3. VS Code ouvre une nouvelle fenêtre connectée à Calypso

---

## 7.4 Installer Continue.dev

1. Une fois connecté à Calypso : Extensions (Ctrl+Shift+X)
2. Recherche **Continue** (continue.dev)
3. Installe

**Configuration Continue :**
- Paramètres → Modèles
- Ajoute **Ollama** :
  - URL : `http://localhost:11434`
  - Modèles : `qwen2.5-coder:7b`, `gemma3:12b-it-q4_K_M`

---

## 7.5 Installer Roo Code

1. Extensions → Recherche **Roo Code**
2. Installe
3. Même config Ollama : `http://localhost:11434`, modèles `qwen2.5-coder:7b` / `gemma3:12b-it-q4_K_M`

---

## 7.6 chroma-mcp (RAG partagé) — optionnel

chroma-mcp est déjà installé dans le venv du projet. Pour le configurer dans Continue :

- Chemin Chroma : `/home/nghia-phan/PROJECTS_WITH_ALBERT/albert-agile/chroma_db`
- Réfère-toi à la doc Continue pour ajouter un serveur MCP chroma-mcp

---

## 7.7 Recommandation RTX 3060

Pendant E4/E5 (quand le graphe LangGraph tourne sur Calypso), configure Continue/Roo Code sur **qwen2.5-coder:7b** pour éviter le swapping de modèles (un seul modèle en VRAM sur RTX 3060).
