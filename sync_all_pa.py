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

print("Fetching all active prodi_semesters across the university...")
ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[is_used]=1", headers=headers, timeout=20)
if ps_res.status_code != 200:
    print(f"Failed to fetch prodi_semester: {ps_res.status_code}")
    exit(1)

ps_data = ps_res.json()
ps_arr = ps_data.get("prodiSemesters") or ps_data.get("data") or []
print(f"Found {len(ps_arr)} prodi_semester(s).")

hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")
advisor_map = {}
total_pa = 0
processed_ps = 0

for ps in ps_arr:
    idSem = ps.get("id") or ps.get("id_prodi_semester")
    if not idSem: continue
    
    processed_ps += 1
    # Print every 50 loops to avoid terminal spam
    if processed_ps % 50 == 0:
        print(f"Processing prodi_semester batch {processed_ps}/{len(ps_arr)}...")
        
    pa_res = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
    if pa_res.status_code != 200: continue
    pa_data = pa_res.json()
    
    pa_arr = pa_data.get("dosens") or pa_data.get("penasihat_akademiks") or pa_data.get("penasihatAkademiks") or pa_data.get("data") or pa_data.get("items") or []
    if type(pa_arr) is dict:
        pa_arr = pa_arr.get("data", [])
        
    for paObj in pa_arr:
        d = paObj.get("dosen") or paObj
        nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
        if not nip: continue
        
        nama = d.get("nama_dosen") or d.get("nama") or d.get("nama_pegawai") or f"Dosen {nip}"
        total_pa += 1
        
        # Upsert User
        u = db.query(User).filter(User.username == nip).first()
        if not u:
            u = User(username=nip, hashed_password=hashed_pw, role="ADVISOR")
            db.add(u)
            db.flush()
        elif u.role != "ADVISOR":
            u.role = "ADVISOR"
            
        u.hashed_password = hashed_pw
        
        # Upsert Advisor Profile
        adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
        if not adv:
            adv = Advisor(user_id=u.id, nama=nama)
            db.add(adv)
            db.flush()
            
        # Map Students
        mhs_list = paObj.get("mahasiswas") or paObj.get("mahasiswa") or paObj.get("mahasiswa_bimbingan") or paObj.get("bimbingan") or []
        for mhs in mhs_list:
            nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
            if nim_mhs: 
                advisor_map[nim_mhs] = adv.id

db.commit()

linked = 0
for nim, adv_id in advisor_map.items():
    st = db.query(Student).filter(Student.nim == nim).first()
    if st:
        st.advisor_id = adv_id
        linked += 1

db.commit()
print(f"Successfully synced {total_pa} PA occurrences across all prodi. Found and mapped {len(advisor_map)} unique students.")
print(f"Successfully attached {linked} students residing in our local database to their PA.")
