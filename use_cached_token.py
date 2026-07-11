import os
import sys
import json
import requests
import bcrypt
from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student

db = next(get_db())

print("=" * 60)
print("Fixing PA with cached Session Tokens...")

# Get token from session.json
token = None
for acc in ['fib_pariwisata', 'fib_sas_prancis', 'fib_sas_jepang', 'fib_sas_daerah', 'fib_ilmu_sejarah']:
    tf = f"plugins/academic-connector/providers/{acc}/session.json"
    if os.path.exists(tf):
        with open(tf, "r") as f:
            try:
                data = json.load(f)
                if data.get("bearerToken"):
                    token = data["bearerToken"]
                    print(f"Loaded token from {acc}")
                    break
            except Exception:
                pass
                
if not token:
    print("[ERROR] No session token found.")
    sys.exit(1)

hashed = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
NEOSIA_BASE = "https://api.neosia.unhas.ac.id"

try:
    ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[is_used]=1", headers=headers, timeout=15)
    ps_data = ps_res.json()
    ps_arr = ps_data.get("prodiSemesters") or ps_data.get("data") or []
    print(f"[OK] Menemukan {len(ps_arr)} prodi_semester aktif.")
    
    total_pa = 0
    advisor_map = {}
    
    for ps in ps_arr:
        idSem = ps.get("id") or ps.get("id_prodi_semester")
        if not idSem: continue
        
        pa_res = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
        if pa_res.status_code != 200: continue
        pa_data = pa_res.json()
        
        pa_arr = (pa_data.get("dosens") or pa_data.get("penasihat_akademiks") or pa_data.get("penasihatAkademiks") or pa_data.get("data") or pa_data.get("items") or [])
        
        for paObj in pa_arr:
            d = paObj.get("dosen") or paObj
            nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
            if not nip: continue
            
            nama = d.get("nama_dosen") or d.get("nama") or d.get("nama_pegawai") or f"Dosen {nip}"
            total_pa += 1
            
            # Upsert
            u = db.query(User).filter(User.username == nip).first()
            if not u:
                u = User(username=nip, hashed_password=hashed, role="ADVISOR")
                db.add(u)
                db.flush()
            elif u.role != "ADVISOR":
                u.role = "ADVISOR"
            
            # Force password reset to password123
            u.hashed_password = hashed
            
            adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
            if not adv:
                adv = Advisor(user_id=u.id, nama=nama)
                db.add(adv)
                db.flush()
                
            mhs_list = paObj.get("mahasiswas") or paObj.get("mahasiswa") or paObj.get("mahasiswa_bimbingan") or paObj.get("bimbingan") or []
            if isinstance(mhs_list, list):
                for mhs in mhs_list:
                    nim = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
                    if nim: advisor_map[nim] = adv.id
            elif paObj.get("nim"):
                advisor_map[str(paObj["nim"])] = adv.id

    db.commit()
    print(f"Loaded {total_pa} PA from NeoSIA, mapped {len(advisor_map)} unique students.")
    
    linked = 0
    for nim, adv_id in advisor_map.items():
        st = db.query(Student).filter(Student.nim == nim).first()
        if st:
            st.advisor_id = adv_id
            linked += 1
            
    db.commit()
    print(f"[OK] Selesai: {total_pa} PA dimuat, {len(advisor_map)} relasi disiapkan, {linked} mahasiswa di DB dihubungkan.")

except Exception as e:
    print(f"[ERROR] {e}")

final_advisors = db.query(User).filter(User.role == "ADVISOR").count()
final_linked = db.query(Student).filter(Student.advisor_id.isnot(None)).count()
print(f"\nTotal Advisor Aktif di DB: {final_advisors}")
print(f"Total Mahasiswa dengan PA di DB: {final_linked}")
