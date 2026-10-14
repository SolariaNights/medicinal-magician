# Medical Magician EHR/EMR intergration layer code
#
# PURPOSE
# Provide patient history to backend.
#
# FIRST VERSION
# Use fictional patient records stored locally in JSON file.
# Accept a test patient ID and find the matching record.
# Return the patient's conditions, medications, and allergies.
# Report when the requested patient cannot be found.
#
# INPUT
# A unique test patient ID, such as "test-001".
#
# OUTPUT
# A Python dictionary containing the patient ID and their
# conditions, medications, and allergies.
# returns None when no patient matches
#
# OUTSIDE THIS VERSION'S SCOPE
# Connecting to real hospital systems or using real patient records.
# Making diagnoses or generating treatment recommendations.
# Building the frontend or the overall backend.
# Changing or writing information back to medical records.
#
# SUCCESS CRITERIA
# A known patient ID returns the correct fictional record.
# An unknown patient ID produces a clear "patient not found" result.
# Missing information is not treated as proof of no medical issues.
# The backend teammate can call our function and use its result.
#
# LATER MILESTONE
# Connect to a FHIR test system to retrieve fictional patient records.
# Agree with the backend teammate on the final output format.

##########################################################################
import json
from pathlib import Path

patient_file = Path(__file__).parent / "patients.json"
###################################################3
# Data structure
# Data source: patients.json
# Contains fictional patient records for the local integration prototype.
# Each record has a unique patient ID and lists of conditions,
# allergies, and medications.
# Used by get_patient() to look up a patient by ID.
# Contains no real patient information.
###########################################################

# Try-except for file error messaging
try:
    # Open up json file for use 
    with open(patient_file, "r") as file:
        patients = json.load(file)
except FileNotFoundError:
    # prints error message and prevents program
    # from trying to seach records it cant load
    print("Patient file not Found.")
    raise        

##########################################
# Function: get_patient
# Input: Patient id
# Purpose: Takes input id and returns a dictionary with all patient
#          information stored in JSON file
#          (in this case just allergies, conditions, and medications)
#           
# Output: Patient Dictionary or None if no match


def get_patient(requested_id):
    # clean text for input errors
    requested_id = requested_id.strip()
    for patient in patients:
        if requested_id == patient["id"]:
            return patient
    return None
#######################################################
if __name__ == "__main__":
    # Ask for patient ID and plug into get_patient function 
    requested_id = input("Enter patient ID: ")
    # Save patient dictionary into result
    result = get_patient(requested_id)
    # print out based on result(none/matching id)
    if result is None:
        print("Patient not found")
    else:
        print("Patient conditions", result["conditions"])
        print("Patient allergies", result["allergies"])
        print("Patient medications", result["medications"])
