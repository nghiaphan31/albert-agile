"""
Sandboxing par conteneurs (spec §7.1).
Exécute run_shell dans un conteneur Docker éphémère pour isoler pytest/scripts.
Activé via AGILE_SANDBOX_RUN_SHELL=true.
"""

import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

IMAGE_NAME = "albert-sandbox"
DEFAULT_TIMEOUT = 300


def run_shell_sandboxed(cmd: str, cwd: Path, timeout: int = DEFAULT_TIMEOUT) -> subprocess.CompletedProcess:
    """
    Exécute la commande dans un conteneur Docker éphémère.
    Monte cwd en /work, exécute cmd, supprime le conteneur à la fin.
    """
    cwd_resolved = cwd.resolve()
    docker_cmd = [
        "docker", "run", "--rm",
        "--network", "none",
        "-v", f"{cwd_resolved}:/work:rw",
        "-w", "/work",
        IMAGE_NAME,
        "sh", "-c", cmd,
    ]
    result = subprocess.run(
        docker_cmd,
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd_resolved,
    )
    return result


def is_sandbox_available() -> bool:
    """Vérifie si l'image sandbox existe et Docker est disponible."""
    try:
        r = subprocess.run(
            ["docker", "images", "-q", IMAGE_NAME],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return r.returncode == 0 and bool(r.stdout.strip())
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False


def build_sandbox_image() -> bool:
    """Build l'image albert-sandbox depuis docker/sandbox/Dockerfile."""
    root = Path(__file__).resolve().parent.parent
    dockerfile_dir = root / "docker" / "sandbox"
    if not (dockerfile_dir / "Dockerfile").exists():
        logger.warning("Dockerfile sandbox absent: %s", dockerfile_dir)
        return False
    try:
        subprocess.run(
            ["docker", "build", "-t", IMAGE_NAME, "."],
            cwd=dockerfile_dir,
            capture_output=True,
            text=True,
            timeout=120,
            check=True,
        )
        return True
    except (subprocess.CalledProcessError, FileNotFoundError, subprocess.TimeoutExpired) as e:
        logger.warning("Build sandbox failed: %s", e)
        return False
