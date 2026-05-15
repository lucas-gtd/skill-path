from pathlib import Path

from skill_path.services.roadmap_loader import load_roadmap


def test_load_roadmap_validates_json(tmp_path: Path) -> None:
    roadmap_path = tmp_path / "roadmap.json"
    roadmap_path.write_text(
        """
        {
          "title": "Backend Python",
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
    assert roadmap.notions[0].name == "API Web"
