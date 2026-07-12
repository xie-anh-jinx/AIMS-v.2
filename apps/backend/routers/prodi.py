from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List, Optional

from packages.database.connection import get_db
from packages.database.models import User, Student, Advisor, AcademicRecord, ConsultationLog, AdminNote, ProdiAdmin
from .auth import get_current_user

router = APIRouter(
    prefix="/prodi",
    tags=["Prodi Dashboard"]
)

def get_prodi_user(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "PRODI":
        raise HTTPException(status_code=403, detail="Akses ditolak. Membutuhkan izin Prodi.")
    prodi_admin = db.query(ProdiAdmin).filter(ProdiAdmin.user_id == current_user.id).first()
    if not prodi_admin:
        raise HTTPException(status_code=403, detail="Akses ditolak. Profil Kaprodi tidak ditemukan.")
    return prodi_admin

@router.get("/overview")
def get_overview(db: Session = Depends(get_db), prodi_admin: ProdiAdmin = Depends(get_prodi_user)):
    students = db.query(Student).filter(Student.prodi == prodi_admin.prodi_name).all()
    student_ids = [s.id for s in students]
    active_count = len([s for s in students if s.status == "Aktif"])
    
    # Analyze records for these students
    records = db.query(AcademicRecord).filter(AcademicRecord.student_id.in_(student_ids)).all()
    latest_records = {}
    for r in records:
        if r.student_id not in latest_records or r.semester > latest_records[r.student_id].semester:
            latest_records[r.student_id] = r
            
    high_risk, warning, safe = 0, 0, 0
    for uid, r in latest_records.items():
        if r.status == "HIGH_RISK": high_risk += 1
        elif r.status == "Warning": warning += 1
        else: safe += 1
        
    return {
        "total_students": len(students),
        "total_active_students": active_count,
        "high_risk_students": high_risk,
        "warning_students": warning,
        "safe_students": safe,
        "total_advisors": db.query(Advisor).filter(Advisor.prodi == prodi_admin.prodi_name).count()
    }

@router.get("/students")
def get_prodi_students(
    limit: int = 50, 
    skip: int = 0, 
    angkatan: Optional[int] = None, 
    status: Optional[str] = None, 
    search: Optional[str] = None,
    db: Session = Depends(get_db), 
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    query = db.query(Student).filter(Student.prodi == prodi_admin.prodi_name)
    
    if angkatan: query = query.filter(Student.angkatan == angkatan)
    if status: query = query.filter(Student.status == status)
    if search:
        search_filter = f"%{search}%"
        query = query.filter((Student.nama.ilike(search_filter)) | (Student.nim.ilike(search_filter)))
        
    return query.offset(skip).limit(limit).all()

@router.get("/advisors")
def get_prodi_advisors(db: Session = Depends(get_db), prodi_admin: ProdiAdmin = Depends(get_prodi_user)):
    advisors = db.query(Advisor).filter(Advisor.prodi == prodi_admin.prodi_name).all()
    results = []
    for adv in advisors:
        student_count = db.query(Student).filter(Student.advisor_id == adv.id).count()
        consultations = db.query(ConsultationLog).filter(ConsultationLog.advisor_id == adv.id).count()
        warnings_sent = db.query(AdminNote).filter(AdminNote.advisor_id == adv.id).count()
        results.append({
            "id": adv.id,
            "nama": adv.nama,
            "student_count": student_count,
            "total_consultations": consultations,
            "warnings_sent": warnings_sent
        })
    return results

@router.get("/stats/angkatan")
def stats_angkatan(db: Session = Depends(get_db), prodi_admin: ProdiAdmin = Depends(get_prodi_user)):
    res = db.query(Student.angkatan, func.count(Student.id)).filter(Student.prodi == prodi_admin.prodi_name).group_by(Student.angkatan).all()
    return [{"name": str(s[0]), "value": s[1]} for s in res]

@router.get("/stats/status")
def stats_status(db: Session = Depends(get_db), prodi_admin: ProdiAdmin = Depends(get_prodi_user)):
    res = db.query(Student.status, func.count(Student.id)).filter(Student.prodi == prodi_admin.prodi_name).group_by(Student.status).all()
    return [{"name": s[0], "value": s[1]} for s in res]
