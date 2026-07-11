import os
import requests
import bcrypt
from dotenv import load_dotenv

# Ensure we have the ENV loaded
load_dotenv(".env")
load_dotenv("plugins/academic-connector/.env", override=False)

from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

db = SessionLocal()
token = os.getenv("NEOSIA_TOKEN")
if not token:
    print("Error: NEOSIA_TOKEN not found in .env")
    exit(1)

headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"

hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")
advisor_map = {}
total_pa = 0

# --- Process 1: Explicit id_prodi_semester = 3604 ---
print("Fetching PA directly for id_prodi_semester=3604...")
pa_res_3604 = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]=3604", headers=headers, timeout=15)
if pa_res_3604.status_code == 200:
    pa_data_3604 = pa_res_3604.json()
    pa_arr = pa_data_3604.get("dosens") or pa_data_3604.get("penasihat_akademiks") or pa_data_3604.get("data") or []
    if type(pa_arr) is dict: pa_arr = pa_arr.get("data", [])
    
    for paObj in pa_arr:
        d = paObj.get("dosen") or paObj
        nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
        if not nip: continue
        
        nama = d.get("nama_dosen") or d.get("nama") or d.get("nama_pegawai") or f"Dosen {nip}"
        total_pa += 1
        
        u = db.query(User).filter(User.username == nip).first()
        if not u:
            u = User(username=nip, hashed_password=hashed_pw, role="ADVISOR")
            db.add(u)
            db.flush()
            
        adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
        if not adv:
            adv = Advisor(user_id=u.id, nama=nama)
            db.add(adv)
            db.flush()
            
        mhs_list = paObj.get("mahasiswas") or paObj.get("mahasiswa") or paObj.get("bimbingan") or []
        for mhs in mhs_list:
            nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
            if nim_mhs: advisor_map[nim_mhs] = adv.id

# --- Process 2: id_prodi = 37 ---
print("Fetching prodi_semester for id_prodi=37...")
ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[id_prodi]=37&filters[is_used]=1", headers=headers, timeout=15)
if ps_res.status_code == 200:
    ps_data = ps_res.json()
    ps_arr = ps_data.get("prodiSemesters") or ps_data.get("data") or []
    print(f"Found {len(ps_arr)} prodi_semester(s) for prodi 37.")
    for ps in ps_arr:
        idSem = ps.get("id") or ps.get("id_prodi_semester")
        if not idSem: continue
        
        pa_res = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
        if pa_res.status_code != 200: continue
        
        pa_data = pa_res.json()
        pa_lst = pa_data.get("dosens") or pa_data.get("penasihat_akademiks") or pa_data.get("data") or []
        if type(pa_lst) is dict: pa_lst = pa_lst.get("data", [])
        
        for paObj in pa_lst:
            d = paObj.get("dosen") or paObj
            nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
            if not nip: continue
            
            nama = d.get("nama_dosen") or d.get("nama") or f"Dosen {nip}"
            total_pa += 1
            
            u = db.query(User).filter(User.username == nip).first()
            if not u:
                u = User(username=nip, hashed_password=hashed_pw, role="ADVISOR")
                db.add(u)
                db.flush()
                
            adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
            if not adv:
                adv = Advisor(user_id=u.id, nama=nama)
                db.add(adv)
                db.flush()
                
            mhs_list = paObj.get("mahasiswas") or paObj.get("mahasiswa") or paObj.get("bimbingan") or []
            for mhs in mhs_list:
                nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
                if nim_mhs: advisor_map[nim_mhs] = adv.id

db.commit()

linked = 0
for nim, adv_id in advisor_map.items():
    st = db.query(Student).filter(Student.nim == nim).first()
    if st:
        st.advisor_id = adv_id
        linked += 1

db.commit()
print(f"Successfully processed {total_pa} PA records from these specific parameters.")
print(f"Found {len(advisor_map)} unique student mappings.")
print(f"Successfully attached {linked} students residing in local database.")
