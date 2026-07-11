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
            
    raise HTTPException(status_code=403, detail="Tidak memiliki hak akses untuk data mahasiswa ini")

@router.get("/", response_model=List[StudentResponse])
def get_students(skip: int = 0, limit: int = 5000, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    query = db.query(Student)
    if current_user.role == "ADVISOR":
        advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
        if advisor:
            query = query.filter(Student.advisor_id == advisor.id)
            query = query.filter(Student.status != 'Lulus')
        else:
            return []

    return query.offset(skip).limit(limit).all()

@router.get("/{nim}", response_model=StudentResponse)
def get_student(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)
    return student

@router.get("/{nim}/transcript", response_model=List[GradeResponse])
def get_student_transcript(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    student = db.query(Student).filter(Student.nim == nim).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    check_student_access(student, current_user, db)

    # --- Attempt Neosia API (real data source) and Sync DB ---
    if NEOSIA_TOKEN:
        try:
            neosia_url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={nim}"
            headers = {"Authorization": f"Bearer {NEOSIA_TOKEN}", "Accept": "application/json"}
            with httpx.Client(timeout=10) as client:
                r = client.get(neosia_url, headers=headers)
            if r.status_code == 200:
                data = r.json()
                transkrips = data.get("transkrips", [])
                if transkrips:
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

                        # 2. Upsert Grade
                        grade = db.query(Grade).filter(Grade.student_id == student.id, Grade.course_id == course.id).first()
                        val_huruf = t.get("nilai_huruf", "-")
                        val_angka = float(t.get("nilai_angka") or 0)
                        
                        if not grade:
                            grade = Grade(
                                student_id=student.id,
                                course_id=course.id,
                                semester=calculated_sem,
                                grade=val_huruf,
                                bobot=val_angka
                            )
                            db.add(grade)
                        else:
                            grade.semester = calculated_sem
                            grade.grade = val_huruf
                            grade.bobot = val_angka
                            
                    db.commit() # Save all synced data to postgres
        except Exception as e:
            print(f"[WARN] Neosia transcript fetch failed for {nim}: {e}")

    # --- Fallback & Normalized Return: local DB ---
    grades = db.query(Grade).filter(Grade.student_id == student.id).all()
    return grades

@router.get("/{nim}/records", response_model=List[AcademicRecordResponse])
def get_student_records(nim: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
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
        
    logs = db.query(ConsultationLog).filter(ConsultationLog.student_id == student.id).order_by(ConsultationLog.date.desc()).all()
    
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
