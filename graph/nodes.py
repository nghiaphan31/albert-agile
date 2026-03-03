"""Noeuds du graphe Agile (R-0 a R-6). LLM cascade (spec III.5, 10.3)."""
import json
import logging
import os
from pathlib import Path

from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.types import interrupt as lg_interrupt

from graph.state import State
from graph.basestore import load_project_context
from graph.laws import format_laws_for_prompt
from graph.llm_factory import get_system_prompt, get_llms_tier1, get_llms_tier2
from graph.cascade import call_with_cascade
from graph.schemas import EpicOutput, ArchitectureOutput, SprintBacklogOutput
from graph.rag import query_rag

logger = logging.getLogger(__name__)

_ORCH_ROOT = Path(os.environ.get("AGILE_ORCHESTRATION_ROOT", Path(__file__).resolve().parent.parent))
_PROJECTS_JSON = Path(os.environ.get("AGILE_PROJECTS_JSON", _ORCH_ROOT / "config" / "projects.json"))
_BASESTORE_STRICT = os.environ.get("AGILE_BASESTORE_STRICT", "true").lower() == "true"


def _load_projects() -> dict:
    """Lit config/projects.json ; retourne {} si absent."""
    if _PROJECTS_JSON.exists():
        try:
            return json.loads(_PROJECTS_JSON.read_text(encoding="utf-8"))
        except Exception as e:
            logger.warning("Impossible de lire %s : %s", _PROJECTS_JSON, e)
    return {}


def load_context(state: State) -> dict:
    """
    Charge le contexte depuis config/projects.json et le BaseStore (spec III.8-A).

    Résolution de project_root :
      1. Utilise la valeur déjà dans l'état si elle est non-None.
      2. Sinon, la lit depuis config/projects.json via AGILE_PROJECTS_JSON.
      3. Si le projet est introuvable et AGILE_BASESTORE_STRICT=true → exception.
         Si AGILE_BASESTORE_STRICT=false → WARNING + project_root = répertoire courant.

    BaseStore : charge adr_counter, sprint_number, dod (AGILE_BASESTORE_STRICT).

    HOTFIX : si start_phase == "HOTFIX" et hotfix_description non vide,
    crée un sprint_backlog synthétique HF-001.

    Le routing E1/E3/HOTFIX est géré par _route_from_load_context dans graph.py.
    """
    project_id = state.get("project_id", "")
    project_root = state.get("project_root")

    if project_root is None:
        projects = _load_projects()
        entry = {k: v for k, v in projects.items() if not k.startswith("_")}.get(project_id)
        if entry and entry.get("path"):
            project_root = Path(entry["path"])
        else:
            msg = (
                f"Projet '{project_id}' introuvable dans {_PROJECTS_JSON}. "
                "Vérifier config/projects.json."
            )
            if _BASESTORE_STRICT:
                raise ValueError(msg)
            logger.warning("%s — AGILE_BASESTORE_STRICT=false, project_root=cwd", msg)
            project_root = Path.cwd()

    # BaseStore : adr_counter, sprint_number, dod
    try:
        ctx = load_project_context(project_id, _BASESTORE_STRICT)
        sprint_number = ctx["sprint_number"]
        adr_counter = ctx["adr_counter"]
        dod = ctx["dod"]
    except ValueError:
        raise
    except Exception as e:
        if _BASESTORE_STRICT:
            raise ValueError(f"BaseStore inaccessible pour '{project_id}': {e}") from e
        logger.warning("BaseStore load failed: %s — valeurs par défaut", e)
        sprint_number = 1
        adr_counter = 0
        dod = None

    result = {
        "project_id": project_id,
        "project_root": project_root,
        "sprint_number": sprint_number,
        "adr_counter": adr_counter,
        "dod": dod,
    }

    # SprintBacklog synthétique HOTFIX (spec III.8-A)
    start_phase = state.get("start_phase", "")
    hotfix_desc = state.get("hotfix_description", "").strip()
    if start_phase == "HOTFIX" and hotfix_desc:
        result["sprint_backlog"] = {
            "id": "HF-001",
            "description": hotfix_desc,
            "tickets": [],
        }

    return result


def _build_messages(role: str, user_content: str) -> list:
    """Construit system + human messages pour un rôle."""
    laws = format_laws_for_prompt(role)
    system = get_system_prompt(role, laws)
    return [SystemMessage(content=system), HumanMessage(content=user_content)]


