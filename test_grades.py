from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade

db = SessionLocal()
student = db.query(Student).filter(Student.nim == "F011231001").first()
grades = db.query(Grade).filter(Grade.student_id == student.id).all()
print(f"Banyak grade untuk {student.nama} = {len(grades)}")
if len(grades) > 0:
    for g in grades[:3]:
        course_sks = g.course.sks if g.course else None
        print(f"Grade: {g.grade}, bobot: {g.bobot}, course_id: {g.course_id}, sks: {course_sks}")
