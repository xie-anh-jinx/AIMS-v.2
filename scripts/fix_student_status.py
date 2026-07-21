"""
fix_student_status.py
---------------------
Memperbaiki data student.status yang terlanjur ditimpa oleh klasifikasi risiko
akademik ("Aman", "Warning", "HIGH_RISK") akibat bug di sync_real_transcripts.py.

Logika: 
- Mahasiswa dengan status "Aman", "Warning", "HIGH_RISK", atau "Baru/Cuti" di 
  tabel students → kembalikan ke "Aktif" karena itu adalah klasifikasi risiko, 
  bukan status keaktifan.
- Status yang sah untuk student.status: Aktif, Cuti, Lulus, Drop Out, Keluar
"""
import sys, os, logging
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student
from sqlalchemy import func

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# Status yang BUKAN status keaktifan NeoSIA — harus dikembalikan ke "Aktif"
RISK_STATUSES = {"Aman", "Warning", "HIGH_RISK", "Baru/Cuti"}

# Status keaktifan yang sah dari NeoSIA
VALID_ENROLLMENT_STATUSES = {"Aktif", "Cuti", "Lulus", "Drop Out", "Keluar", "Non Aktif"}

def fix_status():
    db = SessionLocal()
    
    # Hitung berapa yang perlu diperbaiki
    wrong_students = db.query(Student).filter(
        Student.status.in_(list(RISK_STATUSES))
    ).all()
    
    logger.info(f"Menemukan {len(wrong_students)} mahasiswa dengan status salah")
    
    # Hitung breakdown per status yang salah
    breakdown = db.query(Student.status, func.count(Student.id)).filter(
        Student.status.in_(list(RISK_STATUSES))
    ).group_by(Student.status).all()
    
    for s, c in breakdown:
        logger.info(f"  - '{s}': {c} mahasiswa")
    
    if not wrong_students:
        logger.info("Tidak ada yang perlu diperbaiki. ✅")
        db.close()
        return

    # Perbaiki: set status kembali ke "Aktif"
    fixed_count = 0
    for student in wrong_students:
        old_status = student.status
        student.status = "Aktif"
        fixed_count += 1
        if fixed_count % 100 == 0:
            logger.info(f"  Progress: {fixed_count}/{len(wrong_students)} diperbaiki...")
            db.commit()
    
    db.commit()
    
    # Verifikasi hasil
    remaining_wrong = db.query(func.count(Student.id)).filter(
        Student.status.in_(list(RISK_STATUSES))
    ).scalar()
    
    total_aktif = db.query(func.count(Student.id)).filter(
        Student.status == "Aktif"
    ).scalar()
    
    logger.info("=" * 60)
    logger.info(f"✅ Selesai! {fixed_count} mahasiswa diperbaiki → status 'Aktif'")
    logger.info(f"📊 Total mahasiswa Aktif sekarang: {total_aktif}")
    logger.info(f"📊 Sisa status salah: {remaining_wrong}")
    
    # Tampilkan semua status yang ada sekarang
    all_statuses = db.query(Student.status, func.count(Student.id)).group_by(Student.status).all()
    logger.info("\nDistribusi status mahasiswa saat ini:")
    for s, c in all_statuses:
        logger.info(f"  - '{s}': {c}")
    
    db.close()

if __name__ == "__main__":
    fix_status()
