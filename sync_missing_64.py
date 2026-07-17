import os, sys, time, json, urllib.request
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

def compute_status(ipk: float) -> str:
    if ipk < 2.0: return "HIGH_RISK"
    if ipk < 2.75: return "Warning"
    return "Aman"

def sync_missing():
    db = SessionLocal()
    token = os.environ.get("NEOSIA_TOKEN")
    if not token: sys.exit("No token")
    
    # Get students without records
    students = db.query(Student).filter(
        Student.status == "Aktif", 
        ~Student.id.in_(db.query(AcademicRecord.student_id))
    ).all()
    
    print(f"Found {len(students)} students missing records. Syncing...")
    
    for idx, student in enumerate(students):
        url = f"https://api.neosia.unhas.ac.id/api/admin/transkrip/getTranskripMahasiswa?nim={student.nim}"
        req = urllib.request.Request(url)
        req.add_header("Authorization", f"Bearer {token}")
        
        try:
            with urllib.request.urlopen(req) as response:
                data = json.loads(response.read())
                
                ipk_dict = data.get("current_indeks_prestasi", {})
                ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
                
                transkrips = data.get("transkrips", [])
                valid_sks = sum(int(t.get("sks", 0) or 0) for t in transkrips if t.get("is_used") == 1)
                
                status_text = compute_status(ipk)
                if ipk == 0.0 and valid_sks == 0:
                    status_text = "Baru/Cuti"
                    
                semester_calc = max(1, min(14, (2026 - student.angkatan) * 2)) if student.angkatan else 2
                
                rec = AcademicRecord(
                    student_id=student.id,
                    semester=semester_calc,
                    ipk=ipk,
                    ips=ipk,
                    sks=valid_sks,
                    status=status_text
                )
                db.add(rec)
                
                student.semester = semester_calc
                student.status = status_text if status_text != "Baru/Cuti" else "Aktif"
                
                db.commit()
                print(f"[{idx+1}/{len(students)}] Synced {student.nim}: IPK {ipk}, SKS {valid_sks}, Status {status_text}")
                
        except Exception as e:
            db.rollback()
            print(f"[{idx+1}/{len(students)}] Error {student.nim}: {e}")
            
        time.sleep(1.0)
        
    db.close()

if __name__ == "__main__":
    sync_missing()
