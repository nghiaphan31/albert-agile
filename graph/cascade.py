"""
Cascade N0 vers N1 vers N2 (spec III.5, F8).
Sur escalade N2 : interrupt H5 (approbation API payante) avant d'appeler Claude.
L-ANON : anonymisation avant appels cloud (Gemini, Claude).
"""

import logging
import os
import time

logger = logging.getLogger(__name__)
API_429_MAX_RETRIES = int(os.environ.get("API_429_MAX_RETRIES", "3"))


def _anonymize_prompt(prompt):
    """Applique anonymisation L-ANON avant envoi cloud."""
    from graph.anonymizer import should_anonymize, scrub, apply_rules
    if not should_anonymize():
        return prompt
    if isinstance(prompt, str):
        return scrub(prompt)
    if isinstance(prompt, (list, tuple)):
        return apply_rules(list(prompt))
    return prompt


OLLAMA_500_MAX_RETRIES = int(os.environ.get("OLLAMA_500_MAX_RETRIES", "2"))


def _invoke_with_retry(llm, prompt, schema=None):
    """Appel LLM avec retry sur HTTP 429 et sur 500 Ollama (chargement modèle à froid)."""
    for attempt in range(max(API_429_MAX_RETRIES, OLLAMA_500_MAX_RETRIES) + 1):
        try:
            if schema:
                chain = llm.with_structured_output(schema)
                return chain.invoke(prompt)
            return llm.invoke(prompt)
        except Exception as e:
            err_str = str(e).lower()
            is_429 = "429" in err_str or "rate" in err_str
            is_ollama_500 = "500" in err_str and ("model runner" in err_str or "resource" in err_str or "ollama" in err_str)
            if is_429 and attempt < API_429_MAX_RETRIES:
                wait = 2 ** attempt
                logger.warning("API 429, retry %s/%s in %ss", attempt + 1, API_429_MAX_RETRIES, wait)
                time.sleep(wait)
            elif is_ollama_500 and attempt < OLLAMA_500_MAX_RETRIES:
                wait = 2 + attempt
                logger.warning("Ollama 500 (cold load?), retry %s/%s in %ss", attempt + 1, OLLAMA_500_MAX_RETRIES, wait)
                time.sleep(wait)
            else:
                raise


def _debug_log(msg: str, data: dict):
    try:
        import json
        from pathlib import Path
        proj = Path(__file__).resolve().parent.parent
        lp = proj / ".cursor" / "debug-8b4759.log"
        lp.parent.mkdir(parents=True, exist_ok=True)
        entry = {"sessionId": "8b4759", "location": "graph/cascade.py", "message": msg, "data": data, "timestamp": __import__("time").time() * 1000}
        with open(lp, "a") as f:
            f.write(json.dumps(entry) + "\n")
    except Exception:
        pass

def _model_name(llm) -> str:
    """Nom du modèle pour la signature (tier1-n0, gemini-2.5-flash, etc.)."""
    return str(getattr(llm, "model", "?"))


def call_with_cascade(llm_n0, llm_n1, llm_n2, prompt, schema=None, h5_before_n2: bool = True):
    """
    Appelle N0, escalade vers N1 puis N2 en cas d'échec.
    Avant N2 : interrupt H5 (approbation API payante) si h5_before_n2.
    Retourne (result, model_name) pour permettre de signer la réponse.
    """
    # #region agent log
    _ollama_loaded = None
    try:
        import urllib.request
        u = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
        if not u.startswith("http"):
            u = "http://" + u
        u = u.rstrip("/") + "/api/ps"
        with urllib.request.urlopen(u, timeout=2) as r:
            j = __import__("json").loads(r.read().decode())
            _ollama_loaded = [p.get("name") for p in j.get("models", [])]
    except Exception as xe:
        _ollama_loaded = f"check_failed:{type(xe).__name__}"
    _debug_log("call_with_cascade N0 pre-invoke", {
        "n0_model": getattr(llm_n0, "model", "?"),
        "n0_base_url": getattr(llm_n0, "base_url", None),
        "OLLAMA_KEEP_ALIVE": os.environ.get("OLLAMA_KEEP_ALIVE"),
        "OLLAMA_HOST": os.environ.get("OLLAMA_HOST"),
        "ollama_loaded_now": _ollama_loaded,
        "prompt_size": len(str(prompt)),
        "prompt_type": type(prompt).__name__,
        "hypothesisId": "H1,H2,H3",
    })
    # #endregion
    # N0 warmup: si aucun modèle chargé, précharger via API Ollama (évite 500 cold-load)
    # Ignoré si AGILE_USE_LITELLM_PROXY (on passe par le proxy, pas Ollama direct)
    use_proxy = os.environ.get("AGILE_USE_LITELLM_PROXY", "").lower() in ("1", "true", "yes")
    n0_model = getattr(llm_n0, "model", None)
    if not use_proxy and _ollama_loaded == [] and n0_model and n0_model != "?":
        try:
            import urllib.request
            import json as _json
            base = os.environ.get("OLLAMA_HOST", "http://localhost:11434")
            if not base.startswith("http"):
                base = "http://" + base
            url = base.rstrip("/") + "/api/generate"
            req = urllib.request.Request(url, data=_json.dumps({"model": n0_model, "prompt": ".", "stream": False}).encode(), method="POST", headers={"Content-Type": "application/json"})
            with urllib.request.urlopen(req, timeout=60) as _:
                pass
            logger.info("Ollama warmup: %s préchargé", n0_model)
        except Exception as we:
            logger.debug("Ollama warmup ignoré: %s", we)
    # N0
    _n0_schema = schema
    if os.environ.get("CASCADE_N0_SKIP_STRUCTURED") == "1":
        _n0_schema = None  # H6 test: raw invoke
    try:
        out = _invoke_with_retry(llm_n0, prompt, _n0_schema)
        _debug_log("call_with_cascade N0 success", {"used_schema": _n0_schema is not None, "hypothesisId": "H6"})
        return out, _model_name(llm_n0)
    except Exception as e:
        # #region agent log
        _debug_log("call_with_cascade N0 failure", {
            "exc_type": type(e).__name__,
            "exc_msg": str(e)[:800],
            "used_schema": _n0_schema is not None,
            "has_500": "500" in str(e),
            "hypothesisId": "H6,H7",
        })
        # #endregion
        logger.warning("n0_failure reason=%r escalating_to=N1", str(e))

    # N1 (cloud gratuit — anonymiser L-ANON)
    if llm_n1:
        try:
            prompt_n1 = _anonymize_prompt(prompt)
            out = _invoke_with_retry(llm_n1, prompt_n1, schema)
            return out, _model_name(llm_n1)
        except Exception as e:
            logger.warning("n1_failure reason=%r escalating_to=N2", str(e))

    # N2 (cloud payant — anonymiser L-ANON, H5 interrupt avant Claude)
    if llm_n2:
        prompt_n2 = _anonymize_prompt(prompt)
        if h5_before_n2:
            from langgraph.types import interrupt as lg_interrupt
            ctx = str(prompt)[:500] if not isinstance(prompt, (list, tuple)) else str(prompt)[:500]
            human_ok = lg_interrupt({"reason": "H5", "payload": {"escalation": "N2_claude", "context": ctx}})
            if not (isinstance(human_ok, dict) and human_ok.get("status") == "approved"):
                raise PermissionError("Escalade N2 refusée par l'humain")
        out = _invoke_with_retry(llm_n2, prompt_n2, schema)
        return out, _model_name(llm_n2)

    raise RuntimeError("Tous les niveaux (N0, N1, N2) ont échoué.")
