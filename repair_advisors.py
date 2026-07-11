"""
repair_advisors.py
==================
"""
import os
import sys
import requests
import bcrypt
from dotenv import load_dotenv

# Load env variables FIRST
load_dotenv(".env")
load_dotenv("plugins/academic-connector/.env", override=False) # Only load neoSia creds, do not override DATABASE_URL

from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student

db = next(get_db())

print("=" * 60)
print("STEP 1: Generate bcrypt hash yang valid...")
raw_password = "password123"
hashed = bcrypt.hashpw(raw_password.encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

print("\nSTEP 2: Hapus advisor mockup...")
mockup_users = db.query(User).filter(
    User.role == "ADVISOR",
    User.username.like("PA_%")
).all()
deleted = 0
for u in mockup_users:
    adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
    if adv:
        # Unlink students first
        students = db.query(Student).filter(Student.advisor_id == adv.id).all()
        for s in students:
            s.advisor_id = None
        db.delete(adv)
    db.delete(u)
    deleted += 1
db.commit()
print(f"Deleted {deleted} mockup advisors.")

print("\nSTEP 3: Reset password semua Advisor ke 'password123'...")
advisors_left = db.query(User).filter(User.role == "ADVISOR").all()
for user in advisors_left:
    user.hashed_password = hashed
db.commit()
print(f"Updated {len(advisors_left)} advisor login accounts.")

print("\nSTEP 4: Mencoba ambil data PA dari NeoSIA...")
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"
username_env = os.getenv("ENV_PRODI_PAR_USER", "")
password_env = os.getenv("ENV_PRODI_PAR_PASS", "")

if not username_env:
    print("[SKIP] Tidak ada ENV_PRODI_PAR_USER. Lewati sinkronisasi NeoSIA.")
    sys.exit(0)

try:
    auth_payload = {"username": username_env, "password": password_env}
    print(f"Mengotentikasi akun {username_env} ke NeoSIA...")
    login_res = requests.post("https://backoffice.neosia.unhas.ac.id/api/auth/login", json=auth_payload, timeout=15)
    token = login_res.json().get("token") or login_res.json().get("access_token") if login_res.status_code == 200 else None
    
    if not token:
        login_res2 = requests.post(f"{NEOSIA_BASE}/api/auth/login", json=auth_payload, timeout=15)
        token = login_res2.json().get("token") or login_res2.json().get("access_token") if login_res2.status_code == 200 else None
    
    if not token:
        print("[SKIP] Tidak bisa login ke NeoSIA via API. Sinkronisasi PA dilewati.")
        sys.exit(0)

    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[is_used]=1", headers=headers, timeout=15)
    ps_data = ps_res.json()
    ps_arr = ps_data.get("prodiSemesters") or ps_data.get("data") or []
    print(f"[OK] Menemukan {len(ps_arr)} prodi_semester aktif.")
    
    advisor_map = {}
    total_pa = 0
    
    # Sort or pick realistic number
    for ps in ps_arr:
        idSem = ps.get("id") or ps.get("id_prodi_semester")
        if not idSem: continue
        
        pa_res = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
        pa_data = pa_res.json()
        
        pa_arr = (pa_data.get("penasihat_akademiks") or pa_data.get("penasihatAkademiks") or pa_data.get("data") or pa_data.get("items") or [])
        if not pa_arr: continue
        
        for pa in pa_arr:
            nip = str(pa.get("nip") or pa.get("id_pegawai") or pa.get("username") or "")
            if not nip: continue
            
            nama = pa.get("nama_dosen") or pa.get("nama") or pa.get("nama_pegawai") or f"Dosen {nip}"
            total_pa += 1
            
            u = db.query(User).filter(User.username == nip).first()
            if not u:
                u = User(username=nip, hashed_password=hashed, role="ADVISOR")
                db.add(u)
                db.flush()
            elif u.role != "ADVISOR":
                u.role = "ADVISOR"
            
            adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
            if not adv:
                adv = Advisor(user_id=u.id, nama=nama)
                db.add(adv)
                db.flush()
            
            mhs_list = pa.get("mahasiswa") or pa.get("mahasiswa_bimbingan") or pa.get("bimbingan") or []
            if isinstance(mhs_list, list):
                for mhs in mhs_list:
                    nim = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
                    if nim: advisor_map[nim] = adv.id
            elif pa.get("nim"):
                advisor_map[str(pa["nim"])] = adv.id
    
    db.commit()
    
    linked = 0
    for nim, adv_id in advisor_map.items():
        student = db.query(Student).filter(Student.nim == nim).first()
        if student:
            student.advisor_id = adv_id
            linked += 1
    
    db.commit()
    print(f"[OK] Selesai: {total_pa} PA dimuat, {len(advisor_map)} relasi, {linked} mhs dihubungkan.")

except Exception as e:
    print(f"[ERROR] {e}")

final_advisors = db.query(User).filter(User.role == "ADVISOR").count()
final_linked = db.query(Student).filter(Student.advisor_id.isnot(None)).count()
print(f"\nTotal Advisor Aktif: {final_advisors}")
print(f"Total Mahasiswa Terhubung: {final_linked}")
