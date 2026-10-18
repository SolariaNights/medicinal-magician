##########################################################################
# Medicinal Magician backend: ehr/adapter.py
# (bridge between Alex's integration layer and the API)
#
# PURPOSE
# Alex's MedicalMagician.py finds the patient record. This file converts
# his plain dictionary into the API's PatientSummary, so either side can
# change inside without breaking the other.
#
# SAFETY RULE (from Alex's success criteria)
# Missing information is NOT proof of no medical issues.
#   key missing or null -> listed in missing_fields, shown to AI as UNKNOWN
#   empty list []       -> "none recorded"
#
# INPUT  patient id (string)
# OUTPUT PatientSummary, or None if not found / bad input
##########################################################################
from ..models import PatientListItem, PatientSummary
from . import MedicalMagician as mm

FIELDS = ("conditions", "medications", "allergies")


def list_patients() -> list[PatientListItem]:
    return [PatientListItem(id=p["id"], name=p.get("name", p["id"]), gender=p.get("gender"))
            for p in mm.patients if isinstance(p, dict) and "id" in p]


def get_summary(patient_id: str) -> PatientSummary | None:
    if not isinstance(patient_id, str):
        return None
    record = mm.get_patient(patient_id)
    if record is None:
        return None

    values, missing = {}, []
    for field in FIELDS:
        raw = record.get(field)
        if raw is None:
            missing.append(field)
            values[field] = []
        elif isinstance(raw, list):
            values[field] = [str(x) for x in raw]
        else:
            values[field] = [str(raw)]

    return PatientSummary(
        id=record["id"],
        name=record.get("name", record["id"]),
        age=record.get("age"),
        gender=record.get("gender"),
        missing_fields=missing,
        **values,
    )
