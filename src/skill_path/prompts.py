from __future__ import annotations

import json
from typing import Any

from langchain_core.prompts import ChatPromptTemplate


def build_extraction_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Tu es un analyste de CV. Tu travailles uniquement a partir des informations "
                    "fournies. Extrais une liste normalisee de competences techniques explicites et "
                    "des experiences professionnelles structurees. N'invente jamais de technologie."
                ),
            ),
            (
                "human",
                (
                    "Texte brut du CV:\n{cv_text}\n\n"
                    "Contexte RAG cible:\n{retrieved_context}\n\n"
                    "Retourne uniquement les competences techniques explicites et les experiences "
                    "professionnelles les plus pertinentes."
                ),
            ),
        ]
    )


def build_draft_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Tu rediges un compte rendu d'evaluation de CV en francais. "
                    "Tu dois rester strictement coherent avec les donnees fournies. "
                    "Tu ne peux citer que des competences presentes dans extracted_skills, inferred_skills, "
                    "matched_notions, missing_notions, match_results ou extracted_experiences. "
                    "Le score est la source de verite. "
                    "Les competences inferees doivent toujours etre presentees comme des deductions de la roadmap, "
                    "jamais comme des mentions explicites du CV."
                ),
            ),
            (
                "human",
                (
                    "Donnees d'evaluation:\n{evaluation_payload}\n\n"
                    "Consignes:\n"
                    "- Ecris en markdown.\n"
                    "- Donne un bilan clair, constructif et concis.\n"
                    "- Indique le score numerique.\n"
                    "- Separe les notions validees et les notions a travailler.\n"
                    "- Utilise les experiences extraites uniquement comme preuves contextuelles.\n"
                    "- Si une notion est validee grace a une competence inferee, indique-le explicitement.\n"
                    "- Si un feedback guardrail est present, corrige explicitement les problemes.\n\n"
                    "Feedback guardrail precedent:\n{guardrail_feedback}"
                ),
            ),
        ]
    )


def build_guardrail_prompt() -> ChatPromptTemplate:
    return ChatPromptTemplate.from_messages(
        [
            (
                "system",
                (
                    "Tu es le superviseur final. Verifie si le rapport contredit les donnees d'entree "
                    "ou invente des competences/notions. Si tout est correct, reponds PASS. "
                    "Sinon, reponds FAIL avec une critique actionnable."
                ),
            ),
            (
                "human",
                (
                    "Verite terrain:\n{ground_truth}\n\n"
                    "Rapport a verifier:\n{draft_report}\n\n"
                    "Critere d'echec:\n"
                    "- score ou conclusion incoherents\n"
                    "- competence ou notion inventee\n"
                    "- notion marquee comme acquise alors qu'elle est absente de matched_notions\n"
                    "- competence inferee presentee comme si elle etait explicitement ecrite dans le CV\n"
                    "- omission flagrante d'une incoherence deja signalee"
                ),
            ),
        ]
    )


def dump_prompt_payload(payload: dict[str, Any]) -> str:
    return json.dumps(payload, indent=2, ensure_ascii=False)
