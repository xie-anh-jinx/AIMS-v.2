from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord
from sqlalchemy import func

db = SessionLocal()
subq = db.query(
    AcademicRecord.student_id,
    func.max(AcademicRecord.semester).label("max_semester")
).group_by(AcademicRecord.student_id).subquery()

students = db.query(
    Student.prodi,
    AcademicRecord.ipk,
    Student.status
).join(
    AcademicRecord,
    Student.id == AcademicRecord.student_id
).join(
    subq,
    (AcademicRecord.student_id == subq.c.student_id) & 
    (AcademicRecord.semester == subq.c.max_semester)
).filter(Student.status != 'Lulus').all()

prodi_counts = {}
for s in students:
    if s.prodi not in prodi_counts:
         prodi_counts[s.prodi] = {"merah": 0, "kuning": 0, "hijau": 0}
    ipk = s.ipk or 0.0
    if ipk < 2.0:
        prodi_counts[s.prodi]["merah"] += 1
    elif ipk < 2.75:
        prodi_counts[s.prodi]["kuning"] += 1
    else:
        prodi_counts[s.prodi]["hijau"] += 1

out = [{"prodi": k, "merah": v["merah"], "kuning": v["kuning"], "hijau": v["hijau"]} for k, v in prodi_counts.items()]
import json
print(json.dumps(out, indent=2))
