#!/usr/bin/env python3
"""
Script de test E2E manuel — enchaîne les étapes de validation du flux Agile.

Usage:
  python scripts/test_e2e_manual.py --check-prereq     # Vérifications préalables
  python scripts/test_e2e_manual.py --run-e1          # Lance E1 (atteint H1)
  python scripts/test_e2e_manual.py --list-interrupts # Liste les interrupts
  python scripts/test_e2e_manual.py --status          # Affiche status
  python scripts/test_e2e_manual.py --all             # Exécute tout (prereq + E1 + list + status)

Options:
  --project-id ID   Projet à tester (défaut: albert-agile)
  --thread-id ID    Thread ID (défaut: {project_id}-e2e-test)
  --timeout N       Timeout secondes pour run E1 (défaut: 180)
  --approved        Avec --run-e1, valide automatiquement H1 (approved)
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ORCH_ROOT = Path(__file__).resolve().parent.parent


def _run(cmd: list[str], timeout: int | None = 30, capture: bool = True, extra_env: dict | None = None) -> tuple[int, str]:
    """Exécute une commande, retourne (exit_code, output)."""
    env = {**os.environ, "AGILE_ORCHESTRATION_ROOT": str(ORCH_ROOT)}
    if extra_env:
        env.update(extra_env)
    try:
        r = subprocess.run(
            cmd,
            cwd=ORCH_ROOT,
            capture_output=capture,
            text=True,
            timeout=timeout,
            env=env,
        )
        out = (r.stdout or "") + (r.stderr or "")
        return r.returncode, out
    except subprocess.TimeoutExpired:
        return -1, f"Timeout après {timeout}s"
    except Exception as e:
        return -1, str(e)


def check_prereq() -> int:
    """Vérifie les prérequis (venv, ollama, imports)."""
    errors = []
    # 1. Venv
    venv_py = ORCH_ROOT / ".venv" / "bin" / "python"
    if not venv_py.exists():
        errors.append("Venv absent : .venv/bin/python")
    # 2. Import graphe
    code, out = _run([str(venv_py), "-c", "from graph.graph import graph; print('OK')"], timeout=10)
    if code != 0:
        errors.append(f"Import graphe échoué : {out[:200]}")
    # 3. Ollama
    code, _ = _run(["ollama", "list"], timeout=5)
    if code != 0:
        errors.append("ollama list échoué (Ollama démarré ?)")
    # 4. projects.json
    if not (ORCH_ROOT / "config" / "projects.json").exists():
        errors.append("config/projects.json absent")

    if errors:
        print("PREREQ KO:")
        for e in errors:
            print(f"  - {e}")
        return 1
    print("PREREQ OK (venv, graphe, ollama, config)")
    return 0


def run_e1(project_id: str, thread_id: str, timeout: int, auto_approved: bool) -> int:
    """Lance run_graph E1. Attend interrupt H1 ou timeout.
    E1 utilise tier1 (gemma3) — OLLAMA_KEEP_ALIVE=gemma3 évite le 500 lors du swap modèle.
    """
    py = ORCH_ROOT / ".venv" / "bin" / "python"
    cmd = [str(py), str(ORCH_ROOT / "run_graph.py"), "--project-id", project_id, "--start-phase", "E1", "--thread-id", thread_id]
    print(f"Lancement: python run_graph.py --project-id {project_id} --start-phase E1 --thread-id {thread_id} (timeout={timeout}s)")
    # E1 utilise tier1 (gemma3) ; OLLAMA_KEEP_ALIVE=gemma3 évite 500 lors du swap (H1 root cause).
    code, out = _run(cmd, timeout=timeout, extra_env={"OLLAMA_KEEP_ALIVE": "gemma3:12b-it-q4_K_M"})
    print(out)
    if code != 0:
        print("RUN E1 KO (exit code", code, ")")
        return 1
    if "suspendu" in out or "__interrupt__" in str(out).lower() or "handle_interrupt" in out:
        print("RUN E1 OK — graphe suspendu sur H1")
        if auto_approved:
            code2, out2 = _run([str(py), str(ORCH_ROOT / "scripts" / "handle_interrupt.py"), "--thread-id", thread_id, "--approved"], timeout=30)
            print(out2)
            return 0 if code2 == 0 else 1
        return 0
    if "terminé" in out or "Run terminé" in out:
        print("RUN E1 OK — graphe terminé (sans interrupt)")
        return 0
    print("RUN E1 ? — sortie ambiguë")
    return 0


def list_interrupts() -> int:
    """Liste les interrupts en attente."""
    py = ORCH_ROOT / ".venv" / "bin" / "python"
    code, out = _run([str(py), str(ORCH_ROOT / "scripts" / "handle_interrupt.py")], timeout=10)
    print(out)
    return code


def run_status(project_id: str | None) -> int:
    """Affiche status.py."""
    py = ORCH_ROOT / ".venv" / "bin" / "python"
    cmd = [str(py), str(ORCH_ROOT / "scripts" / "status.py")]
    if project_id:
        cmd.extend(["--project-id", project_id])
    code, out = _run(cmd, timeout=10)
    print(out)
    return code


def main() -> int:
    parser = argparse.ArgumentParser(description="Test E2E manuel du flux Agile")
    parser.add_argument("--check-prereq", action="store_true", help="Vérifier prérequis")
    parser.add_argument("--run-e1", action="store_true", help="Lancer E1 (idéation)")
    parser.add_argument("--list-interrupts", action="store_true", help="Lister interrupts")
    parser.add_argument("--status", action="store_true", help="Afficher status")
    parser.add_argument("--all", action="store_true", help="Exécuter tout")
    parser.add_argument("--project-id", default="albert-agile")
    parser.add_argument("--thread-id", default=None)
    parser.add_argument("--timeout", type=int, default=180)
    parser.add_argument("--approved", action="store_true", help="Valider H1 automatiquement")
    args = parser.parse_args()

    thread_id = args.thread_id or f"{args.project_id}-e2e-test"
    os.chdir(ORCH_ROOT)

    if args.all:
        args.check_prereq = True
        args.run_e1 = True
        args.list_interrupts = True
        args.status = True

    if not any([args.check_prereq, args.run_e1, args.list_interrupts, args.status]):
        parser.print_help()
        return 0

    exit_code = 0
    if args.check_prereq:
        exit_code |= check_prereq()
    if args.run_e1:
        exit_code |= run_e1(args.project_id, thread_id, args.timeout, args.approved)
    if args.list_interrupts:
        exit_code |= list_interrupts()
    if args.status:
        exit_code |= run_status(args.project_id)

    return min(exit_code, 1)


if __name__ == "__main__":
    sys.exit(main())
