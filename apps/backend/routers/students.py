from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Dict, Any, Optional
from packages.database.connection import get_db
from packages.database.models import Student, AcademicRecord, Grade, Course, ConsultationLog, User
from packages.shared.schemas import StudentResponse, AcademicRecordResponse, GradeResponse
from pydantic import BaseModel
import bcrypt
import os
import httpx
from apps.backend.routers.auth import get_current_user
from packages.database.models import User, Advisor

NEOSIA_TOKEN = os.getenv("NEOSIA_TOKEN", "")
NEOSIA_API_BASE = os.getenv("NEOSIA_API_BASE", "https://api.neosia.unhas.ac.id")

router = APIRouter(prefix="/students", tags=["students"])

class ProfileUpdateRequest(BaseModel):
    username: str = None
    password: str = None
    email: str = None
    phone_number_wa: str = None
    telegram_username: str = None

def check_student_access(student: Student, current_user: User, db: Session):
    if current_user.role == "ADMIN":
        return

    elif current_user.role == "STUDENT":
        if student.user_id == current_user.id:
            return
    elif current_user.role == "ADVISOR":
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        if advisor and student.advisor_id == advisor.id:
            return
    
    elif current_user.role == "PRODI":
        from packages.database.models import ProdiAdmin
        prodi_admin = db.query(ProdiAdmin).filter(ProdiAdmin.user_id == current_user.id).first()
        if prodi_admin and student.prodi == prodi_admin.prodi_name:
            return
            
    raise HTTPException(status_code=403, detail="Tidak memiliki hak akses untuk data mahasiswa ini")

@router.get("/", response_model=List[StudentResponse])
def get_students(
    skip: int = 0,
    limit: int = 5000,
    include_do: bool = False,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    query = db.query(Student)
    if current_user.role == "ADVISOR":
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        if advisor:
            query = query.filter(Student.advisor_id == advisor.id)
            if not include_do:
                # Default: only show active + cuti students in main list
                query = query.filter(Student.status.in_(['Aktif', 'Cuti']))
        else:
            return []
    elif current_user.role == "STUDENT":
        query = query.filter(Student.user_id == current_user.id)

    return query.offset(skip).limit(limit).all()

@router.get("/{nim}", response_model=StudentResponse)
def get_student(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)
    return student

@router.get("/{nim}/transcript", response_model=List[GradeResponse])
def get_student_transcript(
    nim: str, 
    force_sync: bool = False,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)

    # Check if we already have cache in local DB
    has_grades = db.query(Grade).filter(Grade.student_id == student.id).first() is not None

    # --- Attempt Neosia API (real data source) and Sync DB ---
    # Only request Neosia API if we don't have grades yet or force_sync is requested
    if NEOSIA_TOKEN and (not has_grades or force_sync):
        try:
            neosia_url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={nim}"
            headers = {"Authorization": f"Bearer {NEOSIA_TOKEN}", "Accept": "application/json"}
            with httpx.Client(timeout=10) as client:
                r = client.get(neosia_url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                transkrips = data.get("transkrips", [])
                
                # Update AcademicRecord immediately from Neosia payload
                ipk_dict = data.get("current_indeks_prestasi", {})
                real_ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
                
                status_str = "Aman"
                if real_ipk < 2.0: status_str = "HIGH_RISK"
                elif real_ipk < 2.75: status_str = "Warning"
                
                valid_sks = sum(int(t.get("sks") or 0) for t in transkrips if t.get("is_used") == 1)
                latest_rec = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).first()
                if latest_rec:
                    latest_rec.ipk = real_ipk
                    latest_rec.sks = valid_sks
                    latest_rec.status = status_str
                else:
                    new_rec = AcademicRecord(student_id=student.id, semester=student.semester or 2, ipk=real_ipk, ips=real_ipk, sks=valid_sks, status=status_str)
                    db.add(new_rec)
                
                if transkrips:
                    # Wipe dirty polluted grades from old syncing bug
                    db.query(Grade).filter(Grade.student_id == student.id).delete()
                    
                    for t in transkrips:
                        if t.get("is_used") != 1: continue
                        
                        kode_mk = t.get("kode_mata_kuliah")
                        if not kode_mk: continue
                            
                        # 1. Upsert Course
                        course = db.query(Course).filter(Course.kode == kode_mk).first()
                        if not course:
                            course = Course(
                                kode=kode_mk,
                                nama=t.get("nama_mata_kuliah", "Mata Kuliah"),
                                sks=int(t.get("sks") or 0),
                                semester=t.get("id_semester")
                            )
                            db.add(course)
                            db.flush() # flush to get course.id
                        else:
                            course.nama = t.get("nama_mata_kuliah", course.nama)
                            course.sks = int(t.get("sks") or course.sks)
                        
                        # Hitung Semester Relatif
                        calculated_sem = t.get("id_semester")
                        sem_obj = t.get("semester")
                        if sem_obj and student.angkatan:
                            tahun = sem_obj.get("tahun")
                            jenis = sem_obj.get("jenis")
                            if tahun:
                                try:
                                    diff = int(tahun) - int(student.angkatan)
                                    if jenis == "ganjil":
                                        calculated_sem = diff * 2 + 1
                                    elif jenis == "genap":
                                        calculated_sem = diff * 2 + 2
                                    elif jenis == "awal": # Semester pendek
                                        calculated_sem = diff * 2 + 3
                                except:
                                    pass

                        # 2. Insert Valid Grade
                        val_huruf = t.get("nilai_huruf", "-")
                        val_angka = float(t.get("nilai_angka") or 0)
                        
                        grade = Grade(
                            student_id=student.id,
                            course_id=course.id,
                            semester=calculated_sem,
                            grade=val_huruf,
                            bobot=val_angka
                        )
                        db.add(grade)
                            
                    db.commit() # Save all synced data to postgres
        except Exception as e:
            print(f"[WARN] Neosia transcript fetch failed for {nim}: {e}")

    # --- Fallback & Normalized Return: local DB ---
    grades = db.query(Grade).filter(Grade.student_id == student.id).all()
    return grades

@router.get("/{nim}/records", response_model=List[AcademicRecordResponse])
def get_student_records(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    from sqlalchemy import func
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)
    records = db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).order_by(AcademicRecord.semester.desc()).all()

    return records

