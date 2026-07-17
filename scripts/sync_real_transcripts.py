import os
import sys
import time
import httpx
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, Course, Grade, AcademicRecord
from sqlalchemy.exc import IntegrityError

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NEOSIA_API_BASE = os.getenv("NEOSIA_API_BASE", "https://api.neosia.unhas.ac.id")
NEOSIA_TOKEN = os.getenv("NEOSIA_TOKEN")
if not NEOSIA_TOKEN:
    logger.error("NEOSIA_TOKEN is missing in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {NEOSIA_TOKEN}",
    "Accept": "application/json"
}

def compute_status(ipk: float) -> str:
    if ipk < 2.0: return "HIGH_RISK"
    if ipk < 2.75: return "Warning"
    return "Aman"

def sync_all_transcripts():
    db = SessionLocal()
    
    # 1. Get all active students without grades yet
    students = db.query(Student).all()
    logger.info(f"Targeting {len(students)} students in DB...")

    # Load existing courses into local cache to avoid heavy DB queries
    courses_in_db = db.query(Course).all()
    course_cache = {c.kode: c.id for c in courses_in_db}
    
    total_added = 0
    total_skipped = 0
    total_failed = 0

    with httpx.Client(timeout=10.0, headers=HEADERS) as client:
        for idx, student in enumerate(students, 1):
            url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={student.nim}"
            
            # API retry logic
            success = False
            for attempt in range(3):
                try:
                    response = client.get(url)
                    
                    if response.status_code == 404:
                        success = True
                        break
                        
                    response.raise_for_status()
                    data = response.json()
                    
                    transkrips = data.get("transkrips", [])
                    ipk_dict = data.get("current_indeks_prestasi", {})
                    ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
                    
                    added_courses = set()
                    total_sks = sum(int(t.get("sks", 0) or 0) for t in transkrips if t.get("is_used") == 1)
                    max_semester = 1
                    
                    db.query(Grade).filter(Grade.student_id == student.id).delete()
                    grades_to_add = []
                    
                    for t in transkrips:
                        if t.get("is_used") != 1: continue
                        
                        kode = t.get("kode_mata_kuliah")
                        if not kode: continue
                        
                        sks = int(t.get("sks", 0) or 0)
                        nama = t.get("nama_mata_kuliah")
                        if not nama and t.get("mata_kuliah"):
                            nama = t.get("mata_kuliah").get("nama_resmi")
                        if not nama: nama = "Unknown"
                        
                        semester_data = t.get("semester", {})
                        sem_val = int(t.get("mata_kuliah", {}).get("semester") or semester_data.get("kode", "1")[-1])
                        
                        bobot = float(t.get("nilai_angka") or 0.0)
                        nilai_huruf = t.get("nilai_huruf") or "E"
                        
                        if kode in added_courses:
                            continue
                        added_courses.add(kode)
                        
                        course_id = course_cache.get(kode)
                        if not course_id:
                            c = Course(kode=kode, nama=nama, sks=sks, semester=sem_val)
                            db.add(c)
                            db.commit()
                            db.refresh(c)
                            course_id = c.id
                            course_cache[kode] = course_id
                            
                        if sem_val > max_semester:
                            max_semester = sem_val
                            
                        grades_to_add.append(
                            Grade(
                                student_id=student.id,
                                course_id=course_id,
                                semester=sem_val,
                                grade=nilai_huruf,
                                bobot=bobot
                            )
                        )
                        
                    db.add_all(grades_to_add)
                    
                    status_text = compute_status(ipk)
                    if ipk == 0.0 and len(grades_to_add) == 0:
                        status_text = "Baru/Cuti"
                    
                    semester_calc = max(1, min(14, (2026 - student.angkatan) * 2)) if student.angkatan else max_semester
                    
                    db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).delete()

                    rec = AcademicRecord(
                        student_id=student.id,
                        semester=semester_calc,
                        ips=ipk,
                        ipk=ipk,
                        sks=total_sks,
                        status=status_text
                    )
                    db.add(rec)
                    student.semester = semester_calc
                    student.status = status_text if status_text != "Baru/Cuti" else "Aktif"
                    
                    db.commit()
                    total_added += 1
                    success = True
                    break
                    
                except httpx.HTTPError as e:
                    time.sleep(3)
                except Exception as e:
                    db.rollback()
                    time.sleep(1)
                    break
                    
            if not success:
                total_failed += 1
            
            time.sleep(2.0)
            
    db.close()
    logger.info("=" * 60)
    logger.info(f"✅ Sync Real Transcripts Selesai! (Added: {total_added}, Skipped: {total_skipped}, Failed: {total_failed})")

if __name__ == "__main__":
    sync_all_transcripts()
