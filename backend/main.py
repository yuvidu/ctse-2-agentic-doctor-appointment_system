from fastapi import FastAPI

app = FastAPI()

SPECIALIZATIONS = [
    "Cardiology",
    "Dermatology",
    "Dentistry",
    "Neurology",
    "Orthopedics",
    "Pediatrics",
    "General Medicine",
    "Gynecology",
    "Psychiatry",
    "Oncology",
    "Endocrinology",
    "Gastroenterology",
    "Pulmonology",
    "Rheumatology",
    "Urology",
    "Ophthalmology",
    "ENT (Ear, Nose, Throat)",
    "Nephrology",
    "Hematology",
    "Anesthesiology",
    "Radiology",
    "Pathology",
    "Surgery (General)",
    "Neurosurgery",
    "Cardiothoracic Surgery"
]

@app.get("/")
def home():
    return {"message": "Backend is running"}

@app.get("/specializations")
def get_specializations():
    return {"data": SPECIALIZATIONS}