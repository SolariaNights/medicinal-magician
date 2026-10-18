##########################################################################
# Medicinal Magician backend: patients.py
#
# PURPOSE
# The one place the API asks for patient records, whatever the source.
# Checks Alex's EHR integration layer first, then FHIR files.
#
# INPUT  patient id, e.g. "test-001" or "demo-001"
# OUTPUT PatientSummary, or None if no source knows that patient
##########################################################################
from .ehr import adapter as ehr
from .fhir import PatientStore
from .models import PatientListItem, PatientSummary


class PatientDirectory:
    def __init__(self, fhir_store: PatientStore):
        self.fhir = fhir_store

    def list(self) -> list[PatientListItem]:
        return ehr.list_patients() + self.fhir.list()

    def summary(self, patient_id: str) -> PatientSummary | None:
        return ehr.get_summary(patient_id) or self.fhir.summary(patient_id)
