# Medicinal Magician — Backend

FastAPI backend for the clinical assistant. **Synthetic data only. No real patient data, ever.**

## Which file do I run?

**`run.py`** — and nothing else. Every other file is imported by it automatically.

| You want to... | Run this (from the `backend/setup` folder) |
|---|---|
| Start the backend | `python run.py`, then open http://127.0.0.1:8000/docs |
| Check nothing is broken | `pytest -q` |
| Test only Alex's patient lookup | `cd app\ehr` then `python MedicalMagician.py` |

Don't run `main.py` or any file inside `app/` directly — you'll get an "attempted relative import" error. That's normal; use `run.py`.

## Run it (Windows, VS Code terminal)

```powershell
cd backend\setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
python run.py
```

macOS/Linux: `source venv/bin/activate` and `cp .env.example .env`.

Then open **http://localhost:8000/docs**. Every endpoint is listed there and you can try them in the browser:
1. `POST /auth/login` with `nurse` / `nurse123` (or `doctor` / `doctor123`)
2. Click **Authorize** (top right), paste the `access_token`
3. `GET /patients` → `POST /sessions` → `POST /sessions/{id}/symptoms`

Run tests: `pytest -q`

## Endpoints (the contract with the frontend)

| Method | Path | Who | Returns |
|---|---|---|---|
| POST | `/auth/login` | anyone | token + role |
| GET | `/patients` | logged in | patient list |
| GET | `/patients/{id}/summary` | logged in | conditions, meds, allergies, encounters |
| POST | `/sessions` | logged in | new triage session |
| GET | `/sessions/{id}` | logged in | session incl. latest suggestions |
| POST | `/sessions/{id}/symptoms` | logged in | `SuggestionSet` (considerations, red flags, follow-up questions) |
| POST | `/sessions/{id}/feedback` | logged in | 204; records accept/reject per consideration |
| GET | `/audit` | physician | who did what to which patient |
| GET | `/health` | anyone | status |

Frontend calls need the header `Authorization: Bearer <token>`. All response shapes live in `app/models.py`. **If you change a model, tell the frontend.**

## How it works

```
symptoms + patient history ──► retrieval.py  (find matching guideline sections)
                           ──► pipeline.py   (build prompt)
                           ──► llm.py        (mock | anthropic | openai)
                           ──► pipeline.py   (parse JSON, validate, retry once, drop fake citations)
                           ──► SuggestionSet
```

| File | Job | Changes later |
|---|---|---|
| `app/models.py` | API shapes | rarely; coordinate with frontend |
| `app/ehr/MedicalMagician.py` + `patients.json` | **Alex's** EHR integration layer: `get_patient(id)` | Alex owns this; moves to a FHIR test server later |
| `app/ehr/adapter.py` | turns Alex's dict into `PatientSummary`; flags missing fields as unknown | only if Alex's output format changes |
| `app/patients.py` | asks Alex's layer first, then FHIR files | rarely |
| `app/fhir.py` | reads FHIR bundles → `PatientSummary` | swap file loading for a FHIR server |
| `app/retrieval.py` | keyword search over `data/guidelines/*.md` | swap for pgvector embeddings, same `search()` signature |
| `app/llm.py` | model provider adapter | add a BAA-covered provider |
| `app/store.py` | sessions, feedback, audit (in memory) | move to Postgres |
| `app/auth.py` | JWT login, 2 roles, 30-min expiry | swap for OIDC |

## Data

- **Patients (Alex's layer):** `app/ehr/patients.json` has `test-001` and `test-002`. Add records there; a record missing `allergies`/`medications`/`conditions` is shown to the AI as UNKNOWN, not "none".
- **Patients (FHIR):** `data/sample_patients/` has 2 hand-made demo patients. For realistic ones, generate with [Synthea](https://github.com/synthetichealth/synthea) (needs Java) and copy files from `output/fhir/` here. They're picked up on restart.
- **Guidelines:** `data/guidelines/triage_placeholders.md` is a team-written **placeholder**, not a clinical source. Replace with summaries of real public guidelines and cite the URL in each section. Keep the `Consider: / Red flags: / Workup: / Ask:` line format.

## Using a real model

In `.env`: set `LLM_PROVIDER=anthropic` (or `openai`) and the matching API key. Keys go only in `.env`, never in code or commits.