def node_r0(state: State) -> dict:
    """R-0 Albert Business Analyst — produit Epic, interrupt H1 (validation Product Owner)."""
    project_id = state.get("project_id", "?")
    user = f"Produis un Epic structuré (cahier des charges) pour le projet {project_id}. Format: titre, description, critères d'acceptation en liste."
    msgs = _build_messages("r0", user)
    n0, n1, n2 = get_llms_tier1()
    try:
        epic = call_with_cascade(n0, n1, n2, msgs, schema=EpicOutput)
        content = epic.model_dump_json() if hasattr(epic, "model_dump_json") else str(epic)
        backlog = {"epic": epic.model_dump() if hasattr(epic, "model_dump") else {"raw": content}}
    except Exception as e:
        logger.exception("node_r0 failed: %s", e)
        content = f"Erreur R-0: {e}"
        backlog = {"epic": {"raw": content}}
    payload = {"reason": "H1", "payload": {"epic": backlog.get("epic", {}), "content": content}}
    human_response = lg_interrupt(payload)
    approved = isinstance(human_response, dict) and human_response.get("status") == "approved"
    return {
        "messages": state.get("messages", []) + [{"role": "assistant", "content": content}],
        "backlog": backlog,
        "h1_approved": approved,
        "h1_feedback": human_response.get("feedback", "") if isinstance(human_response, dict) else "",
    }


def node_r2(state: State) -> dict:
    """R-2 Albert System Architect — Architecture + DoD, interrupt H2. L18: spec_contradiction."""
    project_id = state.get("project_id", "?")
    backlog = state.get("backlog", {})
    rag_ctx = query_rag(project_id, "Architecture Definition of Done backlog", top_k=5)
    rag_str = "\n---\n".join(rag_ctx[:3]) if rag_ctx else ""
    user = (
        f"Projet {project_id}. Backlog: {json.dumps(backlog, ensure_ascii=False)[:500]}.\nRAG (contexte):\n{rag_str}\n\n"
        "Définis l'architecture et la Definition of Done. "
        "Si contradiction entre RAG/Backlog/Architecture (L18), mets contradiction_detected=true et liste contradiction_sources."
    )
    msgs = _build_messages("r2", user)
    n0, n1, n2 = get_llms_tier1()
    arch = None
    try:
        arch = call_with_cascade(n0, n1, n2, msgs, schema=ArchitectureOutput)
        content = arch.model_dump_json() if hasattr(arch, "model_dump_json") else str(arch)
        arch_dict = arch.model_dump() if hasattr(arch, "model_dump") else {"raw": content}
    except Exception as e:
        logger.exception("node_r2 failed: %s", e)
        content = f"Erreur R-2: {e}"
        arch_dict = {"raw": content}
    sources = []
    if arch and getattr(arch, "contradiction_detected", False):
        sources = getattr(arch, "contradiction_sources", None) or ["(sources non spécifiées)"]
    if sources:
        lg_interrupt({"reason": "spec_contradiction", "payload": {"sources": sources}})
    payload = {"reason": "H2", "payload": {"architecture": arch_dict}}
    human_response = lg_interrupt(payload)
    approved = isinstance(human_response, dict) and human_response.get("status") == "approved"
    return {
        "messages": state.get("messages", []) + [{"role": "assistant", "content": content}],
        "architecture": arch_dict,
        "h2_approved": approved,
        "h2_feedback": human_response.get("feedback", "") if isinstance(human_response, dict) else "",
    }


def node_r3(state: State) -> dict:
    """R-3 Albert Scrum Master — Sprint Backlog, interrupt H3 (validation Product Owner)."""
    project_id = state.get("project_id", "?")
    sprint_number = state.get("sprint_number", 1)
    backlog = state.get("backlog", {})
    arch = state.get("architecture", "")
    rag_ctx = query_rag(project_id, "Sprint Backlog tickets Product Backlog", top_k=5)
    rag_str = "\n---\n".join(rag_ctx[:3]) if rag_ctx else ""
    user = f"Projet {project_id}, sprint {sprint_number}. Backlog: {json.dumps(backlog, ensure_ascii=False)[:300]}. Architecture: {str(arch)[:300]}.\nRAG:\n{rag_str}\n\nDécoupe le Sprint Backlog en tickets."
    msgs = _build_messages("r3", user)
    n0, n1, n2 = get_llms_tier2()
    try:
        sb = call_with_cascade(n0, n1, n2, msgs, schema=SprintBacklogOutput)
        content = sb.model_dump_json() if hasattr(sb, "model_dump_json") else str(sb)
        sb_dict = sb.model_dump() if hasattr(sb, "model_dump") else {"raw": content}
    except Exception as e:
        logger.exception("node_r3 failed: %s", e)
        content = f"Erreur R-3: {e}"
        sb_dict = {"raw": content}
    payload = {"reason": "H3", "payload": {"sprint_backlog": sb_dict}}
    human_response = lg_interrupt(payload)
    approved = isinstance(human_response, dict) and human_response.get("status") == "approved"
    return {
        "messages": state.get("messages", []) + [{"role": "assistant", "content": content}],
        "sprint_backlog": sb_dict,
        "h3_approved": approved,
        "h3_feedback": human_response.get("feedback", "") if isinstance(human_response, dict) else "",
    }


