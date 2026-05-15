from __future__ import annotations

from langchain_openai import ChatOpenAI

from skill_path.config import Settings


def build_chat_model(settings: Settings, *, temperature: float) -> ChatOpenAI:
    return ChatOpenAI(
        api_key=settings.openrouter_api_key,
        model=settings.openrouter_model,
        base_url=settings.openrouter_base_url,
        temperature=temperature,
        max_retries=2,
        default_headers={
            "HTTP-Referer": settings.openrouter_site_url,
            "X-Title": settings.openrouter_app_name,
        },
    )


def message_text(content: object) -> str:
    if isinstance(content, str):
        return content.strip()
    if isinstance(content, list):
        parts = [item.get("text", "") for item in content if isinstance(item, dict)]
        return "\n".join(part for part in parts if part).strip()
    return str(content).strip()
