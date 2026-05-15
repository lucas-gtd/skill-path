from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

DEFAULT_BASE_URL = "https://openrouter.ai/api/v1"
DEFAULT_SITE_URL = "https://github.com/lucas-gtd/skill-path"
DEFAULT_APP_NAME = "skill-path"


@dataclass(frozen=True, slots=True)
class Settings:
    openrouter_api_key: str
    openrouter_model: str
    openrouter_base_url: str = DEFAULT_BASE_URL
    openrouter_site_url: str = DEFAULT_SITE_URL
    openrouter_app_name: str = DEFAULT_APP_NAME
    rag_chunk_size: int = 900
    rag_chunk_overlap: int = 120
    rag_top_k: int = 6
    guardrail_max_revisions: int = 3
    extract_temperature: float = 0.0
    report_temperature: float = 0.2
    guardrail_temperature: float = 0.0

    @classmethod
    def from_env(cls, env_file: Path | None = None) -> "Settings":
        if env_file is not None:
            load_dotenv(env_file)
        else:
            load_dotenv()

        api_key = os.getenv("OPENROUTER_API_KEY", "").strip()
        model = os.getenv("OPENROUTER_MODEL", "").strip()
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY is required.")
        if not model:
            raise ValueError("OPENROUTER_MODEL is required.")

        return cls(
            openrouter_api_key=api_key,
            openrouter_model=model,
            openrouter_base_url=os.getenv("OPENROUTER_BASE_URL", DEFAULT_BASE_URL).strip() or DEFAULT_BASE_URL,
            openrouter_site_url=os.getenv("OPENROUTER_SITE_URL", DEFAULT_SITE_URL).strip() or DEFAULT_SITE_URL,
            openrouter_app_name=os.getenv("OPENROUTER_APP_NAME", DEFAULT_APP_NAME).strip() or DEFAULT_APP_NAME,
            rag_chunk_size=int(os.getenv("SKILL_PATH_RAG_CHUNK_SIZE", "900")),
            rag_chunk_overlap=int(os.getenv("SKILL_PATH_RAG_CHUNK_OVERLAP", "120")),
            rag_top_k=int(os.getenv("SKILL_PATH_RAG_TOP_K", "6")),
            guardrail_max_revisions=int(os.getenv("SKILL_PATH_GUARDRAIL_MAX_REVISIONS", "3")),
        )