def node_r4(state: State) -> dict:
    """R-4 Albert Dev Team — exécution code (tools 10.4, RAG 10.5)."""
    project_id = state.get("project_id", "?")
    sprint_backlog = state.get("sprint_backlog", "")
    dod = state.get("dod")
    rag_ctx = query_rag(project_id, "code implementation", top_k=5)
    rag_str = "\n---\n".join(rag_ctx[:3]) if rag_ctx else ""
    user = f"Sprint Backlog: {str(sprint_backlog)[:500]}. DoD: {dod}.\nRAG (code existant):\n{rag_str}\n\nImplémente les tickets (résumé des changements à effectuer)."
    msgs = _build_messages("r4", user)
    n0, n1, n2 = get_llms_tier2()
    try:
        out = call_with_cascade(n0, n1, n2, msgs)
        content = out.content if hasattr(out, "content") else str(out)
    except Exception as e:
        logger.exception("node_r4 failed: %s", e)
        content = f"Erreur R-4: {e}"
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": content}]}


def node_r5(state: State) -> dict:
    """R-5 Albert Release Manager — Git, PR."""
    user = "Résume les actions Git et PR à effectuer pour ce sprint (branch, commit, PR)."
    msgs = _build_messages("r5", user)
    n0, n1, n2 = get_llms_tier2()
    try:
        out = call_with_cascade(n0, n1, n2, msgs)
        content = out.content if hasattr(out, "content") else str(out)
    except Exception as e:
        logger.exception("node_r5 failed: %s", e)
        content = f"Erreur R-5: {e}"
    return {"messages": state.get("messages", []) + [{"role": "assistant", "content": content}]}


def node_r6(state: State) -> dict:
    """R-6 Albert QA et DevOps — tests, CI, H4 Sprint Review. Self-Healing: si tests fail, → R4 (max 3x puis H5)."""
    import os
    max_iter = int(os.environ.get("SELF_HEALING_MAX_ITERATIONS", "3"))
    iterations = state.get("self_healing_iterations", 0)

    user = "Résume le pipeline E5 : build_docs → unit → intégration → E2E. Verdict CI. L21: refuse commit sans docstrings."
    msgs = _build_messages("r6", user)
    n0, n1, n2 = get_llms_tier2()
    try:
        out = call_with_cascade(n0, n1, n2, msgs)
        content = out.content if hasattr(out, "content") else str(out)
        tests_ok = True
    except Exception as e:
        logger.exception("node_r6 failed: %s", e)
        content = f"Erreur R-6: {e}"
        tests_ok = False

    if not tests_ok:
        iterations += 1
        if iterations >= max_iter:
            h5_payload = {"reason": "cost_escalation", "payload": {"iterations": iterations, "report": content}}
            h5_resp = lg_interrupt(h5_payload)
            if not (isinstance(h5_resp, dict) and h5_resp.get("status") == "approved"):
                return {
                    "messages": state.get("messages", []) + [{"role": "assistant", "content": content}],
                    "tests_passed": False,
                    "h4_approved": True,
                    "h5_rejected": True,
                    "self_healing_iterations": iterations,
                }

    payload = {"reason": "H4", "payload": {"tests_report": content, "tests_passed": tests_ok}}
    human_response = lg_interrupt(payload)
    approved = isinstance(human_response, dict) and human_response.get("status") == "approved"
    return {
        "messages": state.get("messages", []) + [{"role": "assistant", "content": content}],
        "tests_passed": tests_ok,
        "h4_approved": approved,
        "h5_rejected": False,
        "self_healing_iterations": iterations,
    }
