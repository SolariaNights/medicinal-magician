##########################################################################
# Medicinal Magician backend: llm.py  (AI model adapter)
#
# PURPOSE
# The only file that talks to an AI model. Everything else just calls
# complete_json() and doesn't care which model is behind it.
#
# PROVIDERS (pick one in .env with LLM_PROVIDER=...)
#   mock      - default. No API key, no internet. Builds a fake-but-valid
#               answer from the guideline text so everyone can develop now.
#   anthropic - Claude. Needs ANTHROPIC_API_KEY in .env.
#   openai    - OpenAI. Needs OPENAI_API_KEY in .env.
#
# LATER MILESTONE
# Add a HIPAA-covered provider (signed BAA) as one more branch here.
##########################################################################
import json
import re

import httpx

from . import config
from .retrieval import Chunk


class LLMError(RuntimeError):
    pass


async def complete_json(system: str, user: str, chunks: list[Chunk]) -> str:
    provider = config.LLM_PROVIDER.lower()
    if provider == "mock":
        return _mock(chunks)
    if provider == "anthropic":
        return await _anthropic(system, user)
    if provider == "openai":
        return await _openai(system, user)
    raise LLMError(f"Unknown LLM_PROVIDER '{config.LLM_PROVIDER}'")


async def _anthropic(system: str, user: str) -> str:
    if not config.ANTHROPIC_API_KEY:
        raise LLMError("ANTHROPIC_API_KEY is not set")
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.anthropic.com/v1/messages",
            headers={"x-api-key": config.ANTHROPIC_API_KEY,
                     "anthropic-version": "2023-06-01",
                     "content-type": "application/json"},
            json={"model": config.LLM_MODEL or "claude-sonnet-5-5",
                  "max_tokens": 2000,
                  "system": system,
                  "messages": [{"role": "user", "content": user}]},
        )
    if r.status_code != 200:
        raise LLMError(f"Anthropic API {r.status_code}: {r.text[:300]}")
    return "".join(b.get("text", "") for b in r.json().get("content", []))


async def _openai(system: str, user: str) -> str:
    if not config.OPENAI_API_KEY:
        raise LLMError("OPENAI_API_KEY is not set")
    async with httpx.AsyncClient(timeout=60) as client:
        r = await client.post(
            "https://api.openai.com/v1/chat/completions",
            headers={"Authorization": f"Bearer {config.OPENAI_API_KEY}"},
            json={"model": config.LLM_MODEL or "gpt-4o-mini",
                  "response_format": {"type": "json_object"},
                  "messages": [{"role": "system", "content": system},
                               {"role": "user", "content": user}]},
        )
    if r.status_code != 200:
        raise LLMError(f"OpenAI API {r.status_code}: {r.text[:300]}")
    return r.json()["choices"][0]["message"]["content"]


def _field(text: str, label: str) -> list[str]:
    m = re.search(rf"^{label}:\s*(.+)$", text, flags=re.M | re.I)
    return [s.strip() for s in m.group(1).split(";") if s.strip()] if m else []


def _mock(chunks: list[Chunk]) -> str:
    considerations, red_flags, questions = [], [], []
    for chunk in chunks[:3]:
        for j, cond in enumerate(_field(chunk.text, "Consider")[:2]):
            considerations.append({
                "id": f"c{len(considerations) + 1}",
                "condition": cond,
                "likelihood": "moderate" if j == 0 else "low",
                "rationale": f"[mock] Matches the guideline section '{chunk.heading}'.",
                "supporting_findings": [],
                "guideline_refs": [chunk.id],
                "suggested_next_steps": _field(chunk.text, "Workup")[:3],
            })
        red_flags += _field(chunk.text, "Red flags")
        questions += _field(chunk.text, "Ask")
    if not considerations:
        considerations.append({
            "id": "c1", "condition": "Insufficient information",
            "likelihood": "low",
            "rationale": "[mock] No guideline section matched the symptoms entered.",
            "supporting_findings": [], "guideline_refs": [], "suggested_next_steps": [],
        })
    return json.dumps({
        "considerations": considerations,
        "red_flags": list(dict.fromkeys(red_flags))[:6],
        "follow_up_questions": list(dict.fromkeys(questions))[:5],
    })
