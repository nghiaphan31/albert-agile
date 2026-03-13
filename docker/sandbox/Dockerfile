# Sandbox Docker (spec §7.1) — exécution pytest / scripts isolée
# Usage: docker run --rm -v PROJECT_ROOT:/work -w /work albert-sandbox pytest ...
FROM python:3.12-slim

RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir pytest>=8.0 ruff

WORKDIR /work
