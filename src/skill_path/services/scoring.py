from __future__ import annotations

import re
from collections import deque
from dataclasses import dataclass, field

from skill_path.schemas import RoadmapModel

SPACE_PATTERN = re.compile(r"[^a-z0-9+#]+")


@dataclass(frozen=True, slots=True)
class ScoringResult:
    explicit_skills: list[str]
    inferred_skills: list[str]
    inferred_skill_paths: dict[str, list[str]]
    matched_notions: list[str]
    missing_notions: list[str]
    score: int
    match_results: list[dict[str, object]]


def normalize_skill_name(value: str) -> str:
    collapsed = SPACE_PATTERN.sub(" ", value.casefold()).strip()
    return " ".join(collapsed.split())


def _phrased_contains(longer: str, shorter: str) -> bool:
    return f" {shorter} " in f" {longer} "


def skill_matches(expected: str, candidate: str) -> bool:
    expected_norm = normalize_skill_name(expected)
    candidate_norm = normalize_skill_name(candidate)
    if not expected_norm or not candidate_norm:
        return False
    if expected_norm == candidate_norm:
        return True

    if len(expected_norm) < 3 or len(candidate_norm) < 3:
        return False

    if len(candidate_norm) > len(expected_norm):
        return _phrased_contains(candidate_norm, expected_norm)
    return _phrased_contains(expected_norm, candidate_norm)


def deduplicate_strings(values: list[str]) -> list[str]:
    seen: set[str] = set()
    unique_values: list[str] = []
    for value in values:
        cleaned = value.strip()
        normalized = normalize_skill_name(cleaned)
        if cleaned and normalized not in seen:
            seen.add(normalized)
            unique_values.append(cleaned)
    return unique_values


@dataclass(slots=True)
class ExpandedSkills:
    explicit_skills: list[str]
    inferred_skills: list[str]
    inferred_skill_paths: dict[str, list[str]] = field(default_factory=dict)


def expand_skills(extracted_skills: list[str], roadmap: RoadmapModel) -> ExpandedSkills:
    explicit_skills = deduplicate_strings(extracted_skills)
    explicit_by_norm = {normalize_skill_name(skill): skill for skill in explicit_skills}
    all_known_by_norm = dict(explicit_by_norm)
    path_by_norm = {norm: [skill] for norm, skill in explicit_by_norm.items()}

    implication_items = [
        (trigger, [target for target in targets if target.strip()])
        for trigger, targets in roadmap.skill_implications.items()
        if trigger.strip()
    ]

    queue: deque[str] = deque(explicit_by_norm)
    while queue:
        current_norm = queue.popleft()
        current_skill = all_known_by_norm[current_norm]

        for trigger, targets in implication_items:
            if not skill_matches(trigger, current_skill):
                continue

            for target in targets:
                target_norm = normalize_skill_name(target)
                if not target_norm:
                    continue
                if target_norm in all_known_by_norm:
                    continue

                all_known_by_norm[target_norm] = target.strip()
                path_by_norm[target_norm] = [*path_by_norm[current_norm], target.strip()]
                queue.append(target_norm)

    inferred_skills = [
        all_known_by_norm[norm]
        for norm in all_known_by_norm
        if norm not in explicit_by_norm
    ]
    inferred_skill_paths = {
        all_known_by_norm[norm]: path_by_norm[norm]
        for norm in all_known_by_norm
        if norm not in explicit_by_norm
    }
    return ExpandedSkills(
        explicit_skills=explicit_skills,
        inferred_skills=inferred_skills,
        inferred_skill_paths=inferred_skill_paths,
    )


def calculate_score(extracted_skills: list[str], roadmap: RoadmapModel) -> ScoringResult:
    expanded = expand_skills(extracted_skills, roadmap)
    explicit_skill_set = set(expanded.explicit_skills)
    available_skills = [*expanded.explicit_skills, *expanded.inferred_skills]
    matched_notions: list[str] = []
    missing_notions: list[str] = []
    match_results: list[dict[str, object]] = []

    for notion in roadmap.notions:
        matched_skills_explicit = sorted(
            {
                skill
                for skill in available_skills
                for expected in notion.technologies
                if skill_matches(expected, skill)
                if skill in explicit_skill_set
            }
        )
        matched_skills_inferred = sorted(
            {
                skill
                for skill in available_skills
                for expected in notion.technologies
                if skill_matches(expected, skill)
                if skill not in explicit_skill_set
            }
        )
        matched = bool(matched_skills_explicit or matched_skills_inferred)
        result = {
            "notion": notion.name,
            "expected_technologies": notion.technologies,
            "matched_skills": [*matched_skills_explicit, *matched_skills_inferred],
            "matched_skills_explicit": matched_skills_explicit,
            "matched_skills_inferred": matched_skills_inferred,
            "inferred_skill_paths": {
                skill: expanded.inferred_skill_paths[skill]
                for skill in matched_skills_inferred
            },
            "matched": matched,
            "matched_by_inference": bool(matched_skills_inferred),
        }
        match_results.append(result)
        if matched:
            matched_notions.append(notion.name)
        else:
            missing_notions.append(notion.name)

    total_notions = len(roadmap.notions)
    score = int(round((len(matched_notions) / total_notions) * 100)) if total_notions else 0
    return ScoringResult(
        explicit_skills=expanded.explicit_skills,
        inferred_skills=expanded.inferred_skills,
        inferred_skill_paths=expanded.inferred_skill_paths,
        matched_notions=matched_notions,
        missing_notions=missing_notions,
        score=score,
        match_results=match_results,
    )
