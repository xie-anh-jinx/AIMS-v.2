from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor

db = SessionLocal()
advisors = db.query(Advisor).filter(Advisor.prodi == None).all()
updated_count = 0

for adv in advisors:
    # Find any student advised by this advisor
    student = db.query(Student).filter(Student.advisor_id == adv.id).first()
    if student and student.prodi:
        adv.prodi = student.prodi
        updated_count += 1

db.commit()
print(f"Berhasil mengidentifikasi dan memperbarui set prodi untuk {updated_count} Dosen PA dari data mahasiswa bimbingan lokal mereka.")
