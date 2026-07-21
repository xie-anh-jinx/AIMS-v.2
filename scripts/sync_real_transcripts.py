"""
sync_real_transcripts.py
------------------------
Sinkronisasi transkrip akademik semua mahasiswa dari NeoSIA ke database AIMS.

PENTING:
- student.status = STATUS KEAKTIFAN dari NeoSIA (Aktif/Cuti/Lulus/Drop Out/Keluar)
  TIDAK BOLEH ditimpa dengan klasifikasi risiko.
- AcademicRecord.status = KLASIFIKASI RISIKO akademik (Aman/Warning/HIGH_RISK)
  berdasarkan IPK mahasiswa.
"""
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
NEOSIA_TOKEN = os.getenv("NEOSIA_TOKEN", "eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiJ9.eyJhdWQiOiIyIiwianRpIjoiNDk4NjZjMWExNGFkZTFmNGMxNDUyOTZlZDc2MjlhNGJmZDIzOTkxNWVjMTBjZjcxNDJlOWYxMjA5ZDk3YzVmZDQ1M2QzZmFjNWFmYzcxYTIiLCJpYXQiOjE3ODM5OTg5MTUuOTgxMDc3LCJuYmYiOjE3ODM5OTg5MTUuOTgxMDgsImV4cCI6MTc4NDQzMDkxNS45NTAwMzgsInN1YiI6Ijg4NDI1Iiwic2NvcGVzIjpbIioiXX0.g2ey9C57ZarKuJCaV-ZH2c3ALXckGye0MjGOMnu6Qt4BAiyVbHhN2FD7J_iAZKvAou2V_ub4dRwHKK74dXdLIF2uHghm800_K5rXL5I7hzgA--NPrUE_zlPaDmMAQHNydcHhPSRCzYOJt5RenB_kUpDznRLDkvmIDuJEYwOcfhVXmkEv7PVOG-U0eqc3aiQ7nG5aASd_sK2OeeSNw0qT0gBz-AjL3hvxVqsRGZ04PEu1QOsVNOnRfejS6S0uEUQvh6s_m7ReB0bDgdPF-llsH71PFB0mMwKj9W71MnphgJ57LthOOmJmDq0ZSsbTtLA2AANOY26UEifzSg_w0AzEY4BH6dJcae4qUHpDS7HBGcelyml7hjMLToZ3Qedr0rwI7P_G3h04eZBs2-0_A_OKF3zEBce1ZAXS5oeNSwlCX_RZpgq8mpLQBsQsOffN5FpjF1c13Om8cNCRRm1RmtN402j-YaLdbGcVfPi63_x5ozWV3JyT--ZMHk_6JO5r6RmPI689GaRVuDyaemsoGuVQ2mnMfRqyH1w2r4Uxo0maVQkPBYKLeDlUrxVHwdVGCkmHFIemlRKwjlxjhrPosU2ugtkzNDx7Xw-HgC-vZqqxi2NGKn1TQrZE6abd_enA7c9qNGd-UHMciu1UojKduFD0OffEYYL5aoQ6Zwl6iok7JJg")

if not NEOSIA_TOKEN:
    logger.error("NEOSIA_TOKEN is missing in .env")
    sys.exit(1)

HEADERS = {
    "Authorization": f"Bearer {NEOSIA_TOKEN}",
    "Accept": "application/json"
}

# Mapping kode_status dari NeoSIA ke nama status yang dipakai di AIMS
NEOSIA_STATUS_MAP = {
    "A": "Aktif",
    "C": "Cuti",
    "L": "Lulus",
    "D": "Drop Out",
    "K": "Keluar",
    "P": "Pindah",
    "N": "Non Aktif",
}

def compute_risk(ipk: float) -> str:
    """Hitung klasifikasi risiko akademik berdasarkan IPK."""
    if ipk < 2.0:   return "HIGH_RISK"
    if ipk < 2.75:  return "Warning"
    return "Aman"

