from __future__ import annotations

from skill_path.services.roadmap_loader import roadmap_from_dict
from skill_path.services.scoring import calculate_score
from skill_path.state import EvaluationState


def calculate_score_node(state: EvaluationState) -> dict[str, object]:
    roadmap = roadmap_from_dict(state["roadmap_json"])
    experience_implied_skills = state.get("experience_implied_skills", [])
    all_seeds = [*state.get("extracted_skills", []), *experience_implied_skills]
    result = calculate_score(all_seeds, roadmap)
    # Restore explicit_skills to only the originally extracted ones, not the implied seeds
    explicit_only = [s for s in result.explicit_skills if s in set(state.get("extracted_skills", []))]
    return {
        "extracted_skills": explicit_only,
        "experience_implied_skills": experience_implied_skills,
        "inferred_skills": result.inferred_skills,
        "inferred_skill_paths": result.inferred_skill_paths,
        "matched_notions": result.matched_notions,
        "missing_notions": result.missing_notions,
        "score": result.score,
        "match_results": result.match_results,
    }
