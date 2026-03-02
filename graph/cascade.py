"""Cascade N0 vers N1 vers N2 (spec III.5, F8)."""
import logging
import os

logger = logging.getLogger(__name__)
API_429_MAX_RETRIES = int(os.environ.get("API_429_MAX_RETRIES", "3"))


def call_with_cascade(llm_n0, llm_n1, llm_n2, prompt: str, schema=None):
    """Appelle N0, escalade vers N1 puis N2 en cas d'echec."""
    try:
        if schema:
            chain = llm_n0.with_structured_output(schema)
            return chain.invoke(prompt)
        return llm_n0.invoke(prompt)
    except Exception as e:
        logger.warning("n0_failure reason=%r escalating_to=N1", str(e))
    try:
        if schema:
            chain = llm_n1.with_structured_output(schema)
            return chain.invoke(prompt)
        return llm_n1.invoke(prompt)
    except Exception as e:
        logger.warning("n1_failure reason=%r escalating_to=N2", str(e))
    if schema:
        chain = llm_n2.with_structured_output(schema)
        return chain.invoke(prompt)
    return llm_n2.invoke(prompt)
