import os
import sys
import random
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, User, AcademicRecord
import bcrypt

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

hashed_pw = get_password_hash("password123")

PRODIS = [
    "Sastra Indonesia",
    "Sastra Inggris",
    "Sastra Perancis",
    "Sastra Mandarin",
    "Sastra Jepang",
    "Sastra Arab",
    "Ilmu Sejarah",
    "Arkeologi",
    "Sastra Daerah"
]

NAMES = ["Ahmad", "Budi", "Siti", "Andi", "Nurul", "Putra", "Putri", "Dewi", "Rina", "Reza", "Fajar", "Dina", "Hendra", "Ayu", "Lestari"]

db = SessionLocal()

base_nim = 2026401001

count = 0
for prodi in PRODIS:
    # 20 students per prodi to make it impactful
    for i in range(1, 21): 
        nim = str(base_nim)
        base_nim += 1
        
        # Check if exists
        existing = db.query(Student).filter(Student.nim == nim).first()
        if existing:
            continue
            
        u = User(username=nim, hashed_password=hashed_pw, role="STUDENT")
        db.add(u)
        db.commit()
        
        nama = f"{random.choice(NAMES)} {random.choice(NAMES)} {i}"
        
        s = Student(
            user_id=u.id,
            nim=nim,
            nama=nama,
            angkatan=2026,
            semester=1,
            prodi=prodi,
            email=f"{nim}@mhs.fib.ac.id",
            nomor_whatsapp=f"0812{nim}",
            status="Aktif"
        )
        db.add(s)
        db.commit()
        
        ipk_val = round(3.0 + random.uniform(-1.0, 1.0), 2)
        status_val = "Aman"
        if ipk_val < 2.0:
            status_val = "Aman"
        elif ipk_val < 2.75:
            status_val = "Aman"
            
        ar = AcademicRecord(
            student_id=s.id,
            semester=1,
            ipk=ipk_val,
            sks=20,
            status=status_val
        )
        db.add(ar)
        db.commit()
        count += 1

print(f"Successfully added {count} new students for FIB class of 2026.")
db.close()
