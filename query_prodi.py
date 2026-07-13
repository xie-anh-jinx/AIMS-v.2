from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, ProdiAdmin

db = SessionLocal()

print("--- Data Prodi di Tabel Mahasiswa ---")
student_prodis = db.query(Student.prodi).distinct().all()
for p in student_prodis:
    print(f"- {p[0]}")

print("\n--- Data Prodi di Tabel Dosen PA ---")
advisor_prodis = db.query(Advisor.prodi).distinct().all()
for p in advisor_prodis:
    print(f"- {p[0]}")

print("\n--- Data Prodi di Tabel Kaprodi (ProdiAdmin) ---")
admin_prodis = db.query(ProdiAdmin.prodi_name).distinct().all()
for p in admin_prodis:
    print(f"- {p[0]}")

