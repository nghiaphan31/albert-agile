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


def _invoke_with_retry(llm, prompt, schema=None):
    """Appel LLM avec retry sur HTTP 429."""
    for attempt in range(API_429_MAX_RETRIES + 1):
        try:
            if schema:
                chain = llm.with_structured_output(schema)
                return chain.invoke(prompt)
            return llm.invoke(prompt)
        except Exception as e:
            err_str = str(e).lower()
            if "429" in err_str or "rate" in err_str:
                if attempt < API_429_MAX_RETRIES:
                    wait = 2 ** attempt
                    logger.warning("API 429, retry %s/%s in %ss", attempt + 1, API_429_MAX_RETRIES, wait)
                    time.sleep(wait)
                else:
                    raise
            else:
                raise


def call_with_cascade(llm_n0, llm_n1, llm_n2, prompt, schema=None, h5_before_n2: bool = True):
    """
    Appelle N0, escalade vers N1 puis N2 en cas d'échec.
    Avant N2 : interrupt H5 (approbation API payante) si h5_before_n2.
    """
    # N0
    try:
        return _invoke_with_retry(llm_n0, prompt, schema)
    except Exception as e:
        logger.warning("n0_failure reason=%r escalating_to=N1", str(e))

    # N1 (cloud gratuit — anonymiser L-ANON)
    if llm_n1:
        try:
            prompt_n1 = _anonymize_prompt(prompt)
            return _invoke_with_retry(llm_n1, prompt_n1, schema)
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
        return _invoke_with_retry(llm_n2, prompt_n2, schema)

    raise RuntimeError("Tous les niveaux (N0, N1, N2) ont échoué.")
