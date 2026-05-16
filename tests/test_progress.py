from pathlib import Path

from skill_path.config import Settings
from skill_path.graph import _wrap_node
from skill_path.main import build_initial_state
from skill_path.services.progress import ConsoleProgressReporter


class PreparationReporterStub:
    def __init__(self) -> None:
        self.events: list[object] = []

    def on_cv_load_start(self) -> None:
        self.events.append("load")

    def on_cv_chunking_start(self) -> None:
        self.events.append("chunk")

    def on_cv_ready(self, chunk_count: int) -> None:
        self.events.append(("ready", chunk_count))

    def on_node_start(self, node_name: str, state: dict[str, object]) -> None:
        self.events.append(("start", node_name, state))

    def on_node_end(self, node_name: str, update: dict[str, object]) -> None:
        self.events.append(("end", node_name, update))


def test_build_initial_state_reports_preparation_steps(monkeypatch) -> None:
    reporter = PreparationReporterStub()

    state = build_initial_state(
        Path("candidate.pdf"),
        Path("roadmap.json"),
        Settings(openrouter_api_key="key", openrouter_model="model"),
        reporter=reporter,
        load_pdf_text_fn=lambda path: "cv text",
        split_cv_text_fn=lambda text, chunk_size, chunk_overlap: ["a", "b"],
    )

    assert reporter.events == ["load", "chunk", ("ready", 2)]
    assert state["cv_chunks"] == ["a", "b"]


def test_wrap_node_reports_start_and_end() -> None:
    reporter = PreparationReporterStub()

    def calculate_score(state: dict[str, object]) -> dict[str, object]:
        assert state["input"] == "ok"
        return {"score": 42}

    wrapped_node = _wrap_node("calculate_score", calculate_score, reporter)

    assert wrapped_node({"input": "ok"}) == {"score": 42}
    assert reporter.events == [
        ("start", "calculate_score", {"input": "ok"}),
        ("end", "calculate_score", {"score": 42}),
    ]


def test_console_progress_reporter_tracks_guardrail_revisions() -> None:
    messages: list[str] = []
    reporter = ConsoleProgressReporter(emit=messages.append, max_guardrail_revisions=3)

    reporter.on_node_start("draft_evaluation", {})
    reporter.on_node_end("draft_evaluation", {"draft_report": "report"})
    reporter.on_node_start("guardrail_check", {})
    reporter.on_node_end(
        "guardrail_check",
        {"guardrail_status": "RETRY", "guardrail_attempts": 1},
    )
    reporter.on_node_start("draft_evaluation", {})

    assert messages == [
        "Redaction du rapport...",
        "Rapport redige.",
        "Verification finale du rapport...",
        "Verification finale: corrections demandees (tentative 1/3).",
        "Revision du rapport...",
    ]