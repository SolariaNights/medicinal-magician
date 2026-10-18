##########################################################################
# Medicinal Magician backend: tests/test_api.py
#
# PURPOSE
# Automatic checks that the whole backend still works. Each function named
# test_... pretends to be the frontend, calls the API, and asserts the
# answer is right. If any assert fails, pytest shows which one and why.
#
# HOW TO RUN (from the backend/setup folder)
#     pytest -q
# Uses the mock AI, so no API key or internet needed.
#
# RULE
# Run this before every push. If you fix a bug, add a test for it.
##########################################################################
import os

os.environ["LLM_PROVIDER"] = "mock"

from fastapi.testclient import TestClient  # noqa: E402
from app.main import app  # noqa: E402

client = TestClient(app)


def login(user="nurse", pw="nurse123"):
    r = client.post("/auth/login", json={"username": user, "password": pw})
    assert r.status_code == 200
    return {"Authorization": f"Bearer {r.json()['access_token']}"}


def test_health():
    body = client.get("/health").json()
    assert body["patients"] >= 2 and body["guideline_chunks"] >= 5


def test_requires_login():
    assert client.get("/patients").status_code == 401


def test_bad_password():
    r = client.post("/auth/login", json={"username": "nurse", "password": "nope"})
    assert r.status_code == 401


def test_patient_summary():
    h = login()
    s = client.get("/patients/demo-001/summary", headers=h).json()
    assert "Type 2 diabetes mellitus" in s["conditions"]
    assert "Acute bronchitis" not in s["conditions"]  # resolved, so excluded
    assert s["allergies"] == ["Penicillin"]


def test_full_flow_chest_pain():
    h = login()
    sid = client.post("/sessions", json={"patient_id": "demo-001"}, headers=h).json()["id"]
    r = client.post(f"/sessions/{sid}/symptoms",
                    json={"text": "crushing chest pain radiating to left arm, sweating"}, headers=h)
    assert r.status_code == 200
    out = r.json()
    names = [c["condition"] for c in out["considerations"]]
    assert "Acute coronary syndrome" in names
    assert out["red_flags"]
    assert "not a diagnosis" in out["disclaimer"]

    cid = out["considerations"][0]["id"]
    fb = client.post(f"/sessions/{sid}/feedback",
                     json={"consideration_id": cid, "accepted": True}, headers=h)
    assert fb.status_code == 204


def test_wheezing_matches_asthma():
    h = login()
    sid = client.post("/sessions", json={"patient_id": "demo-002"}, headers=h).json()["id"]
    out = client.post(f"/sessions/{sid}/symptoms",
                      json={"text": "wheezing and shortness of breath, using inhaler a lot"},
                      headers=h).json()
    assert "Asthma exacerbation" in [c["condition"] for c in out["considerations"]]


def test_audit_physician_only():
    assert client.get("/audit", headers=login()).status_code == 403
    r = client.get("/audit", headers=login("doctor", "doctor123"))
    assert r.status_code == 200 and len(r.json()) > 0


def test_symptoms_outweigh_history():
    # Regression: a diabetic/hypertensive patient's history used to pull chest pain to the top.
    h = login()
    sid = client.post("/sessions", json={"patient_id": "demo-001"}, headers=h).json()["id"]
    out = client.post(f"/sessions/{sid}/symptoms",
                      json={"text": "very thirsty, peeing a lot, nausea and vomiting"},
                      headers=h).json()
    assert out["considerations"][0]["condition"] == "Uncontrolled diabetes mellitus"


# ---------- Alex's EHR integration layer ----------
def test_alex_patient_listed_and_summarized():
    h = login()
    ids = [p["id"] for p in client.get("/patients", headers=h).json()]
    assert "test-001" in ids and "demo-001" in ids
    s = client.get("/patients/test-001/summary", headers=h).json()
    assert s["conditions"] == ["Diabetes", "High Blood Pressure"]
    assert s["allergies"] == ["Nuts"]


def test_unknown_patient_404():
    assert client.get("/patients/nope/summary", headers=login()).status_code == 404


def test_missing_field_is_unknown_not_none(monkeypatch):
    from app.ehr import MedicalMagician as mm
    from app.ehr import adapter
    monkeypatch.setattr(mm, "patients", mm.patients + [{"id": "test-x", "conditions": ["Asthma"]}])
    s = adapter.get_summary("test-x")
    assert set(s.missing_fields) == {"medications", "allergies"}
    assert "UNKNOWN" in s.as_prompt_text() and "do not assume none" in s.as_prompt_text()


def test_alex_patient_full_flow():
    h = login()
    sid = client.post("/sessions", json={"patient_id": "test-002"}, headers=h).json()["id"]
    out = client.post(f"/sessions/{sid}/symptoms",
                      json={"text": "wheezing, short of breath"}, headers=h).json()
    assert "Asthma exacerbation" in [c["condition"] for c in out["considerations"]]
