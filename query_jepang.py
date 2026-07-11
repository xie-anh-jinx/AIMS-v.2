import os
from dotenv import load_dotenv
load_dotenv(".env")
load_dotenv("plugins/academic-connector/.env", override=False)

from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

db = SessionLocal()
prodis = db.query(Student.prodi).distinct().all()
print("Distinct Prodi in DB:", [p[0] for p in prodis])

# Let's find students specifically in Sastra Jepang
jepang_students = db.query(Student).filter(Student.prodi.ilike("%jepang%")).all()
print(f"Total Mahasiswa Sastra Jepang: {len(jepang_students)}")

if jepang_students:
    # See how many have an advisor
    with_adv = [s for s in jepang_students if s.advisor_id is not None]
    print(f"Sastra Jepang Students with PA: {len(with_adv)}")
    
    # Get the unique PAs for them
    adv_ids = set(s.advisor_id for s in with_adv)
    print("\n--- Dosen PA Sastra Jepang yang terkumpul ---")
    for a_id in adv_ids:
        adv = db.query(Advisor).filter(Advisor.id == a_id).first()
        if adv:
            user = db.query(User).filter(User.id == adv.user_id).first()
            count = len([s for s in with_adv if s.advisor_id == adv.id])
            print(f"- [NIP: {user.username if user else 'Tidak ada'}] {adv.nama} (Mendampingi {count} mahasiswa)")
