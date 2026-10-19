import { useState } from 'react'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000'

async function apiRequest(path, options = {}) {
    const { token, ...requestOptions } = options
    const headers = new Headers(requestOptions.headers)
    if (requestOptions.body) {
        headers.set('Content-Type', 'application/json')
    }
    if (token) {
        headers.set('Authorization', `Bearer ${token}`)
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        ...requestOptions,
        headers,
    })
    if (response.status === 204) {
        return null
    }

    const responseText = await response.text()
    let body
    try {
        body = responseText ? JSON.parse(responseText) : null
    } catch {
        body = null
    }
    if (!response.ok) {
        const detail = typeof body?.detail === 'string' ? body.detail : response.statusText
        throw new Error(detail || `Request failed (${response.status})`)
    }
    if (responseText && body === null) {
        throw new Error('The server returned an unreadable response.')
    }
    return body
}

function displayRecordList(items, missingFields, field) {
    if (items.length) {
        return items.join(', ')
    }
    return missingFields.includes(field) ? 'Not available in record' : 'None recorded'
}

function ClinicianWorkspace() {
    const [token, setToken] = useState('')
    const [role, setRole] = useState('')
    const [username, setUsername] = useState('')
    const [password, setPassword] = useState('')
    const [patients, setPatients] = useState([])
    const [selectedPatientId, setSelectedPatientId] = useState('')
    const [patientSummary, setPatientSummary] = useState(null)
    const [symptoms, setSymptoms] = useState('')
    const [sessionId, setSessionId] = useState('')
    const [suggestions, setSuggestions] = useState(null)
    const [feedback, setFeedback] = useState({})
    const [error, setError] = useState('')
    const [busy, setBusy] = useState(false)
    const [feedbackBusyId, setFeedbackBusyId] = useState('')

    async function handleLogin(event) {
        event.preventDefault()
        setError('')
        setBusy(true)
        try {
            const result = await apiRequest('/auth/login', {
                method: 'POST',
                body: JSON.stringify({ username, password }),
            })
            const patientList = await apiRequest('/patients', { token: result.access_token })
            setToken(result.access_token)
            setRole(result.role)
            setPassword('')
            setPatients(patientList)
        } catch (requestError) {
            setError(requestError.message)
        } finally {
            setBusy(false)
        }
    }

    function handleLogout() {
        setToken('')
        setRole('')
        setUsername('')
        setPassword('')
        setPatients([])
        setSelectedPatientId('')
        setPatientSummary(null)
        setSymptoms('')
        setSessionId('')
        setSuggestions(null)
        setFeedback({})
        setError('')
    }

    async function handlePatientChange(event) {
        const patientId = event.target.value
        setSelectedPatientId(patientId)
        setPatientSummary(null)
        setSessionId('')
        setSymptoms('')
        setSuggestions(null)
        setFeedback({})
        setError('')
        if (!patientId) {
            return
        }

        setBusy(true)
        try {
            const summary = await apiRequest(
                `/patients/${encodeURIComponent(patientId)}/summary`,
                { token },
            )
            setPatientSummary(summary)
        } catch (requestError) {
            setError(requestError.message)
        } finally {
            setBusy(false)
        }
    }

    async function handleAssessmentSubmit(event) {
        event.preventDefault()
        if (!selectedPatientId || !patientSummary || symptoms.trim().length < 3) {
            setError('Select a patient and enter at least 3 characters of symptoms.')
            return
        }

        setError('')
        setBusy(true)
        try {
            let activeSessionId = sessionId
            if (!activeSessionId) {
                const session = await apiRequest('/sessions', {
                    method: 'POST',
                    token,
                    body: JSON.stringify({ patient_id: selectedPatientId }),
                })
                activeSessionId = session.id
                setSessionId(activeSessionId)
            }

            const result = await apiRequest(
                `/sessions/${encodeURIComponent(activeSessionId)}/symptoms`,
                {
                    method: 'POST',
                    token,
                    body: JSON.stringify({ text: symptoms.trim() }),
                },
            )
            setSuggestions(result)
            setFeedback({})
        } catch (requestError) {
            setError(requestError.message)
        } finally {
            setBusy(false)
        }
    }

    async function handleFeedback(considerationId, accepted) {
        setError('')
        setFeedbackBusyId(considerationId)
        try {
            await apiRequest(`/sessions/${encodeURIComponent(sessionId)}/feedback`, {
                method: 'POST',
                token,
                body: JSON.stringify({ consideration_id: considerationId, accepted }),
            })
            setFeedback((current) => ({
                ...current,
                [considerationId]: accepted ? 'Accepted' : 'Not accepted',
            }))
        } catch (requestError) {
            setError(requestError.message)
        } finally {
            setFeedbackBusyId('')
        }
    }

    if (!token) {
        return (
            <main className="app-shell">
                <header className="app-header">
                    <p className="eyebrow">Clinical decision support · Demo</p>
                    <h1>Clinician workspace</h1>
                    <p>Sign in with a demo clinician account to review synthetic patient cases.</p>
                </header>
                <form className="panel login-panel" onSubmit={handleLogin}>
                    <h2>Clinician sign in</h2>
                    <label htmlFor="clinician-username">Username</label>
                    <input
                        autoComplete="username"
                        id="clinician-username"
                        required
                        value={username}
                        onChange={(event) => setUsername(event.target.value)}
                    />
                    <label htmlFor="clinician-password">Password</label>
                    <input
                        autoComplete="current-password"
                        id="clinician-password"
                        type="password"
                        required
                        value={password}
                        onChange={(event) => setPassword(event.target.value)}
                    />
                    {error && <p className="error-message" role="alert">{error}</p>}
                    <button className="primary-button" disabled={busy} type="submit">
                        {busy ? 'Signing in…' : 'Sign in'}
                    </button>
                    <p className="demo-hint">
                        Use the nurse or physician demo credentials listed in the backend setup guide.
                    </p>
                </form>
                <p className="safety-note">
                    Synthetic data only. Do not enter real patient information.
                </p>
            </main>
        )
    }

    return (
        <main className="app-shell">
            <header className="app-header app-header-row">
                <div>
                    <p className="eyebrow">Clinical decision support · Demo</p>
                    <h1>Clinician workspace</h1>
                </div>
                <div className="user-controls">
                    <span>{username} · {role}</span>
                    <button className="secondary-button" onClick={handleLogout} type="button">
                        Sign out
                    </button>
                </div>
            </header>

            <p className="safety-note">
                Synthetic data only. Suggestions are not diagnoses; clinician judgment is required.
            </p>
            {error && <p className="error-message page-error" role="alert">{error}</p>}

            <section className="panel">
                <h2>1. Select a patient</h2>
                <label htmlFor="clinician-patient">Demo patient</label>
                <select
                    id="clinician-patient"
                    value={selectedPatientId}
                    onChange={handlePatientChange}
                    disabled={busy}
                >
                    <option value="">Choose a patient…</option>
                    {patients.map((patient) => (
                        <option key={patient.id} value={patient.id}>
                            {patient.name} ({patient.id})
                        </option>
                    ))}
                </select>

                {patientSummary && (
                    <div className="patient-summary">
                        <h3>{patientSummary.name}</h3>
                        <p>
                            {patientSummary.age !== null && patientSummary.age !== undefined
                                ? `${patientSummary.age} years old`
                                : 'Age not provided'}
                            {patientSummary.gender ? ` · ${patientSummary.gender}` : ''}
                        </p>
                        <dl className="history-grid">
                            <div>
                                <dt>Conditions</dt>
                                <dd>{displayRecordList(
                                    patientSummary.conditions,
                                    patientSummary.missing_fields,
                                    'conditions',
                                )}</dd>
                            </div>
                            <div>
                                <dt>Medications</dt>
                                <dd>{displayRecordList(
                                    patientSummary.medications,
                                    patientSummary.missing_fields,
                                    'medications',
                                )}</dd>
                            </div>
                            <div>
                                <dt>Allergies</dt>
                                <dd>{displayRecordList(
                                    patientSummary.allergies,
                                    patientSummary.missing_fields,
                                    'allergies',
                                )}</dd>
                            </div>
                            <div>
                                <dt>Recent encounters</dt>
                                <dd>{displayRecordList(
                                    patientSummary.recent_encounters,
                                    patientSummary.missing_fields,
                                    'recent_encounters',
                                )}</dd>
                            </div>
                        </dl>
                    </div>
                )}
            </section>

            <form className="panel" onSubmit={handleAssessmentSubmit}>
                <h2>2. Describe symptoms</h2>
                <label htmlFor="clinician-symptoms">Current symptoms</label>
                <textarea
                    id="clinician-symptoms"
                    minLength={3}
                    maxLength={4000}
                    placeholder="Enter the symptoms reported for this patient"
                    required
                    rows={5}
                    value={symptoms}
                    onChange={(event) => setSymptoms(event.target.value)}
                />
                <div className="form-footer">
                    <span>{symptoms.length}/4000 characters</span>
                    <button
                        className="primary-button"
                        disabled={busy || !patientSummary}
                        type="submit"
                    >
                        {busy ? 'Working…' : 'Get clinical suggestions'}
                    </button>
                </div>
            </form>

            {suggestions && (
                <section className="panel suggestions-panel" aria-labelledby="suggestions-heading">
                    <h2 id="suggestions-heading">3. Suggestions to consider</h2>
                    <p className="disclaimer">{suggestions.disclaimer}</p>

                    {suggestions.red_flags.length > 0 && (
                        <div className="red-flags">
                            <h3>Warning signs</h3>
                            <ul>
                                {suggestions.red_flags.map((flag, index) => (
                                    <li key={`${index}-${flag}`}>{flag}</li>
                                ))}
                            </ul>
                        </div>
                    )}

                    {suggestions.considerations.length > 0 ? (
                        <div className="considerations">
                            {suggestions.considerations.map((item) => (
                                <article className="consideration-card" key={item.id}>
                                    <div className="consideration-heading">
                                        <h3>{item.condition}</h3>
                                        <span className={`likelihood likelihood-${item.likelihood}`}>
                                            {item.likelihood} likelihood
                                        </span>
                                    </div>
                                    <p>{item.rationale}</p>
                                    {item.supporting_findings.length > 0 && (
                                        <>
                                            <h4>Supporting findings</h4>
                                            <ul>
                                                {item.supporting_findings.map((finding, index) => (
                                                    <li key={`${index}-${finding}`}>{finding}</li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                    {item.suggested_next_steps.length > 0 && (
                                        <>
                                            <h4>Suggested next steps</h4>
                                            <ul>
                                                {item.suggested_next_steps.map((step, index) => (
                                                    <li key={`${index}-${step}`}>{step}</li>
                                                ))}
                                            </ul>
                                        </>
                                    )}
                                    {item.guideline_refs.length > 0 && (
                                        <p className="guideline-refs">
                                            Guideline references: {item.guideline_refs.join(', ')}
                                        </p>
                                    )}
                                    <div className="feedback-controls">
                                        {feedback[item.id] ? (
                                            <span className="feedback-recorded">
                                                Feedback recorded: {feedback[item.id]}
                                            </span>
                                        ) : (
                                            <>
                                                <button
                                                    className="secondary-button"
                                                    disabled={feedbackBusyId === item.id}
                                                    onClick={() => handleFeedback(item.id, true)}
                                                    type="button"
                                                >
                                                    Accept
                                                </button>
                                                <button
                                                    className="secondary-button"
                                                    disabled={feedbackBusyId === item.id}
                                                    onClick={() => handleFeedback(item.id, false)}
                                                    type="button"
                                                >
                                                    Do not accept
                                                </button>
                                            </>
                                        )}
                                    </div>
                                </article>
                            ))}
                        </div>
                    ) : (
                        <p>No considerations were returned. Review the symptoms and use your clinical judgment.</p>
                    )}

                    {suggestions.follow_up_questions.length > 0 && (
                        <div className="follow-up">
                            <h3>Follow-up questions</h3>
                            <ul>
                                {suggestions.follow_up_questions.map((question, index) => (
                                    <li key={`${index}-${question}`}>{question}</li>
                                ))}
                            </ul>
                        </div>
                    )}
                </section>
            )}
        </main>
    )
}

export default ClinicianWorkspace
