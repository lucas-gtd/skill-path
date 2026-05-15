from __future__ import annotations

import re
from dataclasses import dataclass

from skill_path.schemas import RoadmapModel

SPACE_PATTERN = re.compile(r"[^a-z0-9+#.]+")


@dataclass(frozen=True, slots=True)
class ScoringResult:
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


def calculate_score(extracted_skills: list[str], roadmap: RoadmapModel) -> ScoringResult:
    unique_skills = deduplicate_strings(extracted_skills)
    matched_notions: list[str] = []
    missing_notions: list[str] = []
    match_results: list[dict[str, object]] = []

    for notion in roadmap.notions:
        matched_skills = sorted(
            {
                skill
                for skill in unique_skills
                for expected in notion.technologies
                if skill_matches(expected, skill)
            }
        )
        matched = bool(matched_skills)
        result = {
            "notion": notion.name,
            "expected_technologies": notion.technologies,
            "matched_skills": matched_skills,
            "matched": matched,
        }
        match_results.append(result)
        if matched:
            matched_notions.append(notion.name)
        else:
            missing_notions.append(notion.name)

    total_notions = len(roadmap.notions)
    score = int(round((len(matched_notions) / total_notions) * 100)) if total_notions else 0
    return ScoringResult(
        matched_notions=matched_notions,
        missing_notions=missing_notions,
        score=score,
        match_results=match_results,
    )
