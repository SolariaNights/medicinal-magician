# Medicinal Magician

Medicinal Magician is a full-stack clinical decision-support prototype built to demonstrate how a nurse or physician could review a patient’s history and symptoms, then receive structured suggestions grounded in guideline excerpts. The project combines a React frontend with a FastAPI backend that loads synthetic patient records, searches guideline content, and returns a list of possibilities to consider rather than a diagnosis.

This is a demo application for exploration and education. It is intentionally designed around synthetic, non-production patient data and clearly warns users that the clinician remains the final decision-maker.

## What the project does

The app supports a workflow similar to a triage or clinical review process:

- A clinician signs in with a demo account.
- A patient is selected from the available synthetic patient list.
- The user enters current symptoms.
- The backend retrieves relevant guideline sections.
- The AI layer generates a structured response with:
  - possible conditions to consider
  - red flags and warning signs
  - follow-up questions
  - next-step recommendations
  - relevant guideline references
- The clinician can accept or reject each suggestion and review the audit trail if they have physician access.

## Core idea

Medicinal Magician is not meant to replace clinical judgment. The app explicitly frames outputs as “possibilities to consider” and not diagnoses. It is meant to show a safe, explainable decision-support workflow that can be expanded later with real guidelines, better patient data handling, and robust clinical review tooling.

## Project structure

```text
medicinal-magician/
├── README.md
├── package.json
├── vite.config.js
├── index.html
├── public/
├── src/
│   ├── App.jsx
│   ├── ClinicianWorkspace.jsx
│   ├── App.css
│   ├── index.css
│   └── main.jsx
├── backend/
│   └── setup/
│       ├── README.md
│       ├── requirements.txt
│       ├── run.py
│       ├── pytest.ini
│       ├── app/
│       ├── data/
│       └── tests/
└── ehr_intergration/
```

## Frontend

The frontend is a Vite + React application that provides the clinician workspace and demo assessment flow.

Key behavior in the UI:

- patient sign-in flow for demo clinicians
- patient picker and summary view
- symptoms entry form
- AI-generated suggestions panel with red flags and follow-up questions
- accept/reject feedback for each consideration
- synthetic-only warning messaging and safety notes

## Backend

The backend is a FastAPI application located in `backend/setup`. It includes:

- JWT-based authentication for demo nurse and physician accounts
- patient lookup from synthetic and demo data sources
- guideline retrieval matching the typed symptoms
- AI pipeline that turns patient context + guideline excerpts into structured output
- session handling, clinician feedback, and audit logging
- OpenAPI documentation at `/docs`

The backend supports a mock LLM by default, so it can run without external API keys. It can also be configured to call Anthropic or OpenAI if an API key is set.

## Demo accounts

The demo backend includes seeded accounts:

- nurse / nurse123
- doctor / doctor123

The nurse account can access standard workflow pages. The physician account is required to view the audit log.

## Synthetic data and safety

This project uses fictional patient data and placeholder clinical guidelines. It is intended as a prototype and should never be used with real patient information or as a production clinical tool.

The application intentionally includes a disclaimer and cautionary language around diagnoses, red flags, and clinician decision-making.

## Tech stack

- Frontend: React, Vite, JavaScript
- Backend: FastAPI, Pydantic, JWT, pytest
- Data: synthetic patient records and guideline markdown snippets
- LLM integration: mock provider by default, with optional Anthropic/OpenAI support

## Running the app locally

### 1) Install frontend dependencies

```bash
npm install
```

### 2) Start the backend

From the project root:

```bash
cd backend\setup
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python run.py
```

The API server will run on:

- http://127.0.0.1:8000
- Swagger docs: http://127.0.0.1:8000/docs

### 3) Start the frontend

Open a new terminal in the project root:

```bash
npm run dev
```

The Vite app will run on:

- http://localhost:5173

### 4) Log in and use the app

Open the frontend in the browser and sign in using a demo account such as `nurse / nurse123`.

If you want to use a real LLM provider instead of the mock provider, copy the example environment file and update it:

```bash
cd backend\setup
copy .env.example .env
```

Then edit `.env` to set the model provider and API keys as needed.

## Backend test status

The backend includes automated tests for login, patient lookups, symptom workflows, feedback, and role-based access.

Run them with:

```bash
cd backend\setup
pytest -q
```

## Why this project matters

Medicinal Magician demonstrates a practical architecture for a clinical decision-support system:

- patient context from a summary model
- symptom-based retrieval of relevant medical guidance
- structured AI output that encourages review rather than automation
- user feedback loop for clinician acceptance or rejection
- auditability for physician oversight

It is a strong starting point for exploring safer AI workflows in healthcare, especially when paired with synthetic datasets and careful prompt and output validation.

## Notes

- This project is a prototype and not a regulated medical product.
- No real patient data should be entered into the application.
- The system is built to encourage review, transparency, and human oversight at every step.
