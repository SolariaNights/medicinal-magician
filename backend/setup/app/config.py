##########################################################################
# Medicinal Magician backend: config.py
#
# PURPOSE
# All settings in one place: where the data lives, which AI model to use,
# API keys, login timeout, which frontend address is allowed to call us.
#
# HOW TO CHANGE A SETTING
# Don't edit this file. Edit the .env file in the backend/setup folder instead
# (copy .env.example to .env first). Values here are just the defaults.
#
# NEVER put a real API key in this file or any file that gets committed.
##########################################################################
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

PATIENT_DIR = Path(os.getenv("PATIENT_DIR", BASE_DIR / "data" / "sample_patients"))
GUIDELINE_DIR = Path(os.getenv("GUIDELINE_DIR", BASE_DIR / "data" / "guidelines"))

# "mock" works with no API key. Set to "anthropic" or "openai" + the key to use a real model.
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "mock")
LLM_MODEL = os.getenv("LLM_MODEL", "")
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

JWT_SECRET = os.getenv("JWT_SECRET", "dev-only-change-me-before-deploying-0000")
JWT_EXPIRE_MINUTES = int(os.getenv("JWT_EXPIRE_MINUTES", "30"))  # auto-logout

FRONTEND_ORIGINS = os.getenv(
    "FRONTEND_ORIGINS", "http://localhost:5173,http://127.0.0.1:5173"
).split(",")
