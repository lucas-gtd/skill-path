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
                    "fournies. Tu dois extraire deux listes distinctes :\n"
                    "1. skills : competences techniques explicitement nommees dans le CV "
                    "(langages, frameworks, outils, plateformes). N'invente jamais une technologie absente du texte.\n"
                    "2. experience_implied_skills : competences techniques fortement impliquees par les "
                    "descriptions de postes et de projets, meme si elles ne sont pas nommees explicitement. "
                    "Par exemple, un titre 'developpeur full-stack' implique du backend (Node.js ou equivalent), "
                    "un projet SPA Angular implique RESTful APIs, un poste mentionnant CI/CD implique GitHub Actions "
                    "ou equivalent, Docker Compose implique Docker, SQL/Oracle implique une connaissance des bases "
                    "de donnees relationnelles. Reste raisonnable : n'infere que ce qui est "
                    "tres probablement maitrise compte tenu du contexte.\n"
                    "Extrais aussi les experiences professionnelles structurees."
                ),
            ),
            (
                "human",
                (
                    "Texte brut du CV:\n{cv_text}\n\n"
                    "Contexte RAG cible:\n{retrieved_context}\n\n"
                    "Retourne les competences explicites (skills), les competences inferees des experiences "
                    "(experience_implied_skills) et les experiences professionnelles les plus pertinentes."
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
                    "Tu ne peux citer que des competences presentes dans extracted_skills, "
                    "experience_implied_skills, inferred_skills, "
                    "matched_notions, missing_notions, match_results ou extracted_experiences. "
                    "Le score est la source de verite. "
                    "Distingue trois niveaux d'origine pour les competences :\n"
                    "- explicite : presente dans extracted_skills (citee dans le CV)\n"
                    "- inferred from experience : presente dans experience_implied_skills (inferee des descriptions de postes)\n"
                    "- inferred from roadmap : presente dans inferred_skills (deduite par les implications de la roadmap)\n"
                    "Ne presente jamais une competence inferee comme si elle etait explicitement ecrite dans le CV."
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
                    "- Si une notion est validee grace a une competence de experience_implied_skills, "
                    "indique 'inférée des expériences'.\n"
                    "- Si une notion est validee grace a une competence de inferred_skills, "
                    "indique 'inférée par la roadmap'.\n"
                    "- Si une notion est validee grace a une competence de extracted_skills, "
                    "indique la preuve directe depuis le CV.\n"
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
