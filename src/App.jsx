import { useState } from 'react'
import heroImg from './assets/hero.png'
import reactLogo from './assets/react.svg'
import viteLogo from './assets/vite.svg'
import './App.css'

function App() {
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
                    <p>Previous conditions...</p>
                    <p>Current medications...</p>
                    <p>Allergies...</p>
                </div>

            <h2>Current Symptoms</h2>

        <textarea
        placeholder="Tell us what you're experiencing..."
      />

      <br />

      <button>Begin Assessment</button>
        </div>
    );
}
export default App;