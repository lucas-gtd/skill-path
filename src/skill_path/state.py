from __future__ import annotations

from typing import Any, TypedDict


class ExtractedExperience(TypedDict):
    title: str
    company: str
    summary: str


class NotionEvaluation(TypedDict):
    notion: str
    expected_technologies: list[str]
    matched_skills: list[str]
    matched_skills_explicit: list[str]
    matched_skills_inferred: list[str]
    inferred_skill_paths: dict[str, list[str]]
    matched: bool
    matched_by_inference: bool


class EvaluationState(TypedDict, total=False):
    cv_path: str
    roadmap_path: str
    cv_text: str
    cv_chunks: list[str]
    roadmap_json: dict[str, Any]
    extracted_skills: list[str]
    inferred_skills: list[str]
    inferred_skill_paths: dict[str, list[str]]
    extracted_experiences: list[ExtractedExperience]
    matched_notions: list[str]
    missing_notions: list[str]
    match_results: list[NotionEvaluation]
    score: int
    draft_report: str
    guardrail_feedback: str
    guardrail_status: str
    guardrail_attempts: int
    max_guardrail_revisions: int
