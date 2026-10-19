import { useState } from 'react'
import './App.css'

function App() {
    const [assessmentStarted, setAssessmentStarted] = useState(false)
    const [birthday, setBirthday] = useState('')
    const [symptoms, setSymptoms] = useState('')
    const [patientName, setPatientName] = useState('')
    const [severity, setSeverity] = useState('')
    const [error, setError] = useState('')

    return (
        <div>
            <h1>Welcome to the Medicinal Magician!</h1>

            <h2>Patient Information: </h2>

            <div>
                <label>Patient Name</label>
                <input
                placeholder="Enter Patient Name"
                value={patientName}
                onChange={(event) => setPatientName(event.target.value)}
                />
                <label>Date of Birth</label>
                <input
                type="date"
                value={birthday}
                onChange={(event) => setBirthday(event.target.value)}
                />
            </div>

            <h2>Medical History</h2>

            <div>
                <p>Previous Conditions: Not provided</p>
                <p>Current Medications: Not provided</p>
                <p>Allergies: Not provided</p>
            </div>

            <h2>Current Symptoms</h2>

            <textarea
                placeholder="Tell us what you're experiencing..."
                value={symptoms}
                onChange={(event) => setSymptoms(event.target.value)}
            />
                <input 
                 type="radio"
                 name="Pain Severity"
                 value="Mild"
                 onChange={(event) => setSeverity(event.target.value)}
                />
                <label>Mild</label>
                <input 
                type="radio"
                name="Pain Severity"
                value="Moderate"
                onChange={(event) => setSeverity(event.target.value)} 
                />
                <label>Moderate</label>
                <input
                type="radio"
                name="Pain Severity"
                value="Severe"
                onChange={(event) => setSeverity(event.target.value)}
                />
                <label>Severe</label>

            <br />

            <button onClick={() => {
    if (patientName === '') {
        setError('Please put in the patient name.')
    }
    else if (birthday === '') {
        setError("Please enter the patient's date of birth")
    }
    else if (symptoms === '') {
        setError('Please type out the symptoms.')
    }
    else if (severity === '') {
        setError('Please select a severity.')
    }
    else {
        setAssessmentStarted(true)
        setError('')
    }
}}>
    Begin Assessment
</button>
<button onClick={() => {
    setPatientName('')
    setBirthday('')
    setSymptoms('')
    setSeverity('')
    setError('')
    setAssessmentStarted(false)
}}>
    Reset Assessment
</button>

{error}

            {assessmentStarted && (
                <section className="assessment-card" aria-labelledby="assessment-heading">
                    <h2 id="assessment-heading">Assessment summary</h2>
                    <p className="assessment-status">
                        Your responses are ready for provider review.
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
                    >
                        Review or edit responses
                    </button>
                </section>
            )}
    </div>
    )
}

export default App