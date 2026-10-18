##########################################################################
# Medicinal Magician backend: auth.py  (login + permissions)
#
# PURPOSE
# Checks usernames/passwords, hands out tokens, and decides who may call
# what. Two roles: nurse and physician (only physicians can see the audit log).
#
# DEMO LOGINS (fake, for development only)
#   nurse  / nurse123
#   doctor / doctor123
#
# HOW TOKENS WORK
# Login returns a token (JWT). The frontend sends it on every request as
# "Authorization: Bearer <token>". Tokens expire after 30 minutes, which
# is the auto-logout requirement from the blueprint.
#
# LATER MILESTONE
# Swap for a real identity provider (Okta/Auth0). Routes don't change.
##########################################################################
import hashlib
import hmac
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

from . import config
from .models import Role


def _hash(pw: str) -> str:
    return hashlib.sha256(pw.encode()).hexdigest()


# DEV ONLY. Synthetic users for the demo.
DEMO_USERS = {
    "nurse":  {"pw": _hash("nurse123"),  "role": Role.nurse},
    "doctor": {"pw": _hash("doctor123"), "role": Role.physician},
}

_bearer = HTTPBearer(auto_error=False)


def authenticate(username: str, password: str) -> Role | None:
    user = DEMO_USERS.get(username)
    if user and hmac.compare_digest(user["pw"], _hash(password)):
        return user["role"]
    return None


def create_token(username: str, role: Role) -> str:
    exp = datetime.now(timezone.utc) + timedelta(minutes=config.JWT_EXPIRE_MINUTES)
    return jwt.encode({"sub": username, "role": role.value, "exp": exp},
                      config.JWT_SECRET, algorithm="HS256")


class CurrentUser:
    def __init__(self, username: str, role: Role):
        self.username, self.role = username, role


def current_user(creds: HTTPAuthorizationCredentials | None = Depends(_bearer)) -> CurrentUser:
    if creds is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Missing bearer token")
    try:
        data = jwt.decode(creds.credentials, config.JWT_SECRET, algorithms=["HS256"])
    except jwt.ExpiredSignatureError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Session expired, log in again")
    except jwt.InvalidTokenError:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, "Invalid token")
    return CurrentUser(data["sub"], Role(data["role"]))


def require_physician(user: CurrentUser = Depends(current_user)) -> CurrentUser:
    if user.role != Role.physician:
        raise HTTPException(status.HTTP_403_FORBIDDEN, "Physician role required")
    return user
