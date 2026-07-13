from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade

db = SessionLocal()
records = db.query(AcademicRecord).filter(AcademicRecord.ipk == 0.0).all()
updated_count = 0

for record in records:
    # Calculate IPK from Grades for this student up to this semester
    grades = db.query(Grade).filter(Grade.student_id == record.student_id).all()
    if not grades:
        continue
    
    total_bobot_sks = 0.0
    total_sks = 0
    for g in grades:
        if g.course and g.course.sks:
            total_bobot_sks += (g.bobot * g.course.sks)
            total_sks += g.course.sks
            
    if total_sks > 0:
        new_ipk = total_bobot_sks / total_sks
        if new_ipk > 0:
            record.ipk = new_ipk
            updated_count += 1

db.commit()
print(f"Berhasil memperbarui nilai IPK yang kosong/0.0 pada tabel riwayat akademik untuk {updated_count} mahasiswa.")

