from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord
db = SessionLocal()
student = db.query(Student).filter(Student.nim == "F011231001").first()
print(f"Student: {student.nama} (ID: {student.id})")
records = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).all()
for r in records:
    print(f"Semester {r.semester}: IPS={r.ips}, IPK={r.ipk}")
