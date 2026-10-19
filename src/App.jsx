import { useState } from 'react'
import ClinicianWorkspace from './ClinicianWorkspace'
import './App.css'

function App() {
    const [activeScreen, setActiveScreen] = useState('assessment')

    return (
        <div>
            <nav className="screen-switcher" aria-label="Application screens">
                <button
                    aria-current={activeScreen === 'assessment' ? 'page' : undefined}
                    className={activeScreen === 'assessment' ? 'active' : ''}
                    onClick={() => setActiveScreen('assessment')}
                    type="button"
                >
                    Patient assessment
                </button>
                <button
                    aria-current={activeScreen === 'clinician' ? 'page' : undefined}
                    className={activeScreen === 'clinician' ? 'active' : ''}
                    onClick={() => setActiveScreen('clinician')}
                    type="button"
                >
                    Clinician workspace
                </button>
            </nav>
            <div hidden={activeScreen !== 'assessment'}>
                <PatientAssessment />
            </div>
            <div hidden={activeScreen !== 'clinician'}>
                <ClinicianWorkspace />
            </div>
        </div>
    )
}

function PatientAssessment() {
    const [assessmentStarted, setAssessmentStarted] = useState(false)
    const [birthday, setBirthday] = useState('')
    const [symptoms, setSymptoms] = useState('')
    const [patientName, setPatientName] = useState('')
    const [severity, setSeverity] = useState('')
    const [error, setError] = useState('')

    function handleAssessmentSubmit() {
        if (!patientName.trim()) {
            setError('patientName')
        } else if (!birthday) {
            setError('birthday')
        } else if (!symptoms.trim()) {
            setError('symptoms')
        } else if (!severity) {
            setError('severity')
        } else {
            setError('')
            setAssessmentStarted(true)
        }
    }

    function updateField(setter, field) {
        return (event) => {
            setter(event.target.value)
            if (error === field) {
                setError('')
            }
        }
    }

    return (
        <main className="patient-assessment">
            <h1>Welcome to the Medicinal Magician!</h1>

            <h2>Patient Information</h2>

            <div>
                <label htmlFor="patient-name">Patient Name</label>
                <input
                    id="patient-name"
                    placeholder="Enter Patient Name"
                    value={patientName}
                    aria-invalid={error === 'patientName'}
                    aria-describedby={error === 'patientName' ? 'patient-name-error' : undefined}
                    onChange={updateField(setPatientName, 'patientName')}
                />
                {error === 'patientName' && (
                    <p id="patient-name-error" className="field-error" role="alert">
                        Please enter the patient name.
                    </p>
                )}
                <label htmlFor="birthday">Date of Birth</label>
                <input
                    id="birthday"
                    type="date"
                    value={birthday}
                    aria-invalid={error === 'birthday'}
                    aria-describedby={error === 'birthday' ? 'birthday-error' : undefined}
                    onChange={updateField(setBirthday, 'birthday')}
                />
                {error === 'birthday' && (
                    <p id="birthday-error" className="field-error" role="alert">
                        Please enter the patient's date of birth.
                    </p>
                )}
            </div>

            <h2>Medical History</h2>

            <div>
                <p>Previous Conditions: Not provided</p>
                <p>Current Medications: Not provided</p>
                <p>Allergies: Not provided</p>
            </div>

            <h2>Current Symptoms</h2>

            <label htmlFor="symptoms">Describe current symptoms</label>
            <textarea
                id="symptoms"
                placeholder="Tell us what you're experiencing..."
                value={symptoms}
                aria-invalid={error === 'symptoms'}
                aria-describedby={error === 'symptoms' ? 'symptoms-error' : undefined}
                onChange={updateField(setSymptoms, 'symptoms')}
            />
            {error === 'symptoms' && (
                <p id="symptoms-error" className="field-error" role="alert">
                    Please describe the symptoms.
                </p>
            )}
            <fieldset>
                <legend>Pain severity</legend>
                <input
                    type="radio"
                    id="severity-mild"
                    name="pain-severity"
                    value="Mild"
                    checked={severity === 'Mild'}
                    aria-describedby={error === 'severity' ? 'severity-error' : undefined}
                    onChange={updateField(setSeverity, 'severity')}
                />
                <label htmlFor="severity-mild">Mild</label>
                <input
                    type="radio"
                    id="severity-moderate"
                    name="pain-severity"
                    value="Moderate"
                    checked={severity === 'Moderate'}
                    aria-describedby={error === 'severity' ? 'severity-error' : undefined}
                    onChange={updateField(setSeverity, 'severity')}
                />
                <label htmlFor="severity-moderate">Moderate</label>
                <input
                    type="radio"
                    id="severity-severe"
                    name="pain-severity"
                    value="Severe"
                    checked={severity === 'Severe'}
                    aria-describedby={error === 'severity' ? 'severity-error' : undefined}
                    onChange={updateField(setSeverity, 'severity')}
                />
                <label htmlFor="severity-severe">Severe</label>
            </fieldset>
            {error === 'severity' && (
                <p id="severity-error" className="field-error" role="alert">
                    Please select a severity.
                </p>
            )}

            <br />

            <button onClick={handleAssessmentSubmit} type="button">
                Begin Assessment
            </button>
            <button onClick={() => {
                setPatientName('')
                setBirthday('')
                setSymptoms('')
                setSeverity('')
                setError('')
                setAssessmentStarted(false)
            }} type="button">
                Reset Assessment
            </button>

            {assessmentStarted && (
                <section className="assessment-card" aria-labelledby="assessment-heading">
                    <h2 id="assessment-heading">Assessment summary</h2>
                    <p className="assessment-status">
                        This is a preview only. Your responses are not saved or sent to a provider.
                    </p>
                    <dl className="assessment-details">
                        <div>
                            <dt>Patient name</dt>
                            <dd>{patientName}</dd>
                        </div>
                        <div>
                            <dt>Date of birth</dt>
                            <dd>{birthday}</dd>
                        </div>
                        <div>
                            <dt>Symptoms</dt>
                            <dd>{symptoms}</dd>
                        </div>
                        <div>
                            <dt>Severity</dt>
                            <dd>{severity}</dd>
                        </div>
                    </dl>
                    <button
                        className="assessment-edit-button"
                        onClick={() => setAssessmentStarted(false)}
                        type="button"
                    >
                        Review or edit responses
                    </button>
                </section>
            )}
        </main>
    )
}

export default App
