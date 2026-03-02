#!/usr/bin/env python3
"""
Gestion des interrupts H1–H6 (spec III.8-B).

Sans --thread-id : liste tous les threads en attente d'un interrupt.
Avec --thread-id  : affiche le payload, demande approved/rejected/feedback,
                    puis reprend le graphe via graph.invoke(Command(resume=...)).

Approche : accès Python direct au graphe et au checkpointer SQLite.
LangServe n'expose pas d'endpoint /runs/{id}/resume — cette route est propre
à LangGraph Platform (cloud). On bypass le HTTP.
"""
import argparse
import json
import sqlite3
import sys
from pathlib import Path

# Le projet d'orchestration est le parent de ce script
ORCH_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ORCH_ROOT))

from dotenv import load_dotenv

load_dotenv(ORCH_ROOT / ".env")

from langgraph.types import Command

from graph.graph import CHECKPOINT_PATH, graph


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _all_thread_ids() -> list[str]:
    """Retourne tous les thread_id distincts depuis le checkpointer SQLite."""
    if not CHECKPOINT_PATH.exists():
        return []
    conn = sqlite3.connect(str(CHECKPOINT_PATH))
    try:
        cur = conn.cursor()
        cur.execute("SELECT DISTINCT thread_id FROM checkpoints ORDER BY thread_id")
        return [r[0] for r in cur.fetchall()]
    finally:
        conn.close()


def _get_interrupts(thread_id: str) -> list:
    """
    Retourne la liste des Interrupt actifs pour un thread via graph.get_state().
    Résultat vide si le thread est terminé ou inexistant.
    """
    config = {"configurable": {"thread_id": thread_id}}
    try:
        snap = graph.get_state(config)
    except Exception as e:
        print(f"  [avertissement] get_state({thread_id!r}) : {e}", file=sys.stderr)
        return []
    interrupts = []
    for task in snap.tasks:
        if task.interrupts:
            interrupts.extend(task.interrupts)
    return interrupts


def _list_pending() -> list[tuple[str, list]]:
    """Retourne [(thread_id, [Interrupt, ...]), ...] pour tous les threads en attente."""
    pending = []
    for tid in _all_thread_ids():
        intr = _get_interrupts(tid)
        if intr:
            pending.append((tid, intr))
    return pending


def _display_interrupts(thread_id: str, interrupts: list) -> None:
    print(f"\nThread : {thread_id!r}  —  {len(interrupts)} interrupt(s) en attente\n")
    for i, intr in enumerate(interrupts, 1):
        val = intr.value if hasattr(intr, "value") else intr
        print(f"[{i}] Payload :")
        try:
            print(json.dumps(val, indent=4, ensure_ascii=False, default=str))
        except Exception:
            print(f"    {val}")


def _ask_decision(args: argparse.Namespace) -> dict:
    """Construit le dict de décision depuis les arguments ou une invite interactive."""
    if args.approved:
        return {"status": "approved"}
    if args.rejected:
        feedback = args.feedback or ""
        if not feedback:
            feedback = input("Feedback (raison du rejet) : ").strip()
        return {"status": "rejected", "feedback": feedback}
    if args.feedback:
        return {"status": "feedback", "feedback": args.feedback}

    # Mode interactif
    print("\nDécision [approved / rejected / feedback] : ", end="", flush=True)
    choice = input().strip().lower()
    if choice == "approved":
        return {"status": "approved"}
    if choice in ("rejected", "feedback"):
        fb = input("Feedback : ").strip()
        return {"status": choice, "feedback": fb}
    print(f"Choix non reconnu : {choice!r}. Valeurs acceptées : approved, rejected, feedback.")
    sys.exit(2)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Gérer les interrupts H1–H6 (spec III.8-B)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=(
            "Exemples :\n"
            "  python scripts/handle_interrupt.py\n"
            "  python scripts/handle_interrupt.py --thread-id mon-projet-phase-0 --approved\n"
            "  python scripts/handle_interrupt.py --thread-id mon-projet-phase-0 --rejected --feedback 'Revoir le scope'\n"
        ),
    )
    parser.add_argument("--thread-id", help="Thread ID spécifique (sinon liste tous les threads en attente)")
    parser.add_argument("--approved", action="store_true", help="Approuver sans prompt interactif")
    parser.add_argument("--rejected", action="store_true", help="Rejeter sans prompt interactif")
    parser.add_argument("--feedback", default="", help="Feedback texte (combine avec --rejected ou seul)")
    args = parser.parse_args()

    # --- Mode liste ---
    if not args.thread_id:
        pending = _list_pending()
        if not pending:
            print("Aucun interrupt en attente.")
            return 0
        print(f"{len(pending)} thread(s) en attente d'un interrupt :\n")
        for tid, interrupts in pending:
            reason = ""
            if interrupts:
                val = interrupts[0].value if hasattr(interrupts[0], "value") else {}
                reason = val.get("reason", "") if isinstance(val, dict) else ""
            tag = f"  [{reason}]" if reason else ""
            print(f"  {tid}{tag}")
        print(f"\nPour traiter un thread :")
        print(f"  python scripts/handle_interrupt.py --thread-id <thread_id>")
        return 0

    # --- Mode traitement d'un thread ---
    interrupts = _get_interrupts(args.thread_id)
    if not interrupts:
        print(f"Aucun interrupt actif pour le thread '{args.thread_id}'.")
        print("(Le thread est peut-être terminé ou n'existe pas.)")
        return 0

    _display_interrupts(args.thread_id, interrupts)
    decision = _ask_decision(args)
    print(f"\nEnvoi de la décision : {decision}")

    config = {"configurable": {"thread_id": args.thread_id}}
    try:
        result = graph.invoke(Command(resume=decision), config=config)
    except Exception as e:
        print(f"Erreur lors de la reprise du graphe : {e}", file=sys.stderr)
        return 1

    if "__interrupt__" in result:
        next_interrupts = result["__interrupt__"]
        print(f"\nGraphe suspendu à nouveau — {len(next_interrupts)} prochain(s) interrupt(s) :")
        for intr in next_interrupts:
            val = intr.value if hasattr(intr, "value") else intr
            reason = val.get("reason", "?") if isinstance(val, dict) else "?"
            print(f"  [{reason}]")
        print(f"\n  python scripts/handle_interrupt.py --thread-id {args.thread_id}")
    else:
        print("\nGraphe repris et terminé avec succès.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
