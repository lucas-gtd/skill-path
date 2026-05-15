from skill_path.services.scoring import calculate_score, deduplicate_strings, expand_skills, skill_matches
from skill_path.schemas import RoadmapModel


def test_skill_matches_handles_exact_and_phrase_matches() -> None:
    assert skill_matches("Django", "Django")
    assert skill_matches("Django", "Django REST Framework")
    assert skill_matches("Node.js", "Node")
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


def test_expand_skills_adds_transitive_inferred_skills() -> None:
    roadmap = RoadmapModel.model_validate(
        {
            "title": "Frontend",
            "skill_implications": {
                "Angular": ["TypeScript", "HTML", "CSS"],
                "TypeScript": ["JavaScript"],
            },
            "notions": [
                {"name": "Bases du Web", "technologies": ["HTML", "CSS", "JavaScript"]},
            ],
        }
    )

    expanded = expand_skills(["Angular"], roadmap)

    assert expanded.explicit_skills == ["Angular"]
    assert expanded.inferred_skills == ["TypeScript", "HTML", "CSS", "JavaScript"]
    assert expanded.inferred_skill_paths["JavaScript"] == ["Angular", "TypeScript", "JavaScript"]


def test_calculate_score_uses_inferred_skills_with_provenance() -> None:
    roadmap = RoadmapModel.model_validate(
        {
            "title": "Frontend",
            "skill_implications": {
                "Node.js": ["JavaScript"],
                "Angular": ["TypeScript", "HTML", "CSS"],
                "TypeScript": ["JavaScript"],
            },
            "notions": [
                {"name": "Bases du Web", "technologies": ["HTML", "CSS", "JavaScript"]},
                {"name": "Backend", "technologies": ["Node.js"]},
            ],
        }
    )

    result = calculate_score(["Node", "Angular"], roadmap)

    assert result.explicit_skills == ["Node", "Angular"]
    assert result.inferred_skills == ["JavaScript", "TypeScript", "HTML", "CSS"]
    assert result.matched_notions == ["Bases du Web", "Backend"]
    assert result.score == 100
    assert result.match_results[0]["matched_skills_explicit"] == []
    assert result.match_results[0]["matched_skills_inferred"] == ["CSS", "HTML", "JavaScript"]
    assert result.match_results[0]["matched_by_inference"] is True
    assert result.match_results[0]["inferred_skill_paths"]["JavaScript"] == ["Node", "JavaScript"]


def test_expand_skills_handles_cycles_without_looping() -> None:
    roadmap = RoadmapModel.model_validate(
        {
            "title": "Cyclic",
            "skill_implications": {
                "A": ["B"],
                "B": ["C"],
                "C": ["A"],
            },
            "notions": [
                {"name": "Loop", "technologies": ["C"]},
            ],
        }
    )

    expanded = expand_skills(["A"], roadmap)

    assert expanded.explicit_skills == ["A"]
    assert expanded.inferred_skills == ["B", "C"]
