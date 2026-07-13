import os
import random
from dotenv import load_dotenv

load_dotenv(".env")
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

def main():
    db = SessionLocal()
    
    # Ambil semua mahasiswa agar chart Risiko di dashboard admin bisa menampung semuanya
    students = db.query(Student).all()
    
    records_added = 0
    records_updated = 0
    
    for st in students:
        recs = db.query(AcademicRecord).filter(AcademicRecord.student_id == st.id).all()
        
        sem_rel = int(st.semester) if st.semester and str(st.semester).isdigit() else 4
        if sem_rel > 14: sem_rel = 4 
        if sem_rel == 0: sem_rel = 2
        
        base_sks = sem_rel * random.randint(18, 22)
        
        # Determine risk bucket
        buck = random.random()
        if buck < 0.10:
             # High risk
             base_ipk = round(random.uniform(1.20, 1.99), 2)
        elif buck < 0.30:
             # Warning
             base_ipk = round(random.uniform(2.00, 2.74), 2)
        else:
             # Safe
             base_ipk = round(random.uniform(2.75, 3.95), 2)
        
        if not recs:
            # Generate new academic record placeholder
            new_r = AcademicRecord(
                student_id=st.id,
                semester=sem_rel,
                ips=round(random.uniform(2.70, 4.00), 2),
                ipk=base_ipk,
                sks=base_sks,
                status="Aktif"
            )
            db.add(new_r)
            records_added += 1
        else:
            for r in recs:
                # Force regenerate IPK for risk mapping simulation
                r.semester = sem_rel
                r.ipk = base_ipk
                r.sks = base_sks
                r.ips = round(random.uniform(2.70, 4.00), 2)
                r.status = "Aktif"
                records_updated += 1
                    
    db.commit()
    print(f"Generated {records_added} new records and updated {records_updated} zeroes with synthetic metrics.")

if __name__ == "__main__":
    main()
