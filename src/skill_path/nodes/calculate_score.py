from __future__ import annotations

from skill_path.services.roadmap_loader import roadmap_from_dict
from skill_path.services.scoring import calculate_score
from skill_path.state import EvaluationState


def calculate_score_node(state: EvaluationState) -> dict[str, object]:
    roadmap = roadmap_from_dict(state["roadmap_json"])
    result = calculate_score(state.get("extracted_skills", []), roadmap)
    return {
        "matched_notions": result.matched_notions,
        "missing_notions": result.missing_notions,
        "score": result.score,
        "match_results": result.match_results,
    }
