import os
from dotenv import load_dotenv
import requests

load_dotenv(".env")
from packages.database.connection import SessionLocal
from packages.database.models import Student

db = SessionLocal()
stud = db.query(Student).filter(Student.prodi.ilike("%jepang%"), Student.advisor_id.isnot(None)).first()

if stud:
    print(f"Testing student NIM: {stud.nim}")
    # Local API check
    # Without Token, I can bypass by querying DB directly just like the API does:
    from packages.database.models import AcademicRecord
    recs = db.query(AcademicRecord).filter(AcademicRecord.student_id == stud.id).all()
    print("Academic Records found:", len(recs))
    for r in recs:
        print(f"Sem: {r.semester}, SKS: {r.sks}, IPK: {r.ipk}")
else:
    print("Student not found")
