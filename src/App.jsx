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
                <input
                placeholder="Enter Patient Name"
                value={patientName}
                onChange={(event) => setPatientName(event.target.value)}
                />
                <input
                placeholder="Enter Date of Birth"
                value={birthday}
                onChange={(event) => setBirthday(event.target.value)}
                />
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
    setAssessmentStarted(false)
}}>
    Reset Assessment
</button>

{error}

            {assessmentStarted && (
            <div>
            <h2>Assessment</h2>
            <p>Patient name: {patientName}</p>
            <p>Date of Birth: {birthday}</p>
            <p>Symptoms entered: {symptoms}</p>
            <p>Severity: {severity}</p>
            <p>Thank you. Your information has been recorded.</p>
        </div>)
}
    </div>
    )
}

export default App