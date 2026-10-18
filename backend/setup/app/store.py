##########################################################################
# Medicinal Magician backend: store.py
#
# PURPOSE
# Remembers triage sessions, clinician feedback and the audit log
# (who looked at which patient, when).
#
# IMPORTANT
# Everything is kept in memory, so it is ERASED when the server restarts.
# Fine for the demo.
#
# LATER MILESTONE
# Move to PostgreSQL tables, keeping the same method names.
##########################################################################
import uuid
from datetime import datetime, timezone

from .models import AuditEntry, FeedbackRequest, Session


class Store:
    def __init__(self):
        self.sessions: dict[str, Session] = {}
        self.feedback: dict[str, list[FeedbackRequest]] = {}
        self.audit: list[AuditEntry] = []

    def log(self, user: str, action: str, patient_id: str | None = None) -> None:
        self.audit.append(AuditEntry(at=datetime.now(timezone.utc), user=user,
                                     action=action, patient_id=patient_id))

    def create_session(self, patient_id: str, user: str) -> Session:
        s = Session(id=uuid.uuid4().hex[:12], patient_id=patient_id, created_by=user,
                    created_at=datetime.now(timezone.utc))
        self.sessions[s.id] = s
        return s

    def add_feedback(self, session_id: str, fb: FeedbackRequest) -> None:
        self.feedback.setdefault(session_id, []).append(fb)
