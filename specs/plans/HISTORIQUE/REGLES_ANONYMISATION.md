# Règles d'anonymisation cloud (L-ANON)

**Règle absolue** : Aucune donnée personnelle ne quitte Calypso vers le cloud (Gemini, Claude) sans anonymisation préalable ou autorisation explicite du superviseur désigné (rôle R-1/R-7). L'IA locale (Ollama) est la gateway de sortie.

## Données considérées personnelles

- Noms de personnes
- Emails
- Chemins `/home/...`
- Adresses IP
- URLs internes
- Clés API, tokens, identifiants

## Patterns de détection

- **Emails** : `[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}`
- **Chemins Unix** : `/home/[^/]+/`
- **Noms de machines** : hostname, noms de serveurs internes
- **Clés** : `sk-`, `AIza`, patterns token

## Règles de remplacement

| Donnée | Placeholder |
|--------|-------------|
| `nghia-phan` (username) | `[USER]` |
| `/home/nghia-phan/PROJECTS_WITH_ALBERT/` | `[PROJECT_ROOT]/` |
| Emails | `[EMAIL_REDACTED]` |
| IPs | `[IP_REDACTED]` |

## Procédure d'autorisation explicite

- Si `AGILE_ALLOW_PERSONAL_CLOUD=true` + confirmation via interrupt ou `handle_interrupt.py` — seul le superviseur désigné (rôle R-1/R-7) peut débloquer l'envoi de données non anonymisées.
