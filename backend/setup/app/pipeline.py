##########################################################################
# Medicinal Magician backend: pipeline.py  (THE CORE LOGIC)
#
# PURPOSE
# Turns "patient history + typed symptoms" into a safe, checked list of
# possibilities for the clinician to consider.
#
# STEPS
#   1. retrieval.py finds matching guideline sections
#   2. build a prompt: history + symptoms + guideline excerpts
#   3. llm.py asks the AI, which must answer in strict JSON
#   4. check the answer against models.SuggestionSet
#      - bad/garbled answer -> ask once more, then give up with an error
#      - citations to guideline ids we never sent -> removed
#
# SAFETY (FDA "clinical assistant" rule from the blueprint)
# The system prompt forbids diagnoses, and every response carries a
# disclaimer that the clinician is the sole diagnostic authority.
##########################################################################
import json
import re

from pydantic import ValidationError

from . import llm
from .models import PatientSummary, SuggestionSet
from .retrieval import Chunk, GuidelineIndex

SYSTEM_PROMPT = """You are a clinical decision-support assistant used by nurses and physicians.
You surface POSSIBILITIES TO CONSIDER. You never state a diagnosis. The clinician decides.

Rules:
- Base every consideration on the patient summary, the symptoms, and the guideline excerpts given.
- Cite guideline excerpts by their id in "guideline_refs". Only use ids that appear in the excerpts.
- If the information is insufficient, say so and ask follow-up questions instead of guessing.
- List any emergency warning signs in "red_flags".
- Respond with ONLY a JSON object, no prose, matching exactly:
{
  "considerations": [
    {"id": "c1", "condition": str, "likelihood": "low"|"moderate"|"high",
     "rationale": str, "supporting_findings": [str], "guideline_refs": [str],
     "suggested_next_steps": [str]}
  ],
  "red_flags": [str],
  "follow_up_questions": [str]
}
Give at most 5 considerations, most relevant first."""


##########################################
# Function: build_user_prompt
# Input:  patient summary, typed symptoms, matching guideline chunks
# Output: one block of text sent to the AI as the question
##########################################
def build_user_prompt(summary: PatientSummary, symptoms: str, chunks: list[Chunk]) -> str:
    excerpts = "\n\n".join(f"[{c.id}] {c.heading}\n{c.text}" for c in chunks) or "(none matched)"
    return (f"PATIENT HISTORY\n{summary.as_prompt_text()}\n\n"
            f"CURRENT SYMPTOMS (entered by clinician)\n{symptoms}\n\n"
            f"GUIDELINE EXCERPTS\n{excerpts}")


##########################################
# Function: _extract_json
# Input:  the AI's raw reply (text)
# Output: a Python dict
# Why: AIs sometimes wrap JSON in ```code fences``` or add a sentence
#      before it. This cuts out just the {...} part.
##########################################
def _extract_json(raw: str) -> dict:
    raw = raw.strip()
    fenced = re.search(r"```(?:json)?\s*(.*?)```", raw, flags=re.S)
    if fenced:
        raw = fenced.group(1)
    start, end = raw.find("{"), raw.rfind("}")
    if start == -1 or end == -1:
        raise ValueError("no JSON object in model output")
    return json.loads(raw[start:end + 1])


##########################################
# Function: suggest   (called by main.py's /symptoms endpoint)
# Input:  patient summary, typed symptoms, the guideline index
# Output: a checked SuggestionSet, or raises LLMError if the AI fails
##########################################
async def suggest(summary: PatientSummary, symptoms: str, index: GuidelineIndex) -> SuggestionSet:
    # Step 1: find guideline sections that match the symptoms.
    chunks = index.search(symptoms, history=" ".join(summary.conditions))
    # Step 2: build the question for the AI.
    user = build_user_prompt(summary, symptoms, chunks)
    valid_ids = {c.id for c in chunks}

    last_error = ""
    for _ in range(2):  # try at most twice
        # On the retry, tell the AI what was wrong with its first answer.
        prompt = user if not last_error else (
            f"{user}\n\nYour previous reply was invalid ({last_error}). Return only the JSON object.")
        # Step 3: ask the AI.
        raw = await llm.complete_json(SYSTEM_PROMPT, prompt, chunks)
        # Step 4: check the answer has exactly the fields models.py requires.
        try:
            result = SuggestionSet.model_validate(_extract_json(raw))
        except (ValueError, ValidationError) as e:
            last_error = str(e)[:200]
            continue
        # Step 5: remove citations to guideline sections we never gave it
        # (that would be the AI making up a source).
        for c in result.considerations:
            c.guideline_refs = [r for r in c.guideline_refs if r in valid_ids]
        return result
    raise llm.LLMError(f"Model output failed validation twice: {last_error}")
