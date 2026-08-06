import os
import sys
import httpx
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord
from packages.shared.degree_rules import evaluate_academic_risk

NEW_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiMzNjNWJiNjIxODE3YWM5ZGU4OWI2NzE0NDUwOTAyMGE5ODcwZTI5NjE1Y2EwZjViODcyMjE0MTFmNDYwODBjM2I5MGE4ZTYwYTc4NmRlMzYiLCJpYXQiOjE3ODU2NzI3ODUuNjg2ODY4LCJuYmYiOjE3ODU2NzI3ODUuNjg2ODcxLCJleHAiOjE3ODYxMDQ3ODUuNjgxNCwic3ViIjoiODg0MjUiLCJzY29wZXMiOlsiKiJdfQ.HCrMcn-5rXtn6uduGpi0SFLTDxx86MlG7gyeZ8ds7iqbxXunUmAcDnXlD2PkntdwSYNWBMUWI3Pk8STafNlQ_P42BBV2n-myPpk8gcvG2zTFAnRis6KU07-lsxWK8qmWeFNA6wmi9cX9BjbfiOKIZ4nPe6zIvoFuAbPTZ6RFqg0Yoj7Y_Cc08-O8uT0vZ3JevfKfHa7Plpez3YmKoZnlkQubDVWGPtopEtbrUbkeA-ztjRfWIOQuvZS8iq79fVTOAXPjchSu4B0m-djYsnM5BtDb_Qv6PPkBnO5GBbH-0tiE2JJFykOlz-irHMXcWnohuKgkoX-4hp0OexxMrzS_8ka1FPd1s3BVZ8fj0ysxURDQ56XIWo4iaxjtwR3YN2jXwmP9mWeL0ANTMVVueuLw3ljZZR14_xIXlzLjw-B4jTbNYVLtv6xcuLDhEPZIiLDqUGS_PTsqqX_UTft_nT8N17ThxSc8wNWwS2VojRidWY28EBXJCZB3E5SmFOV3wTpgyI5L9rW40QniXtf-DYq4g6njd6h3r00LiKhfOdSCCy7qJAi7hxGq2FpDsz8yBwSz1qD8D8Xxn6tQ9_LpOpjxGlOruPN_fYbl-zbAzIIyClARM8LQcAy0FB9-VLF7-oQjXiMkNwGSBCQnll2Fm4NAStDwdfEP-8Fgdbz9mLHw-ak"

NEOSIA_BASE = "https://api.neosia.unhas.ac.id"
headers = {"Authorization": f"Bearer {NEW_TOKEN}", "Accept": "application/json"}

PRODI_MAP = {
    31: "Sastra Indonesia",
    32: "Sastra Inggris",
    33: "Sastra Perancis",
    34: "Sastra Arab",
    35: "Sastra Daerah",
    36: "Arkeologi",
    37: "Ilmu Sejarah",
    38: "Sastra Jepang",
    197: "Sastra Mandarin",
    198: "Pariwisata"
}

STATUS_MAP = {
    "A": "Aktif",
    "C": "Cuti",
    "L": "Lulus",
    "D": "Drop Out",
    "K": "Keluar",
    "P": "Pindah",
    "N": "Non Aktif",
    "H": "Henti Studi",
}

def sync():
    db = SessionLocal()
    print("🔄 Memulai sinkronisasi data terbaru dari NeoSIA...")

    # 1. Fetch live student status & SPP payment from NeoSIA for all FIB prodis
    updated_status = 0
    updated_transcripts = 0
    
    with httpx.Client(timeout=30) as client:
        for pid, prodi_name in PRODI_MAP.items():
            print(f"📥 Fetching student status & SPP for {prodi_name} (ID: {pid})...")
            url = f"{NEOSIA_BASE}/api/admin/mahasiswa?filters[id_prodi]={pid}"
            try:
                res = client.get(url, headers=headers)
                if res.status_code == 200:
                    data = res.json()
                    mhs_list = data.get("mahasiswas", [])
                    print(f"   -> Retreived {len(mhs_list)} records from NeoSIA.")
                    
                    for m in mhs_list:
                        nim = m.get("nim")
                        if not nim:
                            continue
                        
                        student = db.query(Student).filter(Student.nim == nim).first()
                        if student:
                            kode_status = m.get("kode_status", "A")
                            new_status = STATUS_MAP.get(kode_status, "Aktif")
                            if student.status != new_status:
                                student.status = new_status
                                updated_status += 1
                                
                    db.commit()
            except Exception as e:
                print(f"   ❌ Error fetching prodi {pid}: {e}")
                db.rollback()

        # 2. Update transcripts / academic records for all students
        print("📊 Updating Academic Records & Transcripts...")
        students = db.query(Student).all()
        for idx, s in enumerate(students):
            if idx % 100 == 0 and idx > 0:
                print(f"   Progress transcript sync: {idx}/{len(students)}")
            
            t_url = f"{NEOSIA_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={s.nim}"
            try:
                t_res = client.get(t_url, headers=headers)
                if t_res.status_code == 200:
                    t_data = t_res.json()
                    ipk_dict = t_data.get("current_indeks_prestasi", {})
                    ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
                    sks = int(ipk_dict.get("sks_kumulatif", 0) or 0)
                    
                    # Compute risk
                    sem = s.semester or 1
                    risk = evaluate_academic_risk(s.prodi, sem, sks, ipk)
                    
                    ar = db.query(AcademicRecord).filter(AcademicRecord.student_id == s.id).order_by(AcademicRecord.semester.desc()).first()
                    if ar:
                        ar.ipk = ipk
                        if sks > 0:
                            ar.sks = sks
                        ar.status = "Merah" if risk == "HIGH_RISK" else ("Kuning" if risk == "Warning" else "Aman")
                        updated_transcripts += 1
                    else:
                        new_ar = AcademicRecord(
                            student_id=s.id,
                            semester=sem,
                            ipk=ipk,
                            sks=sks if sks > 0 else 20,
                            status="Merah" if risk == "HIGH_RISK" else ("Kuning" if risk == "Warning" else "Aman")
                        )
                        db.add(new_ar)
                        updated_transcripts += 1
            except Exception as e:
                pass
        
        db.commit()

    print(f"✅ Selesai! Status Mahasiswa diperbarui: {updated_status}, Transkrip & KRS diperbarui: {updated_transcripts}.")
    db.close()

if __name__ == "__main__":
    sync()
