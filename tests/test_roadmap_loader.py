from pathlib import Path

from skill_path.services.roadmap_loader import load_roadmap


def test_load_roadmap_validates_json(tmp_path: Path) -> None:
    roadmap_path = tmp_path / "roadmap.json"
    roadmap_path.write_text(
        """
        {
          "title": "Backend Python",
          "skill_implications": {
            "FastAPI": ["Python"]
          },
          "notions": [
            {
              "name": "API Web",
              "technologies": ["FastAPI", "Django"]
            }
          ]
        }
        """,
        encoding="utf-8",
    )

    roadmap = load_roadmap(roadmap_path)

    assert roadmap.title == "Backend Python"
    assert roadmap.skill_implications == {"FastAPI": ["Python"]}
    assert roadmap.notions[0].name == "API Web"


def test_all_repository_roadmaps_are_valid() -> None:
    roadmap_dir = Path("data") / "roadmaps"

    loaded_titles = [load_roadmap(path).title for path in roadmap_dir.glob("*.json")]

    assert sorted(loaded_titles) == ["Backend Python", "Data Engineer", "Full Stack"]
