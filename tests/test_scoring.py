from skill_path.services.scoring import calculate_score, deduplicate_strings, skill_matches
from skill_path.schemas import RoadmapModel


def test_skill_matches_handles_exact_and_phrase_matches() -> None:
    assert skill_matches("Django", "Django")
    assert skill_matches("Django", "Django REST Framework")
    assert not skill_matches("C", "C++")


def test_deduplicate_strings_preserves_first_seen_value() -> None:
    assert deduplicate_strings(["Python", "python", " FastAPI "]) == ["Python", "FastAPI"]


def test_calculate_score_uses_single_matching_framework_per_notion() -> None:
    roadmap = RoadmapModel.model_validate(
        {
            "title": "Backend",
            "notions": [
                {"name": "API Web", "technologies": ["FastAPI", "Django", "Flask"]},
                {"name": "Database", "technologies": ["PostgreSQL", "MySQL"]},
                {"name": "Frontend", "technologies": ["React", "Vue"]},
            ],
        }
    )

    result = calculate_score(["Django REST Framework", "PostgreSQL"], roadmap)

    assert result.matched_notions == ["API Web", "Database"]
    assert result.missing_notions == ["Frontend"]
    assert result.score == 67
