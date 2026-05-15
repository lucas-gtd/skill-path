from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from skill_path.schemas import RoadmapModel


def load_roadmap(path: str | Path) -> RoadmapModel:
    roadmap_path = Path(path)
    if not roadmap_path.exists():
        raise FileNotFoundError(f"Roadmap JSON not found: {roadmap_path}")
    with roadmap_path.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return RoadmapModel.model_validate(payload)


def roadmap_to_dict(roadmap: RoadmapModel) -> dict[str, Any]:
    return roadmap.model_dump(mode="json")


def roadmap_from_dict(payload: dict[str, Any]) -> RoadmapModel:
    return RoadmapModel.model_validate(payload)
