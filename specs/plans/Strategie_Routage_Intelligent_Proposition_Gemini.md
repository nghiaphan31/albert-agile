# Stratégie de routage intelligent — Proposition Gemini 3.1 Pro

**Source** : Synthèse proposée par Gemini 3.1 Pro (chat navigateur, gratuit) en réponse à une demande d'amélioration de la stratégie d'utilisation des ressources (RTX 5060, modèles locaux, APIs cloud).

**Contexte actuel albert-agile** : RTX 5060 Ti 16G, qwen3:14b local via Ollama, fallback Gemini 2.5 Flash puis Claude Sonnet. Voir [Plan_Configuration_VSCode_Ollama_Local.md](Plan_Configuration_VSCode_Ollama_Local.md).

> ⚠️ **Note d'adaptation** : Les noms de modèles proposés (Gemini 3 Flash, DeepSeek-V3.1, Claude 4.6) peuvent différer des offres actuelles. Adapter selon disponibilité : ex. `gemini-2.5-flash` à la place de `gemini-3-flash`, `claude-sonnet-4` au lieu de `claude-4-6-sonnet`, etc.

---

## 1. La stratégie globale : routage intelligent et optimisation des coûts

L'objectif est d'orchestrer un agent autonome (Roo Code) de manière extrêmement rentable, en déléguant dynamiquement les requêtes au modèle le plus adapté selon la tâche, tout en empêchant l'agent de tourner en boucle et de consommer inutilement des ressources.

La répartition des rôles s'articule autour de trois axes :

1. **L'ingestion massive (`ingest`)** : Le traitement de gigantesques documentations ou *repositories* est confié à Gemini 3 Flash, offrant une fenêtre de contexte massive à un coût dérisoire.
2. **La conception de haut niveau (`architect`)** : L'architecture système et les plans de tests complexes sont envoyés à DeepSeek-V3.1, qui offre le meilleur ratio prix/raisonnement du marché. En cas de défaillance de l'API, le système bascule automatiquement sur Claude 4.6 Sonnet pour garantir la continuité du service.
3. **Le travail de terrain (`worker`)** : Le codage, le refactoring, les validations Git et le débogage itératif sont interceptés et envoyés gratuitement vers le modèle local (Qwen3:14b tournant sur la machine).

---

## 2. La défense en profondeur : sécurité anti-boucle (HITL)

Pour pallier le risque d'entêtement typique des agents autonomes face à un bug persistant, une double protection "Human-in-the-Loop" est instaurée :

- **Niveau 1 (Front-end)** : Des consignes strictes sont données à Roo Code pour qu'il s'interrompe lui-même après trois échecs et utilise son canal officiel pour demander l'assistance humaine.
- **Niveau 2 (Back-end)** : Un disjoncteur silencieux est intégré au routeur (LiteLLM). Il compte les erreurs dans l'historique récent. S'il détecte une boucle que l'agent n'a pas su arrêter, il coupe l'accès au modèle, déclenche une alerte sonore sur le terminal et force la mise en pause.

---

## 3. L'intervention humaine manuelle (HITL) via Gemini 3.1 Pro

Le "Human-in-the-loop" via le chat du navigateur avec Gemini 3.1 Pro permet de faire chuter drastiquement les coûts d'API tout en garantissant une qualité maximale.

1. **L'élaboration de l'Architecture (Zero-to-One)** : Au lieu de consommer des centaines de milliers de tokens API pour les tâtonnements conceptuels, l'itération se fait dans le chat. Le document de spécifications généré est ensuite copié dans un fichier `architecture_blueprint.md` et transmis à Roo Code pour que le modèle local crée le squelette gratuitement.
2. **L'assistance au débogage complexe** : Si le modèle local Qwen se retrouve bloqué sur une erreur tenace, Roo Code est mis en pause. Le fichier problématique et le log d'erreur sont copiés dans le chat Gemini pour une analyse experte, puis la solution précise est transmise à l'agent local.
3. **La génération des Plans de Tests et de la Documentation** : Pour éviter les coûts d'output élevés des API, le code brut est fourni à Gemini dans le navigateur qui se charge de rédiger les documents longs (`plan_de_test.md`). L'exécution répétitive (écrire et passer les tests) est ensuite déléguée au travailleur local.

---

## 4. Les mécanismes de transfert de contexte

Pour faciliter les allers-retours (copier-coller) entre l'IDE et le navigateur sans friction, trois méthodes sont possibles :

