from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class RoadmapNotionModel(BaseModel):
    name: str
    description: str | None = None
    technologies: list[str] = Field(default_factory=list, min_length=1)


class RoadmapModel(BaseModel):
    title: str
    summary: str | None = None
    notions: list[RoadmapNotionModel] = Field(default_factory=list, min_length=1)


class ExtractedExperienceModel(BaseModel):
    title: str
    company: str | None = None
    summary: str


class CVExtractionResultModel(BaseModel):
    skills: list[str] = Field(default_factory=list)
    experiences: list[ExtractedExperienceModel] = Field(default_factory=list)


class GuardrailResultModel(BaseModel):
    status: Literal["PASS", "FAIL"]
    feedback: str = ""


class EvaluationResultModel(BaseModel):
    score: int
    matched_notions: list[str]
    missing_notions: list[str]
    extracted_skills: list[str]
    extracted_experiences: list[ExtractedExperienceModel]
    draft_report: str
    guardrail_status: str
    guardrail_feedback: str = ""
