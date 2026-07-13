"""
patch_students_records.py
──────────────────────────
Sinkronisasi & seeding data akademis (academic_records) untuk seluruh mahasiswa
yang belum memiliki riwayat akademik di database.

Aturan heuristik:
- Jika mahasiswa Lulus -> IPK 3.25, SKS 144, Status "Aman"
- Jika mahasiswa DO -> IPK 1.50, SKS 60, Status "HIGH_RISK"
- Jika mahasiswa Aktif/Cuti/Non Aktif -> Hitung berdasarkan angkatan & lama studi:
  - >= 7 tahun (DO Risk) -> IPK 1.85, SKS 100, Status "HIGH_RISK"
  - >= 5 tahun (Warning)  -> IPK 2.45, SKS 115, Status "Warning"
  - < 5 tahun (Aman)      -> IPK 3.25, SKS (semester * 20), Status "Aman"
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

def main():
    db = SessionLocal()
    
    # Cari mahasiswa yang tidak punya record akademik sama sekali
    subq = db.query(AcademicRecord.student_id).distinct().subquery()
    students_no_rec = db.query(Student).filter(~Student.id.in_(subq)).all()
    
    print(f"Mengurai {len(students_no_rec)} mahasiswa tanpa data akademik...")
    
    batch_size = 500
    created = 0
    current_year = 2026
    
    for idx, s in enumerate(students_no_rec, 1):
        # Default parameter
        est_ipk = 3.25
        est_sks = max(20, min(144, s.semester * 20))
        est_status = "Aman"
        
        if s.status == "Lulus":
            est_ipk = 3.25
            est_sks = 144
            est_status = "Aman"
        elif s.status == "Drop Out":
            est_ipk = 1.50
            est_sks = 60
            est_status = "HIGH_RISK"
        else: # Aktif, Cuti, Non Aktif
            years_enrolled = current_year - s.angkatan
            if years_enrolled >= 7:
                est_ipk = 1.85
                est_status = "HIGH_RISK"
                est_sks = max(40, min(120, s.semester * 15))
            elif years_enrolled >= 5:
                est_ipk = 2.45
                est_status = "Warning"
                est_sks = max(60, min(130, s.semester * 18))
            else:
                est_ipk = 3.25
                est_status = "Aman"
                est_sks = max(20, min(144, s.semester * 20))
                
        # Buat AcademicRecord
        rec = AcademicRecord(
            student_id=s.id,
            semester=s.semester or 1,
            ips=est_ipk,
            ipk=est_ipk,
            sks=est_sks,
            status=est_status
        )
        db.add(rec)
        created += 1
        
        if idx % batch_size == 0:
            db.commit()
            print(f"Progress: {idx}/{len(students_no_rec)} disinkronkan.")
            
    db.commit()
    db.close()
    
    print("=" * 60)
    print(f"✅ Seeding AcademicRecord Selesai!")
    print(f"   - Total record ditambahkan: {created}")
    print("=" * 60)

if __name__ == "__main__":
    main()
