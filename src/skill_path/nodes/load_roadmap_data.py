from __future__ import annotations

from skill_path.services.roadmap_loader import load_roadmap, roadmap_to_dict
from skill_path.state import EvaluationState


def load_roadmap_data(state: EvaluationState) -> dict[str, object]:
    roadmap = load_roadmap(state["roadmap_path"])
    return {"roadmap_json": roadmap_to_dict(roadmap)}
