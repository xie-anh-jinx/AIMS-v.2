import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, Grade

db = SessionLocal()

print("Mulai Rollback Database (Menghapus Data Se-Fakultas)...")

# Ambil semua student IDs yang punya riwayat Grades
students_with_grades = db.query(Grade.student_id).distinct().all()
valid_ids = [r[0] for r in students_with_grades]

# Hitung semua mahasiswa yang TIDAK ada di dalam valid_ids
invader_students = db.query(Student).filter(Student.id.not_in(valid_ids)).all()

count = len(invader_students)
if count > 0:
    print(f"Ditemukan {count} data mahasiswa dari ekstraksi 4 jam terakhir (se-Fakultas). Membuang...")
    db.query(Student).filter(Student.id.not_in(valid_ids)).delete(synchronize_session=False)
    db.commit()
    print("Database kembali bersih seperti 8 jam lalu! Total mahasiswa aktif di tabel AIMS kini hanya menyisakan data murni yang berjejak nilai.")
else:
    print("Database sudah berada dalam mode murni.")