1. **L'export natif de Roo Code (Le plus rapide)** : L'interface de chat de Roo Code possède une icône de copie ou un menu d'export permettant de récupérer en un clic la dernière réponse, le log d'erreur complet ou l'historique récent proprement formaté en Markdown.
2. **Les extensions VS Code "AI Context Copier" (Le plus structuré)** : Des extensions gratuites comme "ChatGPT - Copy to Clipboard" ou "AI Context" permettent de sélectionner plusieurs fichiers dans l'explorateur et de les copier dans le presse-papier avec une structure Markdown parfaite (incluant le nom du fichier et le bloc de code associé).
3. **Le script local Python (L'approche sur-mesure)** : Un petit utilitaire en ligne de commande (utilisant la librairie `pyperclip`) qui lit les fichiers ciblés, récupère automatiquement les derniers logs d'erreurs du projet, formate le tout avec des instructions claires et l'envoie directement dans le presse-papier.

---

## 5. Fichiers de configuration (mot pour mot)

### 5.1 Fichier de configuration principal LiteLLM (`config/litellm_config.yaml`)

Ce fichier déclare les trois rôles, configure les modèles associés, gère le *fallback* automatique pour l'architecte, et active le script d'interception Python.

```yaml
model_list:
  # 1. L'Architecte Cloud (DeepSeek en priorité, Claude en roue de secours)
  - model_name: architect
    litellm_params:
      model: deepseek/deepseek-chat-v3.1
      fallbacks:
        - anthropic/claude-4-6-sonnet-20260219

  # 2. L'ingestion massive de contexte documentaire
  - model_name: ingest
    litellm_params:
      model: gemini/gemini-3-flash

  # 3. Le travailleur local gratuit (Code, Debug, Git)
  - model_name: worker
    litellm_params:
      model: ollama/qwen3:14b
      api_base: http://localhost:11434

litellm_settings:
  # Appel de ton script Python pour l'interception et le routage
  custom_callbacks:
    - custom_roo_hook.proxy_handler_instance
```

> **Note** : Dans LiteLLM récent, le champ est `callbacks` (et non `custom_callbacks`), et le chemin doit correspondre à un module importable (ex. `config.custom_roo_hook.proxy_handler_instance` si le fichier est dans `config/`).

---

### 5.2 Script d'interception et de routage (`config/custom_roo_hook.py`)

Ce *Pre-Call Hook* intercepte la requête de Roo Code avant qu'elle ne soit traitée. Il gère d'abord le disjoncteur de sécurité (analyse des 5 derniers messages), puis, si aucune boucle n'est détectée, il route la requête vers l'alias correspondant aux mots-clés détectés. *Voir [section 5.3](#53-limite-des-mots-clés-et-routage-sémantique-par-embeddings) pour l'évolution par embeddings sémantiques.*

```python
from litellm.integrations.custom_logger import CustomLogger

class RooCodeHandler(CustomLogger):
    async def async_pre_call_hook(self, user_api_key_dict, cache, data, call_type):
        messages = data.get("messages", [])
        if not messages:
            return data

        # --- 1. DISJONCTEUR DE SÉCURITÉ (HITL TRIGGER) ---
        # Analyser les 5 derniers messages pour repérer une boucle d'erreurs
        error_count = 0
        recent_messages = messages[-5:]
        for msg in recent_messages:
            content = str(msg.get("content", "")).lower()
            if "error" in content or "command failed" in content or "exception" in content:
                error_count += 1

        if error_count >= 3:
            # Alerte visuelle et sonore (bip) dans le terminal où tourne LiteLLM
            print("\a")
            print("\n" + "🔴"*20)
            print("🚨 ALERTE HITL : Boucle d'erreurs détectée !")
            print("Intervention humaine requise. Arrêt forcé de l'agent.")
            print("🔴"*20 + "\n")

            # On écrase la requête pour forcer l'agent à utiliser son outil 'ask_user'
            data["messages"] = [{
                "role": "user",
                "content": "SYSTEM OVERRIDE: You are stuck in an error loop. You MUST stop immediately. Use the 'ask_user' tool to explain the error to the human and wait for instructions. Do not execute any other tool."
            }]
            data["model"] = "worker"
            return data

        # --- 2. ROUTAGE INTELLIGENT (Si tout va bien) ---
        last_message = str(messages[-1].get("content", "")).lower()

        ingest_triggers = [
            "ingérer", "documentation complète", "lire le repository",
            "analyser le framework", "contexte global"
        ]

        architect_triggers = [
            "architecture", "plan de test", "conception globale",
            "analyse systémique", "structurer le projet"
        ]

        if any(trigger in last_message for trigger in ingest_triggers):
            data["model"] = "ingest"
        elif any(trigger in last_message for trigger in architect_triggers):
            data["model"] = "architect"
        else:
            data["model"] = "worker"

        return data

    async def async_post_call_success_hook(self, data, user_api_key_dict, response):
        # --- Garde ton code existant ici pour le fake stream si nécessaire ---
        pass

# Instanciation pour LiteLLM
proxy_handler_instance = RooCodeHandler()
```

---

### 5.3 Limite des mots-clés et routage sémantique par embeddings

**Source** : Suggestion d'adaptation par Gemini 3.1 Pro.

#### La limite des mots-clés simples

Avec le script actuel (section 5.2), si Roo Code écrit « Je vais structurer le projet », la condition `"structurer le projet" in text` fonctionne.

Mais si Roo Code écrit « Je vais concevoir le squelette de l'application », le routeur rate le mot-clé et envoie cette tâche d'architecture complexe au petit modèle local, qui risque de mal faire le travail.

#### La combinaison Python + Embeddings

L'idée est d'utiliser le script Python comme « filtre extracteur » avant de faire appel au moteur sémantique :

1. **L'isolation** : Le script intercepte la requête et isole rigoureusement `messages[-1]` (l'intention de Roo), en laissant de côté les milliers de tokens du System Prompt.
2. **La vectorisation** : Le script Python prend cette courte phrase isolée et demande en arrière-plan au modèle local `nomic-embed-text` (via Ollama) d'en produire un vecteur mathématique.
3. **La comparaison (similarité cosinus)** : Le script compare ce vecteur avec des vecteurs de référence pré-calculés (ex. un vecteur moyen pour « Tâches d'architecture », un vecteur moyen pour « Tâches d'ingestion »).
4. **Le routage** : Il choisit la route mathématiquement la plus proche et envoie la vraie requête au bon modèle (DeepSeek, Gemini ou Qwen).

#### Les avantages

- **Zéro lissage** : Puisqu'on ne vectorise que la dernière phrase, l'embedding est extrêmement net et discriminant.
- **Flexibilité totale** : Plus besoin de maintenir une liste interminable de synonymes dans le code Python. L'embedding comprendra par lui-même que « squelette », « blueprint » ou « fondations » relèvent de l'alias `architect`.

#### Implémentation suggérée

- Modèle embedding local : `nomic-embed-text` (déjà disponible via Ollama, aligné avec le RAG albert-agile).
- Stockage des vecteurs de référence : pré-calculer une fois les embeddings de phrases exemples par catégorie (ingest, architect, worker) et les persister (JSON ou fichier binaire) pour éviter de recalculer à chaque requête.
- Seuil de similarité : définir un seuil minimal ; si aucune catégorie ne dépasse le seuil, fallback sur `worker` (par défaut, plus sûr).

---

### 5.4 Instructions personnalisées pour l'agent (Roo Code Custom Instructions)

Ce bloc de texte, placé dans les paramètres de l'extension Roo Code, constitue la première ligne de défense. Il empêche le modèle local de multiplier les tentatives ratées et formalise sa demande d'aide.

```text
# CRITICAL RULE: HUMAN-IN-THE-LOOP (HITL) TRIGGER
You are operating in a resource-optimized environment. If you encounter the same error, a failing test, or a command failure 3 times in a row while attempting to fix it, YOU MUST STOP IMMEDIATELY. Do not attempt a 4th fix. Do not hallucinate workarounds.

Instead, you must strictly use the 'ask_user' tool to request human intervention.
Your message to the user must start exactly with: "🚨 HITL REQUIRED: I am stuck in an error loop."
Include a brief, bulleted summary of:
1. The exact error message.
2. The 3 attempted solutions that failed.
Wait for the user's explicit instructions before proceeding with any other tool.
```

---

## 6. Synthèse et cartographie avec la config actuelle

| Proposition Gemini | Config actuelle albert-agile | Statut |
|--------------------|------------------------------|--------|
| Routage ingest / architect / worker | Cascade qwen3 → gemini → claude, pas de routage par mots-clés | À intégrer |
| Routage sémantique (embeddings) | Mots-clés simples seulement ; nomic-embed-text disponible pour RAG | Évolution proposée : Python + nomic-embed-text + similarité cosinus |
| Disjoncteur HITL back-end | Non implémenté | À ajouter |
| Instructions HITL front-end | `litellm_hooks.py` (fix tool calls), pas de règle HITL explicite | À ajouter aux Custom Instructions Roo |
| Transfert de contexte IDE ↔ navigateur | Non documenté | À documenter / scripts à créer |
| Modèles DeepSeek, Gemini 3 Flash | qwen3 local, Gemini 2.5 Flash, Claude Sonnet | Adapter selon dispo API |

Voir [Plan_Configuration_VSCode_Ollama_Local.md](Plan_Configuration_VSCode_Ollama_Local.md) pour la configuration déployée et [Strategie_Modeles_LLM_Thinking_Albert_Agile.md](Strategie_Modeles_LLM_Thinking_Albert_Agile.md) pour la stratégie thinking/CoT.
