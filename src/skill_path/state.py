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
    matched: bool


class EvaluationState(TypedDict, total=False):
    cv_path: str
    roadmap_path: str
    cv_text: str
    cv_chunks: list[str]
    roadmap_json: dict[str, Any]
    extracted_skills: list[str]
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
