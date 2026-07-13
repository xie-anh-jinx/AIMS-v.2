from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade

db = SessionLocal()
fatmawati = db.query(Student).filter(Student.nim == "F011231001").first()
record = db.query(AcademicRecord).filter(AcademicRecord.student_id == fatmawati.id).first()

grades = db.query(Grade).filter(Grade.student_id == fatmawati.id).all()
total_bobotsks = 0
total_sks = 0
for g in grades:
    if g.course and g.course.sks:
        total_bobotsks += g.bobot * g.course.sks
        total_sks += g.course.sks

print(f"B4 Update: fatmawati IPK={record.ipk}")
if total_sks > 0:
    record.ipk = total_bobotsks / total_sks
    print(f"Calculated IPK: {record.ipk}")

db.commit()

