from __future__ import annotations

from collections.abc import Callable

from skill_path.config import Settings
from skill_path.prompts import build_extraction_prompt
from skill_path.schemas import CVExtractionResultModel
from skill_path.services.llm_factory import build_chat_model
from skill_path.services.retriever import retrieve_context
from skill_path.services.scoring import deduplicate_strings
from skill_path.state import EvaluationState


def build_extract_cv_skills_node(settings: Settings) -> Callable[[EvaluationState], dict[str, object]]:
    llm = build_chat_model(settings, temperature=settings.extract_temperature)
    structured_llm = llm.with_structured_output(CVExtractionResultModel)
    prompt = build_extraction_prompt()
    chain = prompt | structured_llm

    def extract_cv_skills(state: EvaluationState) -> dict[str, object]:
        retrieved_context = retrieve_context(
            chunks=state["cv_chunks"],
            queries=[
                "Competences techniques, frameworks, langages, outils, bases de donnees.",
                "Experiences professionnelles, roles, missions, projets, stack technique.",
            ],
            top_k=settings.rag_top_k,
        )
        result = chain.invoke(
            {
                "cv_text": state["cv_text"],
                "retrieved_context": retrieved_context,
            }
        )
        return {
            "extracted_skills": deduplicate_strings(result.skills),
            "extracted_experiences": [
                {
                    "title": experience.title.strip(),
                    "company": (experience.company or "").strip(),
                    "summary": experience.summary.strip(),
                }
                for experience in result.experiences
                if experience.title.strip() and experience.summary.strip()
            ],
        }

    return extract_cv_skills
