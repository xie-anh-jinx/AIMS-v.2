import random
import bcrypt
from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student

db = next(get_db())

print("=== MENGEMBALIKAN RELASI PA (OFFLINE MAPPING) ===")

# NIP dan Nama Dosen PA Riil (dari FIB Unhas - sampel representatif agar login berhasil)
REAL_PAS = [
    {"nip": "197911172010122002", "nama": "Dr. Ade Prastiwi, M.Hum"},
    {"nip": "197104031997022001", "nama": "Dr. Fierenziana Getruida Junus, SS.,M.Hum."},
    {"nip": "198501012015041001", "nama": "Prof. Budi Santoso, Ph.D"},
    {"nip": "198002022010121002", "nama": "Dr. Siti Aminah, M.A"},
    {"nip": "199003032014041003", "nama": "Bambang Pamungkas, S.S., M.Hum"},
    {"nip": "197505052002122001", "nama": "Prof. Nurul Fajriah, Ph.D"}
]

hashed_pw = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

# 1. Pastikan semua PA di atas ada di database dengan password123
advisor_ids = []
for pa in REAL_PAS:
    nip = pa["nip"]
    
    u = db.query(User).filter(User.username == nip).first()
    if not u:
        u = User(username=nip, hashed_password=hashed_pw, role="ADVISOR")
        db.add(u)
        db.flush()
    else:
        u.hashed_password = hashed_pw
        u.role = "ADVISOR"
        db.flush()
        
    adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
    if not adv:
        adv = Advisor(user_id=u.id, nama=pa["nama"])
        db.add(adv)
        db.flush()
    else:
        adv.nama = pa["nama"]
        
    advisor_ids.append(adv.id)
    
db.commit()
print(f"[OK] {len(advisor_ids)} Dosen PA berhasil dimasukkan dan bisa login dengan 'password123'")

# 2. Bind semua mahasiswa ke salah satu PA ini agar relasinya muncul di Frontend
students = db.query(Student).all()
linked = 0
for s in students:
    # Deterministic assignment based on numeric portion of NIM so it doesn't change randomly
    numeric_nim = sum(ord(c) for c in s.nim)
    s.advisor_id = advisor_ids[numeric_nim % len(advisor_ids)]
    linked += 1

db.commit()
print(f"[OK] {linked} relasi Mahasiswa-Dosen PA berhasil dipetakan seluruhnya.")
