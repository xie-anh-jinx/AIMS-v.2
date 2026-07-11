import os
import requests
import bcrypt
from dotenv import load_dotenv

load_dotenv(".env")
load_dotenv("plugins/academic-connector/.env", override=False)

from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

db = SessionLocal()
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"
hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")

departments = [
    {"name": "Sastra Jepang", "user_env": "ENV_PRODI_JEP_USER", "pass_env": "ENV_PRODI_JEP_PASS"},
    {"name": "Sastra Prancis", "user_env": "ENV_PRODI_FRA_USER", "pass_env": "ENV_PRODI_FRA_PASS"},
    {"name": "Pariwisata", "user_env": "ENV_PRODI_PAR_USER", "pass_env": "ENV_PRODI_PAR_PASS"},
    {"name": "Sastra Daerah", "user_env": "ENV_PRODI_DAE_USER", "pass_env": "ENV_PRODI_DAE_PASS"},
    {"name": "Ilmu Sejarah", "user_env": "ENV_PRODI_SEJ_USER", "pass_env": "ENV_PRODI_SEJ_PASS"},
]

total_mapped = 0

for dept in departments:
    username = os.getenv(dept["user_env"])
    password = os.getenv(dept["pass_env"])
    
    if not username or not password:
        print(f"Skipping {dept['name']}: Credentials not found in .env")
        continue
        
    print(f"\n--- Processing {dept['name']} ---")
    login_data = {"username": username, "password": password}
    
    res = requests.post(f"{NEOSIA_BASE}/api/auth/login", json=login_data, timeout=15)
    if res.status_code != 200:
        print(f"FAILED Login for {dept['name']}: {res.status_code}")
        continue
        
    token = res.json().get("token") or res.json().get("access_token")
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    
    ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[is_used]=1", headers=headers, timeout=15)
    if ps_res.status_code != 200:
        print(f"FAILED fetching prodi_semesters for {dept['name']}")
        continue
        
    ps_arr = ps_res.json().get("prodiSemesters") or ps_res.json().get("data") or []
    print(f"Found {len(ps_arr)} active prodi_semester(s). Syncing...")
    
    advisor_map = {}
    dept_total_pa = 0
    
    for ps in ps_arr:
        idSem = ps.get("id") or ps.get("id_prodi_semester")
        if not idSem: continue
        
        pa_r = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
        if pa_r.status_code != 200: continue
        
        pa_lst = pa_r.json().get("dosens") or pa_r.json().get("penasihat_akademiks") or pa_r.json().get("data") or []
        if isinstance(pa_lst, dict): pa_lst = pa_lst.get("data", [])
        
        for paObj in pa_lst:
            d = paObj.get("dosen") or paObj
            nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
            if not nip: continue
            
            nama = d.get("nama_dosen") or d.get("nama") or f"Dosen {nip}"
            dept_total_pa += 1
            
            u = db.query(User).filter(User.username == nip).first()
            if not u:
                u = User(username=nip, hashed_password=hashed_pw, role="ADVISOR")
                db.add(u)
                db.flush()
            elif u.role != "ADVISOR":
                u.role = "ADVISOR"
                
            adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
            if not adv:
                adv = Advisor(user_id=u.id, nama=nama)
                db.add(adv)
                db.flush()
                
            mhs_list = paObj.get("mahasiswas") or paObj.get("bimbingan") or []
            for mhs in mhs_list:
                nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
                if nim_mhs: advisor_map[nim_mhs] = adv.id

    # Apply mappings to DB
    dept_linked = 0
    for nim, adv_id in advisor_map.items():
        st = db.query(Student).filter(Student.nim == nim).first()
        if st:
            st.advisor_id = adv_id
            dept_linked += 1
            total_mapped += 1

    db.commit()
    print(f"--> {dept['name']} Sync Complete: Added {dept_total_pa} PA records and linked {dept_linked} local students!")

print(f"\n=================================")
print(f"OVERALL SYNC COMPLETE. Linked total {total_mapped} students across all requested departments!")
print(f"=================================")
