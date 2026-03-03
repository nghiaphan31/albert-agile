"""Pytest fixtures pour les tests E2E."""
import os
import sys
from pathlib import Path

# Ajouter la racine du projet au path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
os.environ.setdefault("AGILE_ORCHESTRATION_ROOT", str(ROOT))
