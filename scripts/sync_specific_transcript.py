import os
import sys
import httpx
import logging
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, Course, Grade, AcademicRecord

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

NEOSIA_API_BASE = os.getenv("NEOSIA_API_BASE", "https://api.neosia.unhas.ac.id")
# Use the token provided by user or from ENV
NEOSIA_TOKEN = "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiNDk4NjZjMWExNGFkZTFmNGMxNDUyOTZlZDc2MjlhNGJmZDIzOTkxNWVjMTBjZjcxNDJlOWYxMjA5ZDk3YzVmZDQ1M2QzZmFjNWFmYzcxYTIiLCJpYXQiOjE3ODM5OTg5MTUuOTgxMDc3LCJuYmYiOjE3ODM5OTg5MTUuOTgxMDgsImV4cCI6MTc4NDQzMDkxNS45NTAwMzgsInN1YiI6Ijg4NDI1Iiwic2NvcGVzIjpbIioiXX0.g2ey9C57ZarKuJCaV-ZH2c3ALXckGye0MjGOMnu6Qt4BAiyVbHhN2FD7J_iAZKvAou2V_ub4dRwHKK74dXdLIF2uHghm800_K5rXL5I7hzgA--NPrUE_zlPaDmMAQHNydcHhPSRCzYOJt5RenB_kUpDznRLDkvmIDuJEYwOcfhVXmkEv7PVOG-U0eqc3aiQ7nG5aASd_sK2OeeSNw0qT0gBz-AjL3hvxVqsRGZ04PEu1QOsVNOnRfejS6S0uEUQvh6s_m7ReB0bDgdPF-llsH71PFB0mMwKj9W71MnphgJ57LthOOmJmDq0ZSsbTtLA2AANOY26UEifzSg_w0AzEY4BH6dJcae4qUHpDS7HBGcelyml7hjMLToZ3Qedr0rwI7P_G3h04eZBs2-0_A_OKF3zEBce1ZAXS5oeNSwlCX_RZpgq8mpLQBsQsOffN5FpjF1c13Om8cNCRRm1RmtN402j-YaLdbGcVfPi63_x5ozWV3JyT--ZMHk_6JO5r6RmPI689GaRVuDyaemsoGuVQ2mnMfRqyH1w2r4Uxo0maVQkPBYKLeDlUrxVHwdVGCkmHFIemlRKwjlxjhrPosU2ugtkzNDx7Xw-HgC-vZqqxi2NGKn1TQrZE6abd_enA7c9qNGd-UHMciu1UojKduFD0OffEYYL5aoQ6Zwl6iok7JJg"

HEADERS = {
    "Authorization": f"Bearer {NEOSIA_TOKEN}",
    "Accept": "application/json"
}

def compute_status(ipk: float) -> str:
    if ipk < 2.0: return "HIGH_RISK"
    if ipk < 2.75: return "Warning"
    return "Aman"

def sync_single_student(nim: str):
    db = SessionLocal()
    student = db.query(Student).filter(Student.nim == nim).first()
    
    if not student:
        logger.error(f"Student with NIM {nim} not found in local DB.")
        db.close()
        return

    courses_in_db = db.query(Course).all()
    course_cache = {c.kode: c.id for c in courses_in_db}
    
    url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={student.nim}"
    
    with httpx.Client(timeout=10.0, headers=HEADERS) as client:
        response = client.get(url)
        if response.status_code != 200:
            logger.error(f"Failed to fetch transkrip from NeoSIA for {nim}: {response.status_code}")
            return
            
        data = response.json()
        transkrips = data.get("transkrips", [])
        ipk_dict = data.get("current_indeks_prestasi", {})
        ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
        
        added_courses = set()
        total_sks = sum(int(t.get("sks", 0) or 0) for t in transkrips if t.get("is_used") == 1)
        max_semester = 1
        
        # Reset existing records
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
            sem_val_raw = t.get("mata_kuliah", {}).get("semester") or semester_data.get("kode", "1")[-1]
            try: sem_val = int(sem_val_raw)
            except: sem_val = 1
            
            bobot = float(t.get("nilai_angka") or 0.0)
            nilai_huruf = t.get("nilai_huruf") or "E"
            
            if kode in added_courses: continue
            added_courses.add(kode)
            
            course_id = course_cache.get(kode)
            if not course_id:
                new_c = Course(kode=kode, nama=nama, sks=sks)
                db.add(new_c)
                db.flush()
                course_id = new_c.id
                course_cache[kode] = course_id
                
            grades_to_add.append(Grade(
                student_id=student.id,
                course_id=course_id,
                semester=sem_val,
                bobot=bobot,
                grade=nilai_huruf
            ))
            if sem_val > max_semester:
                max_semester = sem_val

        db.add_all(grades_to_add)

        # Build dummy AcademicRecords (IPK simulation)
        db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).delete()
        records_to_add = []
        
        status_rec = compute_status(ipk)
        for s in range(1, max_semester + 1):
            records_to_add.append(AcademicRecord(
                student_id=student.id,
                semester=s,
                ips=ipk,
                ipk=ipk,
                sks=total_sks if s == max_semester else (total_sks // max_semester) * s,
                status=status_rec
            ))
            
        db.add_all(records_to_add)
        db.commit()
        
        logger.info(f"Successfully synced transcript for {student.nim}: {len(grades_to_add)} courses, IPK {ipk}, SKS {total_sks}")

if __name__ == "__main__":
    sync_single_student("F011201037")
