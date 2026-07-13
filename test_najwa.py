import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord
import json

db = SessionLocal()
st = db.query(Student).filter(Student.nim == "F031251018").first()
if st:
    print(f"Student: {st.nama} ({st.nim}) - {st.prodi}")
    recs = db.query(AcademicRecord).filter(AcademicRecord.student_id == st.id).all()
    for r in recs:
        print(f"Record: IPK {r.ipk}, SKS {r.sks}")
else:
    print("Student not found.")
