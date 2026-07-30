import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, User, AcademicRecord

db = SessionLocal()

fake_students = db.query(Student).filter(Student.nim.like("2026401%")).all()
print(f"Found {len(fake_students)} fake students.")
for fs in fake_students:
    print(f"Deleting {fs.nim} - {fs.nama}")
    db.query(AcademicRecord).filter(AcademicRecord.student_id == fs.id).delete()
    u_id = fs.user_id
    db.delete(fs)
    db.flush()
    if u_id:
        db.query(User).filter(User.id == u_id).delete()
        db.flush()

db.commit()
print("Cleaned up remaining dummy students.")
db.close()
