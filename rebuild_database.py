import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord, Grade

def compute_status(ipk, sks_total, angkatan):
    # Rule of thumb heuristic to reconstruct lost Lulus/DO stats
    current_year = 2026
    years_active = current_year - angkatan
    
    if sks_total >= 144 and ipk >= 2.25:
        return "Lulus"
    
    if years_active >= 7 and sks_total < 144:
        return "Drop Out"
        
    return "Aktif"

db = SessionLocal()

print("Merekontruksi Rekam Akademik (IPK/SKS) dari tabel Nilai...")
students = db.query(Student).all()
rebuilt = 0

for st in students:
    grades = db.query(Grade).filter(Grade.student_id == st.id).all()
    
    total_bobot_sks = 0.0
    total_sks = 0
    valid_semester = 1
    
    for g in grades:
        if g.course and g.course.sks:
            total_bobot_sks += (g.bobot * g.course.sks)
            total_sks += g.course.sks
            if g.semester and g.semester > valid_semester:
                valid_semester = g.semester
                
    if total_sks > 0:
        new_ipk = round(total_bobot_sks / total_sks, 2)
        # Reconstruct status
        new_status = compute_status(new_ipk, total_sks, st.angkatan)
        
        # Override student status
        st.status = new_status
        
        # Create valid Academic Record
        rec = AcademicRecord(
            student_id=st.id,
            semester=valid_semester,
            ipk=new_ipk,
            ips=new_ipk, # approximation
            sks=total_sks,
            status=new_status
        )
        db.add(rec)
        rebuilt += 1
    else:
        # If no grades, we don't know their standing (likely newly synced S2 or freshmen)
        st.status = "Aktif" 

db.commit()
print(f"Berhasil mengkalkulasi ulang dan memulihkan {rebuilt} data IPK serta Status Lulus/DO!")
