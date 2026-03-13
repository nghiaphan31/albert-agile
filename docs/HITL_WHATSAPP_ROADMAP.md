# HITL déporté WhatsApp (spec §7.2) — Roadmap

**Statut** : optionnel, non implémenté.

## Objectif

Envoyer les interrupts (H1–H6) vers WhatsApp au lieu de bloquer sur `handle_interrupt.py` dans VS Code. Validation depuis le téléphone, puis le graphe reprend.

## Architecture proposée

```
LangGraph (interrupt) → Gateway → WhatsApp (Baileys / API Business)
                                        ↓
                              Utilisateur répond (approved/rejected)
                                        ↓
                              Gateway → graph.invoke(Command(resume=...))
```

## Composants

| Composant            | Description                                      |
|----------------------|--------------------------------------------------|
| Gateway              | Service Python entre LangGraph et le connecteur WhatsApp |
| Connecteur WhatsApp  | Baileys (non-officiel) ou API WhatsApp Business  |
| Mapping thread_id    | Associer chaque conversation au `thread_id` LangGraph |

## Prérequis

- Compte WhatsApp Business (pour API officielle) ou usage de Baileys
- Conformité RGPD pour stockage des échanges
- Infrastructure pour héberger la Gateway

## Décision

Phase marquée comme **roadmap**. À documenter dans une spec dédiée si priorisé.
