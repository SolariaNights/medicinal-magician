import { useState } from 'react'
import './App.css'

function App() {
    const [assessmentStarted, setAssessmentStarted] = useState(false)
    const [symptoms, setSymptoms] = useState('')
    const [patientName, setPatientName] = useState('')

    return (
        <div>
            <h1>Welcome to the Medicinal Magician!</h1>

            <h2>Patient Information: </h2>

            <div>
                <input
                placeholder="Enter Patient Name"
                value={patientName}
                onChange={(event) => setPatientName(event.target.value)}
                />
                <p>Date of Birth: 06/09/1969</p>
            </div>

            <h2>Medical History</h2>

            <div>
                <p>Previous Conditions: None listed</p>
                <p>Current Medications: None listed</p>
                <p>Allergies: None listed</p>
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
                value2="Moderate"
                value3="Severe"
            />

            <br />

            <button onClick={() => setAssessmentStarted(true)}>
                Begin Assessment
            </button>

            {assessmentStarted && (
            <div>
            <h2>Assessment</h2>
            <p>Symptoms entered: {symptoms}</p>
            <p>Thank you. Your information has been recorded.</p>
        </div>)
}
    </div>
    )
}

export default App