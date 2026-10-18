##########################################################################
# Medicinal Magician backend: fhir.py
#
# PURPOSE
# Reads patient records stored in FHIR format (the healthcare data standard
# from the blueprint) and condenses each one into a short PatientSummary.
#
# INPUT
# FHIR R4 bundle .json files in data/sample_patients/ (e.g. Synthea output).
#
# OUTPUT
# PatientSummary objects (see models.py): conditions, meds, allergies,
# last few visits. Only ACTIVE conditions are kept; resolved ones are dropped.
#
# LATER MILESTONE
# Read from a FHIR test server instead of files. Only this file changes.
##########################################################################
import json
from datetime import date
from pathlib import Path

from .models import PatientListItem, PatientSummary


def _text(codeable: dict | None) -> str | None:
    if not codeable:
        return None
    if codeable.get("text"):
        return codeable["text"]
    for c in codeable.get("coding", []):
        if c.get("display"):
            return c["display"]
    return None


def _name(patient: dict) -> str:
    for n in patient.get("name", []):
        given = " ".join(n.get("given", []))
        # Synthea appends digits to names (e.g. "Maria914"); strip them for display.
        full = f"{given} {n.get('family', '')}".strip()
        return "".join(ch for ch in full if not ch.isdigit())
    return "Unknown"


def _age(birth: str | None) -> int | None:
    if not birth:
        return None
    try:
        b = date.fromisoformat(birth[:10])
    except ValueError:
        return None
    t = date.today()
    return t.year - b.year - ((t.month, t.day) < (b.month, b.day))


def _is_active(resource: dict) -> bool:
    status = resource.get("clinicalStatus", {}).get("coding", [{}])[0].get("code")
    if status:
        return status == "active"
    return "abatementDateTime" not in resource


class PatientStore:
    def __init__(self, folder: Path):
        self._bundles: dict[str, list[dict]] = {}
        self.load(folder)

    def load(self, folder: Path) -> None:
        self._bundles.clear()
        for path in sorted(folder.glob("*.json")):
            try:
                bundle = json.loads(path.read_text(encoding="utf-8"))
            except (json.JSONDecodeError, UnicodeDecodeError):
                continue
            resources = [e.get("resource", {}) for e in bundle.get("entry", [])]
            patient = next((r for r in resources if r.get("resourceType") == "Patient"), None)
            if patient and patient.get("id"):
                self._bundles[patient["id"]] = resources

    def _patient(self, pid: str) -> dict | None:
        res = self._bundles.get(pid)
        if res is None:
            return None
        return next(r for r in res if r.get("resourceType") == "Patient")

    def list(self) -> list[PatientListItem]:
        out = []
        for pid in self._bundles:
            p = self._patient(pid)
            out.append(PatientListItem(id=pid, name=_name(p), birth_date=p.get("birthDate"),
                                       gender=p.get("gender")))
        return out

    def summary(self, pid: str, max_items: int = 15) -> PatientSummary | None:
        res = self._bundles.get(pid)
        if res is None:
            return None
        p = self._patient(pid)

        def collect(rtype: str, field: str, active_only: bool) -> list[str]:
            seen: list[str] = []
            for r in res:
                if r.get("resourceType") != rtype:
                    continue
                if active_only and not _is_active(r):
                    continue
                t = _text(r.get(field))
                if t and t not in seen:
                    seen.append(t)
            return seen[-max_items:]

        meds = [m for m in collect("MedicationRequest", "medicationCodeableConcept", False)]
        encounters = sorted(
            (r for r in res if r.get("resourceType") == "Encounter"),
            key=lambda r: r.get("period", {}).get("start", ""),
        )[-5:]
        enc_text = [
            f"{e.get('period', {}).get('start', '')[:10]}: {_text((e.get('type') or [{}])[0]) or 'encounter'}"
            for e in encounters
        ]

        return PatientSummary(
            id=pid,
            name=_name(p),
            age=_age(p.get("birthDate")),
            gender=p.get("gender"),
            conditions=collect("Condition", "code", True),
            medications=meds,
            allergies=collect("AllergyIntolerance", "code", True),
            recent_encounters=enc_text,
        )
