from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from skill_path.config import Settings
from skill_path.schemas import EvaluationResultModel, ExtractedExperienceModel


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Evaluate a CV PDF against a roadmap JSON using LangChain, OpenRouter and LangGraph."
    )
    parser.add_argument("cv_pdf", type=Path, help="Path to the candidate CV PDF.")
    parser.add_argument("roadmap_json", type=Path, help="Path to the roadmap JSON file.")
    parser.add_argument(
        "--env-file",
        type=Path,
        default=None,
        help="Optional .env file to load before reading environment variables.",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=None,
        help="Optional path where the generated markdown report will be written.",
    )
    parser.add_argument(
        "--state-output",
        type=Path,
        default=None,
        help="Optional path where the final state snapshot will be written as JSON.",
    )
    return parser.parse_args()


def build_initial_state(cv_path: Path, roadmap_path: Path, settings: Settings) -> dict[str, Any]:
    from skill_path.services.pdf_loader import load_pdf_text
    from skill_path.services.retriever import split_cv_text

    cv_text = load_pdf_text(cv_path)
    cv_chunks = split_cv_text(
        cv_text,
        chunk_size=settings.rag_chunk_size,
        chunk_overlap=settings.rag_chunk_overlap,
    )
    return {
        "cv_path": str(cv_path),
        "roadmap_path": str(roadmap_path),
        "cv_text": cv_text,
        "cv_chunks": cv_chunks,
        "roadmap_json": {},
        "extracted_skills": [],
        "extracted_experiences": [],
        "matched_notions": [],
        "missing_notions": [],
        "match_results": [],
        "score": 0,
        "draft_report": "",
        "guardrail_feedback": "",
        "guardrail_status": "PENDING",
        "guardrail_attempts": 0,
        "max_guardrail_revisions": settings.guardrail_max_revisions,
    }


def export_state(final_state: dict[str, Any], output_path: Path) -> None:
    payload = EvaluationResultModel(
        score=final_state["score"],
        matched_notions=final_state["matched_notions"],
        missing_notions=final_state["missing_notions"],
        extracted_skills=final_state["extracted_skills"],
        extracted_experiences=[
            ExtractedExperienceModel.model_validate(item) for item in final_state.get("extracted_experiences", [])
        ],
        draft_report=final_state["draft_report"],
        guardrail_status=final_state["guardrail_status"],
        guardrail_feedback=final_state.get("guardrail_feedback", ""),
    ).model_dump(mode="json")
    output_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False), encoding="utf-8")


def main() -> int:
    args = parse_args()
    from skill_path.graph import build_graph

    settings = Settings.from_env(args.env_file)
    graph = build_graph(settings)

    final_state = graph.invoke(
        build_initial_state(args.cv_pdf.resolve(), args.roadmap_json.resolve(), settings),
        config={"recursion_limit": 25},
    )
    report = final_state["draft_report"]

    if args.output is not None:
        args.output.write_text(report, encoding="utf-8")
    if args.state_output is not None:
        export_state(final_state, args.state_output)

    print(report)

    if final_state.get("guardrail_status") != "PASS":
        feedback = final_state.get("guardrail_feedback", "Unknown guardrail failure.")
        raise SystemExit(f"Guardrail failed after {final_state.get('guardrail_attempts', 0)} attempt(s): {feedback}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