def sync_all_transcripts():
    db = SessionLocal()

    students = db.query(Student).all()
    logger.info(f"Memulai sinkronisasi {len(students)} mahasiswa dari NeoSIA...")

    courses_in_db = db.query(Course).all()
    course_cache = {c.kode: c.id for c in courses_in_db}

    total_added   = 0
    total_skipped = 0
    total_failed  = 0

    with httpx.Client(timeout=15.0, headers=HEADERS) as client:
        for idx, student in enumerate(students, 1):

            if idx % 50 == 0:
                logger.info(f"Progress: {idx}/{len(students)} | ✅{total_added} ❌{total_failed}")

            transkrip_url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={student.nim}"

            success = False
            for attempt in range(3):
                try:
                    response = client.get(transkrip_url)

                    if response.status_code == 404:
                        total_skipped += 1
                        success = True
                        break

                    response.raise_for_status()
                    data = response.json()

                    transkrips = data.get("transkrips", [])
                    ipk_dict   = data.get("current_indeks_prestasi", {})
                    ipk        = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)

                    added_courses = set()
                    total_sks     = sum(int(t.get("sks", 0) or 0) for t in transkrips if t.get("is_used") == 1)
                    max_semester  = 1

                    db.query(Grade).filter(Grade.student_id == student.id).delete()
                    grades_to_add = []

                    for t in transkrips:
                        if t.get("is_used") != 1:
                            continue

                        kode = t.get("kode_mata_kuliah")
                        if not kode:
                            continue

                        sks  = int(t.get("sks", 0) or 0)
                        nama = t.get("nama_mata_kuliah")
                        if not nama and t.get("mata_kuliah"):
                            nama = t.get("mata_kuliah").get("nama_resmi")
                        if not nama:
                            nama = "Unknown"

                        semester_data = t.get("semester", {})
                        try:
                            sem_val = int(t.get("mata_kuliah", {}).get("semester") or semester_data.get("kode", "1")[-1])
                        except Exception:
                            sem_val = 1

                        bobot       = float(t.get("nilai_angka") or 0.0)
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

                        grades_to_add.append(Grade(
                            student_id=student.id,
                            course_id=course_id,
                            semester=sem_val,
                            grade=nilai_huruf,
                            bobot=bobot
                        ))

                    db.add_all(grades_to_add)

                    # ─── Klasifikasi RISIKO (hanya untuk AcademicRecord) ────────────────
                    risk_status   = compute_risk(ipk)

                    # Estimasi semester berdasarkan angkatan
                    semester_calc = max(1, min(14, (2026 - student.angkatan) * 2)) if student.angkatan else max_semester

                    db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).delete()
                    db.add(AcademicRecord(
                        student_id=student.id,
                        semester=semester_calc,
                        ips=ipk,
                        ipk=ipk,
                        sks=total_sks,
                        status=risk_status        # ← HANYA klasifikasi risiko
                    ))

                    # ─── Update semester mahasiswa + STATUS DARI NEOSIA ─────────────────
                    # Ambil kode_status dari data transkrip (ada di field mahasiswa)
                    mhs_data    = data.get("mahasiswa", {})
                    kode_status = mhs_data.get("kode_status", "A")
                    enrollment_status = NEOSIA_STATUS_MAP.get(kode_status, "Aktif")

                    student.semester = semester_calc
                    student.status   = enrollment_status  # ← Status KEAKTIFAN dari NeoSIA

                    db.commit()
                    total_added += 1
                    success = True
                    break

                except httpx.HTTPError as e:
                    logger.warning(f"  [{attempt+1}/3] HTTP error untuk {student.nim}: {e}")
                    time.sleep(3)
                except Exception as e:
                    logger.error(f"  Error untuk {student.nim}: {e}")
                    db.rollback()
                    break

            if not success:
                total_failed += 1

            time.sleep(2.0)

    db.close()
    logger.info("=" * 60)
    logger.info(f"✅ Sync Selesai! Added: {total_added} | Skipped: {total_skipped} | Failed: {total_failed}")

if __name__ == "__main__":
    sync_all_transcripts()
