from __future__ import annotations

from collections.abc import Callable

from langgraph.graph import END, START, StateGraph

from skill_path.config import Settings
from skill_path.services.progress import ProgressReporter
from skill_path.state import EvaluationState


def route_after_guardrail(state: EvaluationState) -> str:
    status = state.get("guardrail_status", "FAIL")
    if status == "PASS":
        return "pass"
    if status == "RETRY":
        return "retry"
    return "fail"


def _wrap_node(
    node_name: str,
    node: Callable[[EvaluationState], dict[str, object]],
    reporter: ProgressReporter | None,
) -> Callable[[EvaluationState], dict[str, object]]:
    if reporter is None:
        return node

    def wrapped_node(state: EvaluationState) -> dict[str, object]:
        reporter.on_node_start(node_name, state)
        update = node(state)
        reporter.on_node_end(node_name, update)
        return update

    return wrapped_node


def build_graph(settings: Settings, reporter: ProgressReporter | None = None):
    from skill_path.nodes.calculate_score import calculate_score_node
    from skill_path.nodes.draft_evaluation import build_draft_evaluation_node
    from skill_path.nodes.extract_cv_skills import build_extract_cv_skills_node
    from skill_path.nodes.guardrail_check import build_guardrail_check_node
    from skill_path.nodes.load_roadmap_data import load_roadmap_data

    builder = StateGraph(EvaluationState)

    builder.add_node(
        "extract_cv_skills",
        _wrap_node("extract_cv_skills", build_extract_cv_skills_node(settings), reporter),
    )
    builder.add_node("load_roadmap_data", _wrap_node("load_roadmap_data", load_roadmap_data, reporter))
    builder.add_node("calculate_score", _wrap_node("calculate_score", calculate_score_node, reporter))
    builder.add_node(
        "draft_evaluation",
        _wrap_node("draft_evaluation", build_draft_evaluation_node(settings), reporter),
    )
    builder.add_node(
        "guardrail_check",
        _wrap_node("guardrail_check", build_guardrail_check_node(settings), reporter),
    )

    builder.add_edge(START, "extract_cv_skills")
    builder.add_edge(START, "load_roadmap_data")
    builder.add_edge("extract_cv_skills", "calculate_score")
    builder.add_edge("load_roadmap_data", "calculate_score")
    builder.add_edge("calculate_score", "draft_evaluation")
    builder.add_edge("draft_evaluation", "guardrail_check")
    builder.add_conditional_edges(
        "guardrail_check",
        route_after_guardrail,
        {
            "pass": END,
            "retry": "draft_evaluation",
            "fail": END,
        },
    )

    return builder.compile()
