from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

db = SessionLocal()
fa = db.query(Student).filter(Student.nim == "F011231001").first()
records = db.query(AcademicRecord).filter(AcademicRecord.student_id == fa.id).order_by(AcademicRecord.semester).all()
for r in records:
    print(f"ID={r.id}, Semester={r.semester}, IPS={r.ips}, IPK={r.ipk}")
