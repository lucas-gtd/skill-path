from __future__ import annotations

from collections.abc import Callable

from skill_path.config import Settings
from skill_path.prompts import build_draft_prompt, dump_prompt_payload
from skill_path.services.llm_factory import build_chat_model, message_text
from skill_path.state import EvaluationState


def build_draft_evaluation_node(settings: Settings) -> Callable[[EvaluationState], dict[str, object]]:
    llm = build_chat_model(settings, temperature=settings.report_temperature)
    prompt = build_draft_prompt()
    chain = prompt | llm

    def draft_evaluation(state: EvaluationState) -> dict[str, object]:
        payload = {
            "score": state["score"],
            "matched_notions": state["matched_notions"],
            "missing_notions": state["missing_notions"],
            "match_results": state["match_results"],
            "extracted_skills": state["extracted_skills"],
            "inferred_skills": state.get("inferred_skills", []),
            "inferred_skill_paths": state.get("inferred_skill_paths", {}),
            "extracted_experiences": state.get("extracted_experiences", []),
        }
        response = chain.invoke(
            {
                "evaluation_payload": dump_prompt_payload(payload),
                "guardrail_feedback": state.get("guardrail_feedback", "") or "Aucun feedback precedent.",
            }
        )
        return {"draft_report": message_text(response.content)}

    return draft_evaluation
