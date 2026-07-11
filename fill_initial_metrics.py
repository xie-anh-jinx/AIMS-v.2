import os
import random
from dotenv import load_dotenv

load_dotenv(".env")
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

def main():
    db = SessionLocal()
    
    # Ambil semua mahasiswa yang punya PA tapi record IPK nya masih 0 atau kosong
    students = db.query(Student).filter(Student.advisor_id.isnot(None)).all()
    
    records_added = 0
    records_updated = 0
    
    for st in students:
        recs = db.query(AcademicRecord).filter(AcademicRecord.student_id == st.id).all()
        
        # Determine relative sem based on angkatan (assume current year is 2026 for S2 context, or 2025 based on previous)
        # We will use st.semester or estimate from angkatan
        sem_rel = int(st.semester) if st.semester and str(st.semester).isdigit() else 4
        if sem_rel > 14: sem_rel = 4 # Fallback
        if sem_rel == 0: sem_rel = 2
        
        base_sks = sem_rel * random.randint(18, 22)
        base_ipk = round(random.uniform(2.80, 3.95), 2)
        
        if not recs:
            # Generate new academic record placeholder
            new_r = AcademicRecord(
                student_id=st.id,
                semester=sem_rel,
                ips=round(random.uniform(2.80, 4.00), 2),
                ipk=base_ipk,
                sks=base_sks,
                status="AKTIF"
            )
            db.add(new_r)
            records_added += 1
        else:
            for r in recs:
                if r.ipk == 0.0 or r.sks == 0:
                    r.semester = sem_rel
                    r.ipk = base_ipk
                    r.sks = base_sks
                    r.ips = round(random.uniform(2.80, 4.00), 2)
                    r.status = "AKTIF"
                    records_updated += 1
                    
    db.commit()
    print(f"Generated {records_added} new records and updated {records_updated} zeroes with synthetic metrics.")

if __name__ == "__main__":
    main()
