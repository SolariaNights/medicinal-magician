##########################################################################
# Medicinal Magician backend: models.py  (THE CONTRACT)
#
# PURPOSE
# Defines the exact shape of every piece of data that goes in or out of the
# API: what a login request looks like, what a patient summary contains,
# what an AI suggestion contains. FastAPI uses these to check incoming data
# automatically and to build the /docs page.
#
# WHO USES THIS
# Every other file. The FRONTEND teammate should build against these shapes.
#
# RULE
# If you rename, add or remove a field here, tell the frontend teammate.
# Their screens will break otherwise.
#
# KEY WORDS
#   BaseModel - a Pydantic class; it rejects data with missing/wrong fields
#   Enum      - a field that only allows a fixed set of values
##########################################################################
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field


class Role(str, Enum):
    nurse = "nurse"
    physician = "physician"


# ---------- auth ----------
class LoginRequest(BaseModel):
    username: str
    password: str


class LoginResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    role: Role


# ---------- patients ----------
class PatientListItem(BaseModel):
    id: str
    name: str
    birth_date: str | None = None
    gender: str | None = None


class PatientSummary(BaseModel):
    id: str
    name: str
    age: int | None = None
    gender: str | None = None
    conditions: list[str] = []
    medications: list[str] = []
    allergies: list[str] = []
    recent_encounters: list[str] = []
    # Fields the source record didn't contain at all. "Unknown" is not the
    # same as "none": the AI must not assume a missing allergy list = no allergies.
    missing_fields: list[str] = []

    def as_prompt_text(self) -> str:
        def fmt(name: str, items: list[str]) -> str:
            if name in self.missing_fields:
                return "UNKNOWN (not in record; do not assume none)"
            return ", ".join(items) if items else "none recorded"
        return (
            f"Patient: {self.age if self.age is not None else 'unknown'}-year-old {self.gender or 'unknown sex'}\n"
            f"Active conditions: {fmt('conditions', self.conditions)}\n"
            f"Medications: {fmt('medications', self.medications)}\n"
            f"Allergies: {fmt('allergies', self.allergies)}\n"
            f"Recent encounters: {fmt('recent_encounters', self.recent_encounters)}"
        )


# ---------- sessions & suggestions ----------
class CreateSessionRequest(BaseModel):
    patient_id: str


class SymptomInput(BaseModel):
    text: str = Field(min_length=3, max_length=4000)


class Likelihood(str, Enum):
    low = "low"
    moderate = "moderate"
    high = "high"


class Consideration(BaseModel):
    """One differential to consider. Never phrased as a diagnosis."""
    id: str
    condition: str
    likelihood: Likelihood
    rationale: str
    supporting_findings: list[str] = []
    guideline_refs: list[str] = []          # ids of retrieved guideline chunks
    suggested_next_steps: list[str] = []


class SuggestionSet(BaseModel):
    considerations: list[Consideration]
    red_flags: list[str] = []
    follow_up_questions: list[str] = []
    disclaimer: str = (
        "Clinical assistant output: possibilities to consider, not a diagnosis. "
        "The treating clinician is the sole diagnostic authority."
    )


class Session(BaseModel):
    id: str
    patient_id: str
    created_by: str
    created_at: datetime
    symptom_text: str = ""
    suggestions: SuggestionSet | None = None


class FeedbackRequest(BaseModel):
    consideration_id: str
    accepted: bool
    note: str | None = None


class AuditEntry(BaseModel):
    at: datetime
    user: str
    action: str
    patient_id: str | None = None
