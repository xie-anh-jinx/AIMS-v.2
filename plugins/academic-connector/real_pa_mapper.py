import os
import sys
import json
import requests
import bcrypt
from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student

db = next(get_db())

print("=" * 60)
print("Injecting REAL PA mappings using Manual Auth Token...")

TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiZWY3NjYxNzhjNDA5YjcxNjBhZjI3MjdmNWViNzg2MDBjZjE4MDkzZGFmMTc3NzJiMGJkMDQ5OTZlNmFkZDkzZDljN2IyNzQ0YmE3MWNiOGQiLCJpYXQiOjE3ODMzOTUyMTMuMzE5NzgyLCJuYmYiOjE3ODMzOTUyMTMuMzE5Nzg1LCJleHAiOjE3ODM4MjcyMTMuMzE0ODY5LCJzdWIiOiIxMjE5NzEiLCJzY29wZXMiOlsiKiJdfQ.U38V2Z0FBu_wsfb7cK5frVPKFNSCeZfPUtFTTRkSdAEAfhJSz2I0_d1b0cigtCywjhWXO5CyAEDHvfepx2NNuzsYQrWOrtZ7c-8TO6jDPSOBAep1rBOmYXVf1MUY-iScIs2lgynSS1PdYzTI0bMV1_vMcImt18OtWmuCdkGtuDu7TJjTwpMIVPP1sR6B9LdxT519A7Z1Ri1kYu6Z4mHKBlPmMJMVTXJpyrqFArJTWcbNJu86u8lRtiFuUrXYNTEPYFfVg27ArIczk5SYUZ48J1ZtPDraXQM3bX7jBl-NigQSaHghicLB64Ch7jt-iNure0FAeqUGHd05R084skqWsaauCN2FYULqhLFaop_51TuGrInXPxNjOyBruTI0xoquabBtuuwZXyp7y_g5_mp29grfNzchJ6BqoysVdEX339PPwlRCyqmW1uorFlZfUjV9U21N9-N2NSmS6AHfesz9DoCuOUBM1bvTxdH-tVYa2_TBRnQxY2v5VYVwtFbYGrZeZCgr-qPoF_oeEK7Hmta2v4s_SRmaCFcgSWID2qDuif_6ZCxIrHzQfLnRZ4A6g5L1q8EEJODSzolcRX8RVFQOOyrjxD6kpQ3-e_uW5LSQZFd8D2eP55QT8DTFrT-HvIYsOdOWaijdaWwY9wUTqzvEQUd-T9ZUccBT1jfl251D_ks"

headers = {
    "Authorization": f"Bearer {TOKEN}", 
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Linux; Android 15; Pixel 9) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/150.0.0.0 Mobile Safari/537.36"
}

NEOSIA_BASE = "https://api.neosia.unhas.ac.id"
hashed = bcrypt.hashpw("password123".encode("utf-8"), bcrypt.gensalt(rounds=12)).decode("utf-8")

def map_db():
    try:
        # Clear fake/emergency mappings
        db.query(Student).update({Student.advisor_id: None})
        fake_advs = db.query(Advisor).all()
        for fa in fake_advs:
            if not fa.nama.startswith("Prof. Dr.") and not fa.nama.startswith("Dr."):
                db.delete(fa)
        db.commit()

        # Let's get prodi_semester id 3600 exactly as the user specified
        print("[API] Fetching PA data for id_prodi_semester=3600...")
        pa_res = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]=3600", headers=headers, timeout=15)
        
        if pa_res.status_code != 200:
            print(f"[ERROR] API returned {pa_res.status_code}")
            return
            
        pa_data = pa_res.json()
        pa_arr = (pa_data.get("dosens") or pa_data.get("penasihat_akademiks") or pa_data.get("penasihatAkademiks") or pa_data.get("data") or pa_data.get("items") or [])
        
        total_pa = 0
        advisor_map = {}
        
        for paObj in pa_arr:
            d = paObj.get("dosen") or paObj
            nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
            if not nip: continue
            
            nama = d.get("nama_dosen") or d.get("nama") or d.get("nama_pegawai") or f"Dosen {nip}"
            total_pa += 1
            
            u = db.query(User).filter(User.username == nip).first()
            if not u:
                u = User(username=nip, hashed_password=hashed, role="ADVISOR")
                db.add(u)
                db.flush()
            
            u.hashed_password = hashed
            u.role = "ADVISOR"
            
            adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
            if not adv:
                adv = Advisor(user_id=u.id, nama=nama)
                db.add(adv)
                db.flush()
            else:
                adv.nama = nama
                
            mhs_list = paObj.get("mahasiswas") or paObj.get("mahasiswa") or paObj.get("bimbingan") or []
            if isinstance(mhs_list, list):
                for mhs in mhs_list:
                    nim = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
                    if nim: advisor_map[nim] = adv.id
        
        db.commit()
        print(f"Loaded {total_pa} PA, mapped {len(advisor_map)} unique students from Sem 3600.")
        
        # Now fetch other active semesters
        ps_res = requests.get(f"{NEOSIA_BASE}/api/admin/prodi_semester?filters[is_used]=1", headers=headers, timeout=15)
        if ps_res.status_code == 200:
            ps_arr = ps_res.json().get("prodiSemesters") or ps_res.json().get("data") or []
            for ps in ps_arr:
                idSem = ps.get("id") or ps.get("id_prodi_semester")
                if idSem and str(idSem) != "3600":
                    print(f"Fetching PA data for semester {idSem}...")
                    r = requests.get(f"{NEOSIA_BASE}/api/admin/penasihat_akademik?filters[id_prodi_semester]={idSem}", headers=headers, timeout=15)
                    if r.status_code == 200:
                        arr = (r.json().get("dosens") or r.json().get("data") or [])
                        for paO in arr:
                            d = paO.get("dosen") or paO
                            nip = str(d.get("nip"))
                            if not nip: continue
                            
                            u = db.query(User).filter(User.username == nip).first()
                            if not u:
                                u = User(username=nip, hashed_password=hashed, role="ADVISOR")
                                db.add(u)
                                db.flush()
                                
                            a = db.query(Advisor).filter(Advisor.user_id == u.id).first()
                            if not a:
                                a = Advisor(user_id=u.id, nama=d.get("nama") or f"Dosen {nip}")
                                db.add(a)
                                db.flush()
                                
                            ml = paO.get("mahasiswas") or paO.get("mahasiswa") or []
                            for m in ml:
                                n = str(m.get("nim"))
                                if n: advisor_map[n] = a.id
            db.commit()
            print(f"Loaded ALL ACTIVE semesters. Total mapping: {len(advisor_map)} unique students.")

        # Assign in DB
        linked = 0
        for nim, adv_id in advisor_map.items():
            st = db.query(Student).filter(Student.nim == nim).first()
            if st:
                st.advisor_id = adv_id
                linked += 1
                
        db.commit()
        print(f"[OK] {linked} mahasiswa di DB berhasil diikat dengan Dosen PA masing-masing.")

    except Exception as e:
        print(f"[ERROR] {e}")

if __name__ == "__main__":
    map_db()
    
    final_advisors = db.query(User).filter(User.role == "ADVISOR").count()
    final_linked = db.query(Student).filter(Student.advisor_id.isnot(None)).count()
    print(f"\nFinal Statistics:")
    print(f"Total Advisor Aktif di DB: {final_advisors}")
    print(f"Total Mahasiswa dengan PA di DB: {final_linked}")
