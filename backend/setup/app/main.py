##########################################################################
# Medicinal Magician backend: main.py  (THE ENTRY POINT)
#
# PURPOSE
# This is the "front door" of the backend. It creates the web server and
# defines every URL (endpoint) the frontend can call. Each endpoint is a
# small function that checks the request, hands the real work to another
# file, and sends back the answer.
#
# HOW TO RUN
# Don't run this file directly. From the backend/setup folder run:
#     python run.py
# then open http://127.0.0.1:8000/docs to try every endpoint in the browser.
#
# WHAT HAPPENS ON A TYPICAL VISIT
#   1. POST /auth/login                  -> nurse/doctor logs in, gets a token
#   2. GET  /patients                    -> pick a patient
#   3. POST /sessions                    -> open a triage session for them
#   4. POST /sessions/{id}/symptoms      -> type symptoms, get AI suggestions
#   5. POST /sessions/{id}/feedback      -> clinician accepts/rejects each one
#
# WHO DOES WHAT (other files)
#   models.py    - the exact shape of every request and response
#   auth.py      - login, tokens, nurse vs physician permissions
#   patients.py  - finds patient history (Alex's layer + FHIR files)
#   pipeline.py  - symptoms + history -> guidelines -> AI -> checked answer
#   store.py     - remembers sessions, feedback and the audit log
#
# KEY WORDS
#   endpoint  - a URL the frontend calls, e.g. GET /patients
#   token     - proof you logged in; sent as "Authorization: Bearer <token>"
#   Depends() - FastAPI runs that function first (here: "is this user
#               logged in?") and refuses the request if it fails
#   HTTPException(404, ...) - sends an error back to the frontend
##########################################################################
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from . import config, llm, pipeline
from .auth import CurrentUser, authenticate, create_token, current_user, require_physician
from .fhir import PatientStore
from .models import (AuditEntry, CreateSessionRequest, FeedbackRequest, LoginRequest,
                     LoginResponse, PatientListItem, PatientSummary, Session,
                     SuggestionSet, SymptomInput)
from .patients import PatientDirectory
from .retrieval import GuidelineIndex
from .store import Store

# Create the web app. The title/description show up on the /docs page.
app = FastAPI(title="Medicinal Magician API", version="0.1.0",
              description="Clinical assistant backend. Synthetic data only.")

# CORS: browsers block a website from calling a server on a different port
# unless the server allows it. This allows the React (Vite) frontend on
# port 5173 to call us on port 8000.
app.add_middleware(CORSMiddleware, allow_origins=config.FRONTEND_ORIGINS,
                   allow_credentials=True, allow_methods=["*"], allow_headers=["*"])

# Load everything once when the server starts (not on every request).
patients = PatientDirectory(PatientStore(config.PATIENT_DIR))  # patient records
guidelines = GuidelineIndex(config.GUIDELINE_DIR)              # medical guideline text
store = Store()                                                # sessions + audit log


# Quick "is the server alive?" check. No login needed.
@app.get("/health")
def health():
    return {"status": "ok", "patients": len(patients.list()),
            "guideline_chunks": len(guidelines.chunks), "llm_provider": config.LLM_PROVIDER}


# ---------- auth ----------
# Check username/password. If correct, return a token the frontend must
# attach to every other request.
@app.post("/auth/login", response_model=LoginResponse)
def login(body: LoginRequest):
    role = authenticate(body.username, body.password)
    if role is None:
        raise HTTPException(401, "Wrong username or password")
    store.log(body.username, "login")
    return LoginResponse(access_token=create_token(body.username, role), role=role)


# ---------- patients ----------
# List every (fictional) patient so the frontend can show a picker.
@app.get("/patients", response_model=list[PatientListItem])
def list_patients(user: CurrentUser = Depends(current_user)):
    return patients.list()


# One patient's condensed history: conditions, meds, allergies, visits.
# Logged in the audit trail because viewing a record is a privacy event.
@app.get("/patients/{patient_id}/summary", response_model=PatientSummary)
def patient_summary(patient_id: str, user: CurrentUser = Depends(current_user)):
    s = patients.summary(patient_id)
    if s is None:
        raise HTTPException(404, "Patient not found")
    store.log(user.username, "view_patient", patient_id)
    return s


# ---------- sessions ----------
# Helper used by several endpoints below: find a session or send a 404.
def _get_session(session_id: str) -> Session:
    s = store.sessions.get(session_id)
    if s is None:
        raise HTTPException(404, "Session not found")
    return s


# Start a triage session for one patient. Returns a session id the
# frontend uses for the rest of the visit.
@app.post("/sessions", response_model=Session, status_code=201)
def create_session(body: CreateSessionRequest, user: CurrentUser = Depends(current_user)):
    if patients.summary(body.patient_id) is None:
        raise HTTPException(404, "Patient not found")
    store.log(user.username, "open_session", body.patient_id)
    return store.create_session(body.patient_id, user.username)


# Re-load a session (e.g. after a page refresh).
@app.get("/sessions/{session_id}", response_model=Session)
def get_session(session_id: str, user: CurrentUser = Depends(current_user)):
    return _get_session(session_id)


# THE MAIN FEATURE. Takes the typed symptoms, runs the AI pipeline, and
# returns "possibilities to consider". `async` lets the server keep
# answering other requests while it waits on the AI.
@app.post("/sessions/{session_id}/symptoms", response_model=SuggestionSet)
async def submit_symptoms(session_id: str, body: SymptomInput,
                          user: CurrentUser = Depends(current_user)):
    session = _get_session(session_id)
    summary = patients.summary(session.patient_id)
    try:
        result = await pipeline.suggest(summary, body.text, guidelines)
    except llm.LLMError as e:
        # 502 = "a service we depend on (the AI) failed", not the user's fault.
        raise HTTPException(502, f"AI step failed: {e}")
    session.symptom_text = body.text
    session.suggestions = result
    store.log(user.username, "generate_suggestions", session.patient_id)
    return result


# Clinician marks a suggestion as useful or not. Collected now so we can
# measure accuracy later (Phase 4 in the blueprint).
@app.post("/sessions/{session_id}/feedback", status_code=204)
def feedback(session_id: str, body: FeedbackRequest, user: CurrentUser = Depends(current_user)):
    session = _get_session(session_id)
    ids = {c.id for c in (session.suggestions.considerations if session.suggestions else [])}
    if body.consideration_id not in ids:
        raise HTTPException(404, "No such consideration in this session")
    store.add_feedback(session_id, body)
    store.log(user.username, f"feedback:{'accept' if body.accepted else 'reject'}",
              session.patient_id)


# ---------- audit ----------
# Who did what to which patient, newest first. Physicians only.
@app.get("/audit", response_model=list[AuditEntry])
def audit(user: CurrentUser = Depends(require_physician)):
    return list(reversed(store.audit[-200:]))