@router.get("/{nim}/consultations", response_model=List[Dict[str, Any]])
def get_student_consultations(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)
        
    logs = db.query(ConsultationLog).filter(
        ConsultationLog.student_id == student.id,
        ConsultationLog.is_archived_by_receiver == False
    ).order_by(ConsultationLog.date.desc()).all()
    
    res = []
    for log in logs:
        advisor = db.query(Advisor).filter(Advisor.id == log.advisor_id).first()
        res.append({
            "id": log.id,
            "advisor_name": advisor.nama if advisor else "Pembimbing Akademik",
            "date": log.date.strftime("%d %b %Y, %H:%M"),
            "type": log.type,
            "status": log.status,
            "notes": log.notes
        })
    return res

@router.patch("/{nim}/consultations/{log_id}/archive")
def archive_student_consultation(
    nim: str,
    log_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)
        
    log = db.query(ConsultationLog).filter(ConsultationLog.id == log_id, ConsultationLog.student_id == student.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Consultation log not found")
        
    if log.status != "Selesai":
        raise HTTPException(status_code=400, detail="Hanya catatan yang sudah Selesai yang bisa disembunyikan")
        
    log.is_archived_by_receiver = True
    db.commit()
    return {"message": "Catatan berhasil dihapus dari riwayat Anda"}

@router.put("/{nim}/profile")
def update_student_profile(nim: str, payload: ProfileUpdateRequest, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
        
    # Only self (STUDENT) or ADMIN can edit
    if current_user.role == "STUDENT" and current_user.id != student.user_id:
        raise HTTPException(status_code=403, detail="Tidak diizinkan mengubah profil mahasiswa lain")

    elif current_user.role == "ADVISOR":
        raise HTTPException(status_code=403, detail="Pembimbing Akademik tidak diizinkan mengubah profil mahasiswa")

    # Update Student Data
    if payload.email is not None:
        student.email = payload.email
    if payload.phone_number_wa is not None:
        student.phone_number_wa = payload.phone_number_wa
        student.nomor_whatsapp = payload.phone_number_wa
    if payload.telegram_username is not None:
        student.telegram_username = payload.telegram_username
        
    # Update linked User credentials
    user = db.query(User).filter(User.id == student.user_id).first()
    if user:
        if payload.username and payload.username.strip():
            conflict = db.query(User).filter(User.username == payload.username, User.id != user.id).first()
            if conflict:
                raise HTTPException(status_code=400, detail="Username sudah digunakan oleh akun lain")
            user.username = payload.username
            
        if payload.password and payload.password.strip():
            hashed_pw = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.hashed_password = hashed_pw

    db.commit()
    return {"message": "Profil berhasil diperbarui"}

@router.get("/{nim}/neosia-status")
def get_student_neosia_status_endpoint(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)

    if not NEOSIA_TOKEN:
        return {
            "nim": student.nim,
            "nama": student.nama,
            "status_krs": "BELUM_KRS",
            "sudah_bayar": False,
            "nominal_spp": 2000000,
            "tahun_ajaran": "2026/2027",
            "semester_jenis": "ganjil"
        }

    try:
        # Standardize matching name
        std_prodi = student.prodi.upper().strip() if student.prodi else ""
        if std_prodi and not std_prodi.endswith("- S1") and not std_prodi.endswith("- S2") and not std_prodi.endswith("- S3"):
            std_prodi = f"{std_prodi} - S1"

        url_ps = f"{NEOSIA_API_BASE}/api/admin/prodi_semester?filters[is_used]=1"
        headers = {"Authorization": f"Bearer {NEOSIA_TOKEN}", "Accept": "application/json"}
        
        with httpx.Client(timeout=15) as client:
            r_ps = client.get(url_ps, headers=headers)
            if r_ps.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch active semesters from Neosia")
            
            ps_arr = r_ps.json().get("prodiSemesters") or r_ps.json().get("data") or []
            matched_ps = None
            for ps in ps_arr:
                p_name = (ps.get("prodi") or {}).get("nama_resmi", "").upper()
                if std_prodi in p_name or p_name in std_prodi:
                    matched_ps = ps
                    break
            
            if not matched_ps:
                for ps in ps_arr:
                    p_name = (ps.get("prodi") or {}).get("nama_resmi", "").upper()
                    if any(w in p_name for w in std_prodi.split() if len(w) > 3):
                        matched_ps = ps
                        break

            if not matched_ps:
                id_prodi = 33
                id_prodi_semester = 3850
                sem_year = "2026/2027"
                sem_term = "ganjil"
            else:
                id_prodi = matched_ps["id_prodi"]
                id_prodi_semester = matched_ps["id"]
                sem_year = matched_ps.get("semester", {}).get("tahun_ajaran", "2026/2027")
                sem_term = matched_ps.get("semester", {}).get("jenis", "ganjil")

            # Query status_krs
            url_krs = f"{NEOSIA_API_BASE}/api/admin/mahasiswa/status_krs?filters[id_prodi]={id_prodi}&filters[angkatan]={student.angkatan or 2024}&filters[id_prodi_semester]={id_prodi_semester}"
            r_krs = client.get(url_krs, headers=headers)
            if r_krs.status_code != 200:
                raise HTTPException(status_code=502, detail="Failed to fetch KRS status from Neosia")

            krs_data = r_krs.json()
            mahasiswas = krs_data.get("mahasiswas", {})
            
            sudah_krs = mahasiswas.get("sudah_krs", [])
            belum_krs = mahasiswas.get("belum_krs", [])
            
            target_nim = student.nim.upper().strip()
            found_mhs = None
            status_krs = "BELUM_KRS"
            
            for m in sudah_krs:
                m_info = m.get("mahasiswa") or m
                if str(m_info.get("nim", "")).upper().strip() == target_nim:
                    found_mhs = m_info
                    status_krs = "SUDAH_KRS"
                    break
                    
            if not found_mhs:
                for m in belum_krs:
                    m_info = m.get("mahasiswa") or m
                    if str(m_info.get("nim", "")).upper().strip() == target_nim:
                        found_mhs = m_info
                        status_krs = "BELUM_KRS"
                        break
                        
            if not found_mhs:
                return {
                    "nim": student.nim,
                    "nama": student.nama,
                    "status_krs": "BELUM_KRS",
                    "sudah_bayar": False,
                    "nominal_spp": 2000000,
                    "tahun_ajaran": sem_year,
                    "semester_jenis": sem_term
                }

            pay_info = found_mhs.get("statusPembayaran") or {}
            sudah_bayar = pay_info.get("sudah_bayar") == 1
            nominal = pay_info.get("nominal") or found_mhs.get("spp")
            
            return {
                "nim": target_nim,
                "nama": found_mhs.get("nama_mahasiswa"),
                "status_krs": status_krs,
                "sudah_bayar": sudah_bayar,
                "nominal_spp": nominal,
                "tahun_ajaran": sem_year,
                "semester_jenis": sem_term
            }
    except Exception:
        return {
            "nim": student.nim,
            "nama": student.nama,
            "status_krs": "BELUM_KRS",
            "sudah_bayar": False,
            "nominal_spp": 2000000,
            "tahun_ajaran": "2026/2027",
            "semester_jenis": "ganjil"
        }
