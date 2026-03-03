"""
Tools pour R-4 (Albert Dev Team) et R-5 (Albert Release Manager) — spec III.8-H, F9, L8, L19.
read_file, write_file (atomique), run_shell (allowlist stricte).
"""

import os
import shlex
import subprocess
from pathlib import Path

# Allowlist : binaire -> set de sous-commandes autorisées, ou None = tous args OK
ALLOWLIST: dict[str, set[str] | None] = {
    "pip": {"install"},
    "pytest": None,
    "ruff": {"check", "format"},
    "git": {"add", "commit", "push", "checkout", "merge", "status", "diff", "log"},
    "gh": {"pr"},
    "npm": {"run"},
    "sphinx-build": None,
    "ollama": {"run"},
}


def read_file(path: str, project_root: Path) -> str:
    """Lecture d'un fichier (chemin relatif à project_root)."""
    full = (project_root / path).resolve()
    if not full.is_relative_to(project_root.resolve()):
        raise PermissionError(f"Chemin hors projet: {path}")
    return full.read_text(encoding="utf-8", errors="replace")


def write_file(path: str, content: str, project_root: Path, overwrite: bool = False) -> None:
    """
    Écriture atomique (F9) : .tmp puis os.replace.
    L19 : si overwrite=False et fichier existe, vérifier avant écrasement.
    """
    full = (project_root / path).resolve()
    if not full.is_relative_to(project_root.resolve()):
        raise PermissionError(f"Chemin hors projet: {path}")
    if full.exists() and not overwrite:
        raise FileExistsError(f"Fichier existe: {path}. Utiliser overwrite=True pour écraser.")
    tmp = full.with_suffix(full.suffix + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    os.replace(tmp, full)


def run_shell(cmd: str, cwd: Path, timeout: int = 300) -> subprocess.CompletedProcess:
    """
    Exécution avec allowlist stricte (L8 Non-destruction).
    Valide via shlex.split sur le premier token ET le sous-token.
    """
    parts = shlex.split(cmd)
    if not parts:
        raise ValueError("Commande vide")
    binary = parts[0]
    subcmd = parts[1] if len(parts) > 1 else None
    allowed_subcmds = ALLOWLIST.get(binary)
    if allowed_subcmds is None and binary not in ALLOWLIST:
        raise PermissionError(f"Binaire non autorisé : {binary!r}")
    if allowed_subcmds is not None and subcmd not in allowed_subcmds:
        raise PermissionError(f"Sous-commande non autorisée : {binary} {subcmd!r}")

    result = subprocess.run(
        parts,
        cwd=cwd,
        capture_output=True,
        text=True,
        timeout=timeout,
        env={**os.environ},
    )
    return result


def create_tools_r4(project_root: Path) -> list:
    """Crée les tools LangChain pour R-4 (read_file, write_file, run_shell)."""
    from langchain_core.tools import tool

    @tool
    def read_file_tool(path: str) -> str:
        """Lit un fichier du projet (chemin relatif à la racine)."""
        return read_file(path, project_root)

    @tool
    def write_file_tool(path: str, content: str, overwrite: bool = False) -> str:
        """Écrit un fichier (atomique). overwrite=True pour écraser."""
        write_file(path, content, project_root, overwrite=overwrite)
        return f"Écrit {path}"

    @tool
    def run_shell_tool(cmd: str) -> str:
        """Exécute une commande (allowlist: pip, pytest, ruff, git, gh, npm, sphinx-build, ollama)."""
        r = run_shell(cmd, project_root)
        out = (r.stdout or "") + (r.stderr or "")
        return f"exit={r.returncode}\n{out}" if out else f"exit={r.returncode}"

    return [read_file_tool, write_file_tool, run_shell_tool]


def create_tools_r5(project_root: Path) -> list:
    """Crée les tools LangChain pour R-5 (run_shell pour git/gh uniquement)."""
    from langchain_core.tools import tool

    @tool
    def run_shell_tool(cmd: str) -> str:
        """Exécute git ou gh (allowlist: git add/commit/push/checkout/merge/status/diff/log, gh pr)."""
        r = run_shell(cmd, project_root)
        out = (r.stdout or "") + (r.stderr or "")
        return f"exit={r.returncode}\n{out}" if out else f"exit={r.returncode}"

    return [run_shell_tool]
