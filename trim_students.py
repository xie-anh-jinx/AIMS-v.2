import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade, ConsultationLog, NotificationLog, User
from sqlalchemy import or_, and_

db = SessionLocal()

print("Penyusutan Data Range Angkatan [ < 2019 OR > 2025 ]...")

# 1. Cari Mahasiswa Out of Bounds
students_to_delete = db.query(Student).filter(
    or_(Student.angkatan < 2019, Student.angkatan > 2025)
).all()

student_ids = [s.id for s in students_to_delete]
user_ids = [s.user_id for s in students_to_delete if s.user_id]

print(f"Menemukan {len(student_ids)} mahasiswa yang tidak sesuai syarat angkatan 2019-2025.")

if len(student_ids) > 0:
    # 2. Hapus Relasi Ketergantungan (Foreign Keys)
    deleted_records = db.query(AcademicRecord).filter(AcademicRecord.student_id.in_(student_ids)).delete(synchronize_session=False)
    deleted_grades = db.query(Grade).filter(Grade.student_id.in_(student_ids)).delete(synchronize_session=False)
    deleted_cons = db.query(ConsultationLog).filter(ConsultationLog.student_id.in_(student_ids)).delete(synchronize_session=False)
    deleted_notifs = db.query(NotificationLog).filter(NotificationLog.student_id.in_(student_ids)).delete(synchronize_session=False)
    
    # 3. Hapus Akun User (jika student punya user_id)
    if len(user_ids) > 0:
        db.query(User).filter(User.id.in_(user_ids)).delete(synchronize_session=False)
    
    # 4. Hapus Baris Mahasiswa Itu Sendiri
    deleted_students = db.query(Student).filter(Student.id.in_(student_ids)).delete(synchronize_session=False)
    
    db.commit()
    print(f"Berhasil membersihkan: {deleted_students} Mahasiswa, {deleted_records} Rekam Akademik, {deleted_grades} Nilai MK.")
else:
    print("Database sudah bersih, tidak ada mahasiswa lawas/asumsi yang terdeteksi.")
