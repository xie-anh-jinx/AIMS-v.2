import os
import json
import bcrypt
from dotenv import load_dotenv

load_dotenv(".env")
from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

def main():
    dump_path = "plugins/academic-connector/pa_dump_all.json"
    if not os.path.exists(dump_path):
        print(f"Error: {dump_path} not found.")
        return
        
    with open(dump_path, "r") as f:
        pa_lst = json.load(f)
        
    print(f"Loaded {len(pa_lst)} raw PA records from dump.")
    if len(pa_lst) == 0:
        return
        
    db = SessionLocal()
    hashed_pw = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode("utf-8")
    
    advisor_map = {}
    total_assigned_students = 0
    
    for paObj in pa_lst:
        d = paObj.get("dosen") or paObj
        nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
        if not nip: continue
        
        nama = d.get("nama_dosen") or d.get("nama") or f"Dosen {nip}"
        
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
            if nim_mhs:
                advisor_map[nim_mhs] = adv.id
                total_assigned_students += 1
                
    # Commit advisors first
    db.commit()
    print(f"Found {len(advisor_map)} unique students mapping to advisors.")
    
    # Map students
    linked = 0
    for nim, adv_id in advisor_map.items():
        st = db.query(Student).filter(Student.nim == nim).first()
        if st:
            st.advisor_id = adv_id
            linked += 1
            
    db.commit()
    print(f"BOM! Successfully imported & matched {linked} missing student-PA relational nodes to local DB!")

if __name__ == "__main__":
    main()
