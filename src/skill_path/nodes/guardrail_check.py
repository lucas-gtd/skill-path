from __future__ import annotations

from collections.abc import Callable

from skill_path.config import Settings
from skill_path.prompts import build_guardrail_prompt, dump_prompt_payload
from skill_path.schemas import GuardrailResultModel
from skill_path.services.llm_factory import build_chat_model
from skill_path.state import EvaluationState


def build_guardrail_check_node(settings: Settings) -> Callable[[EvaluationState], dict[str, object]]:
    llm = build_chat_model(settings, temperature=settings.guardrail_temperature)
    structured_llm = llm.with_structured_output(GuardrailResultModel)
    prompt = build_guardrail_prompt()
    chain = prompt | structured_llm

    def guardrail_check(state: EvaluationState) -> dict[str, object]:
        attempts = state.get("guardrail_attempts", 0) + 1
        verdict = chain.invoke(
            {
                "ground_truth": dump_prompt_payload(
                    {
                        "score": state["score"],
                        "matched_notions": state["matched_notions"],
                        "missing_notions": state["missing_notions"],
                        "match_results": state["match_results"],
                        "extracted_skills": state["extracted_skills"],
                        "extracted_experiences": state.get("extracted_experiences", []),
                    }
                ),
                "draft_report": state["draft_report"],
            }
        )

        if verdict.status == "PASS":
            return {
                "guardrail_status": "PASS",
                "guardrail_feedback": "",
                "guardrail_attempts": attempts,
            }

        if attempts < state.get("max_guardrail_revisions", settings.guardrail_max_revisions):
            status = "RETRY"
        else:
            status = "FAIL"

        return {
            "guardrail_status": status,
            "guardrail_feedback": verdict.feedback.strip() or "Le rapport doit etre corrige sans inventer de competences.",
            "guardrail_attempts": attempts,
        }

    return guardrail_check
