import { useState } from 'react'
import './App.css'

function App() {
    const [assessmentStarted, setAssessmentStarted] = useState(false)

    return (
        <div>
            <h1>Welcome to the Medicinal Magician!</h1>
            <h2>Patient Information: </h2>
            <div>
                <p>Patient: Your Mom</p>
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
      />

      <br />

      <button onClick={() => setAssessmentStarted(true)}>
        Begin Assessment
        </button>

        {assessmentStarted && (
    <p>Assessment started!</p>
        )
}
   </div> 
    );
} 
export default App;