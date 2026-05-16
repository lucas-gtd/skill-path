from __future__ import annotations

import sys
from collections.abc import Callable, Mapping
from typing import Protocol


class ProgressReporter(Protocol):
    def on_cv_load_start(self) -> None: ...

    def on_cv_chunking_start(self) -> None: ...

    def on_cv_ready(self, chunk_count: int) -> None: ...

    def on_node_start(self, node_name: str, state: Mapping[str, object]) -> None: ...

    def on_node_end(self, node_name: str, update: Mapping[str, object]) -> None: ...


class ConsoleProgressReporter:
    def __init__(
        self,
        emit: Callable[[str], None] | None = None,
        *,
        max_guardrail_revisions: int = 0,
    ) -> None:
        self._emit = emit or self._default_emit
        self._max_guardrail_revisions = max_guardrail_revisions
        self._pending_revision = False

    def _default_emit(self, message: str) -> None:
        print(f"[skill-path] {message}", file=sys.stderr, flush=True)

    def on_cv_load_start(self) -> None:
        self._emit("Chargement du CV PDF...")

    def on_cv_chunking_start(self) -> None:
        self._emit("Decoupage du CV pour l'analyse...")

    def on_cv_ready(self, chunk_count: int) -> None:
        suffix = "s" if chunk_count != 1 else ""
        self._emit(f"CV prepare: {chunk_count} segment{suffix} pret{suffix} pour l'analyse.")

    def on_node_start(self, node_name: str, state: Mapping[str, object]) -> None:
        del state
        message = {
            "extract_cv_skills": "Extraction des competences et experiences du CV...",
            "load_roadmap_data": "Chargement de la roadmap cible...",
            "calculate_score": "Calcul du score de correspondance...",
            "guardrail_check": "Verification finale du rapport...",
        }.get(node_name)

        if node_name == "draft_evaluation":
            message = "Revision du rapport..." if self._pending_revision else "Redaction du rapport..."
            self._pending_revision = False

        if message is not None:
            self._emit(message)

    def on_node_end(self, node_name: str, update: Mapping[str, object]) -> None:
        if node_name == "extract_cv_skills":
            skill_count = _count_list_items(update.get("extracted_skills"))
            experience_count = _count_list_items(update.get("extracted_experiences"))
            if skill_count is not None and experience_count is not None:
                self._emit(
                    "Extraction terminee: "
                    f"{skill_count} competence(s) et {experience_count} experience(s) retenue(s)."
                )
            else:
                self._emit("Extraction terminee.")
            return

        if node_name == "load_roadmap_data":
            self._emit("Roadmap chargee.")
            return

        if node_name == "calculate_score":
            score = update.get("score")
            if isinstance(score, int):
                self._emit(f"Scoring termine: couverture estimee a {score}%.")
            else:
                self._emit("Scoring termine.")
            return

        if node_name == "draft_evaluation":
            self._emit("Rapport redige.")
            return

        if node_name != "guardrail_check":
            return

        status = update.get("guardrail_status")
        attempts = update.get("guardrail_attempts")
        attempt_label = attempts if isinstance(attempts, int) else "?"

        if status == "PASS":
            self._emit(f"Verification finale validee en {attempt_label} tentative(s).")
            return

        if status == "RETRY":
            self._pending_revision = True
            total = self._max_guardrail_revisions or "?"
            self._emit(f"Verification finale: corrections demandees (tentative {attempt_label}/{total}).")
            return

        self._emit(f"Verification finale en echec apres {attempt_label} tentative(s).")


def _count_list_items(value: object) -> int | None:
    if not isinstance(value, list):
        return None
    return len(value)