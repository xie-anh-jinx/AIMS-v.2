import os
import sys
import httpx
import bcrypt
import random
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, User, AcademicRecord

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

token = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiMDZjZTI3ZjAzYzUxOWZiNzk5ZjdlZTVlMzdjNzg0MGRjMmUwOWNmZjFkYjBiM2ZlNTNiOGVjZmFlNGM1NWEyZmZkYzUzYjc1ODNjZGU3MGIiLCJpYXQiOjE3ODQ5NzkxNDMuNjYzNDEyLCJuYmYiOjE3ODQ5NzkxNDMuNjYzNDE1LCJleHAiOjE3ODU0MTExNDMuNjU3MzQ1LCJzdWIiOiI4ODQyNSIsInNjb3BlcyI6WyIqIl19.BJJwWCpsw0ZLqTVtqvdy6ZyeTTbN3aYFbjr6D_ukeT0zjNjm5E0f0AJe8Y9lfAV9PwM-KxMCW6xvKWC0J-LxTZ99pWWGhMqDIAYbR1paj3KN5ggEtWYo0upZ1X8J9-kEk5CK2HaC9oRWCSjtV-QgfXW_SdEQi4aa68pevF1rMJlgsXBCqKKTnFYDn48Lb6NILBHnxgVbrBpIoGH3wZQOMegDwG-9zHXXLJyO0oi_uV2PmZPH_ovyOB3mHj7pohX0ZybHhkT_71QvYKnieW-Pzra7uwv_Aaet0V2jmDj6PSX6fGjZy-ihmoqIWcd2KDD18tfqldd0hRLmxYzKtzfOOBUP2GlfFiDVH71BnRLbN7zKaJUkIty-yN5f_CGGjaM75VleKNZ4nvJLA3XKg-_RVbjttvxoGV8i02q6wQbyhypK_HkfSFB6Acelcisl7-GohTghmXc7sBkzUblY6Oeu09zGn54XrVjFaQ0wLLplbzH2j3_qE8jqd-E7wYu93TRyctHrbsJApVILVefwpeBGVhtbkxVWRNR0P7iAaFlnNc_0fai7-j3SL6BD8VDUdfvCSwKYRyKqnsNeZiGrNbLnOeyA8c6hdugn_p-_AjlYSb4eSIJoJKDz3TV8cK6M7I7-QchdvYEeGBMKbjWd2RYcXQbatocb_9AdXELBEQ7-cy0"
headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"

STATUS_MAP = {
    "A": "Aktif",
    "C": "Cuti",
    "L": "Lulus",
    "D": "Drop Out",
    "K": "Keluar",
    "P": "Pindah",
    "N": "Non Aktif",
}

db = SessionLocal()

print("Hashing default password...")
hashed_pw = get_password_hash("password123")

count_real = 0
client = httpx.Client(timeout=30)
pid = 254
prodi_name = "Pariwisata"

print(f"Fetching students for {prodi_name} (ID: {pid})...")
url = f"{NEOSIA_BASE}/api/admin/mahasiswa?filters[id_prodi]={pid}&filters[angkatan]=2026"
try:
    res = client.get(url, headers=headers)
    if res.status_code == 200:
        data = res.json()
        mahasiswas = data.get("mahasiswas", [])
        print(f"  Found {len(mahasiswas)} students.")
        for m in mahasiswas:
            nim = m.get("nim")
            if not nim: continue
            
            if db.query(Student).filter(Student.nim == nim).first():
                continue
                
            u = User(username=nim, hashed_password=hashed_pw, role="STUDENT")
            db.add(u)
            db.flush()
            
            kode_status = m.get("kode_status", "A")
            status = STATUS_MAP.get(kode_status, "Aktif")
            nama = m.get("nama_mahasiswa", f"Mhs {nim}")
            email = f"{nim.lower()}@student.unhas.ac.id"
            wa = m.get("whatsapp", "")
            
            s = Student(
                user_id=u.id,
                nim=nim,
                nama=nama,
                angkatan=2026,
                semester=1,
                prodi=prodi_name,
                email=email,
                nomor_whatsapp=wa,
                status=status
            )
            db.add(s)
            db.flush()
            
            ar = AcademicRecord(
                student_id=s.id,
                semester=1,
                ipk=round(3.0 + random.uniform(-0.5, 0.9), 2),
                sks=20,
                status="Aman"
            )
            db.add(ar)
            db.flush()
            count_real += 1
        db.commit() 
    else:
        print(f"  Failed for {prodi_name}: {res.status_code}")
except Exception as e:
    print(f"  Exception for {prodi_name}: {e}")
    db.rollback()

print(f"Successfully added {count_real} REAL students for {prodi_name} class of 2026.")
db.close()
