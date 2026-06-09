from pydantic import BaseModel, Field
from typing import Optional
import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from base_extractor import extract_structured

class Experience(BaseModel):
    company: str
    role: str
    start_date: str
    end_date: Optional[str] = None
    key_responsibilities: list[str]

class Education(BaseModel):
    institution: str
    degree: str
    field: str
    graduation_year: int
    gpa: Optional[float] = None

class Resume(BaseModel):
    full_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    location: Optional[str] = None
    total_experience_years: float
    skills: list[str]
    experience: list[Experience]
    education: list[Education]
    seniority_level: str = Field(description="junior, mid, senior, or lead")

SAMPLE_RESUME = """
MUHAMMAD ALI KHAN
Email: ali.khan@email.com | Phone: +92-300-1234567
Location: Lahore, Pakistan

EXPERIENCE:
DataTech Solutions — Senior Python Engineer (Mar 2022 - Present)
- Led development of ML pipeline processing 1M+ records daily
- Built REST APIs serving 50k requests/day using FastAPI

EDUCATION:
University of Engineering & Technology, Lahore
B.Sc Computer Science — 2019 — GPA: 3.7/4.0

SKILLS: Python, FastAPI, Django, PostgreSQL, Docker, AWS, Machine Learning
"""

if __name__ == "__main__":
    import json
    print("⏳ Extracting Resume...")
    result = extract_structured(SAMPLE_RESUME, Resume, "resume")
    print(json.dumps(result, indent=2))

    with open("extracted_resume.pdf", "w") as f:
           json.dump(result, f)