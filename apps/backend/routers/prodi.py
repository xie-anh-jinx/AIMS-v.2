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
        student = next((s for s in students if s.id == uid), None)
        if not student or student.status == "Lulus":
            continue
            
        if r.ipk < 2.0: high_risk += 1
        elif 2.0 <= r.ipk < 2.75: warning += 1
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

@router.get("/stats/semester")
def stats_semester(db: Session = Depends(get_db), prodi_admin: ProdiAdmin = Depends(get_prodi_user)):
    res = db.query(Student.semester, func.count(Student.id)).filter(Student.prodi == prodi_admin.prodi_name, Student.status == "Aktif").group_by(Student.semester).all()
    out = [{"name": f"Sm {s[0]}", "value": s[1]} for s in res if s[0]]
    out.sort(key=lambda x: int(x["name"].split(" ")[1]))
    return out

@router.get("/risk-students")
def get_prodi_risk_students(
    zone: str, 
    db: Session = Depends(get_db), 
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    subq = db.query(
        AcademicRecord.student_id,
        func.max(AcademicRecord.semester).label("max_semester")
    ).group_by(AcademicRecord.student_id).subquery()
    
    query = db.query(
        Student, 
        AcademicRecord.ipk, 
        Advisor.nama.label("advisor_name")
    ).join(
        AcademicRecord, 
        Student.id == AcademicRecord.student_id
    ).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) & 
        (AcademicRecord.semester == subq.c.max_semester)
    ).outerjoin(
        Advisor,
        Student.advisor_id == Advisor.id
    ).filter(
        Student.prodi == prodi_admin.prodi_name
    )
    
    if zone == "merah":
        query = query.filter(AcademicRecord.ipk < 2.0, Student.status != "Lulus")
    elif zone == "kuning":
        query = query.filter(AcademicRecord.ipk >= 2.0, AcademicRecord.ipk < 2.75, Student.status != "Lulus")
    elif zone == "hijau":
        query = query.filter(AcademicRecord.ipk >= 2.75)
        
    results = query.all()
    out = []
    for st, ipk, adv_name in results:
        out.append({
            "id": st.id,
            "nama": st.nama,
            "nim": st.nim,
            "prodi": st.prodi,
            "semester": st.semester,
            "status": st.status,
            "angkatan": st.angkatan,
            "ipk": ipk,
            "advisor_name": adv_name or "Belum Ditentukan"
        })
    return out

from pydantic import BaseModel
class ProdiNoteCreate(BaseModel):
    advisor_id: int
    type: str
    status: str
    notes: str

@router.post("/advisor-notes")
def create_prodi_note(
    payload: ProdiNoteCreate,
    db: Session = Depends(get_db),
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    advisor = db.query(Advisor).filter(Advisor.id == payload.advisor_id, Advisor.prodi == prodi_admin.prodi_name).first()
    if not advisor:
        raise HTTPException(status_code=400, detail="Penasihat Akademik tidak ditemukan di prodi ini")
        
    note = AdminNote(
        advisor_id=payload.advisor_id,
        type=payload.type,
        status=payload.status,
        notes=payload.notes
    )
    db.add(note)
    db.commit()
    return {"message": "Catatan berhasil dikirim"}

@router.get("/advisor-notes/sent")
def get_sent_prodi_notes(
    db: Session = Depends(get_db),
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    notes = db.query(AdminNote, Advisor).join(Advisor, AdminNote.advisor_id == Advisor.id).filter(
        Advisor.prodi == prodi_admin.prodi_name,
        AdminNote.is_archived_by_sender == False
    ).order_by(AdminNote.date.desc()).all()
    
    out = []
    for n, adv in notes:
        out.append({
            "id": n.id,
            "advisor_name": adv.nama,
            "type": n.type,
            "status": n.status,
            "notes": n.notes,
            "date": n.date.strftime("%d %b %Y, %H:%M")
        })
    return out

@router.delete("/advisor-notes/{note_id}")
def delete_prodi_note(
    note_id: int,
    db: Session = Depends(get_db),
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    note = db.query(AdminNote).join(Advisor, AdminNote.advisor_id == Advisor.id).filter(
        AdminNote.id == note_id,
        Advisor.prodi == prodi_admin.prodi_name
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    
    note.is_archived_by_sender = True
    db.commit()
    return {"message": "Catatan dihapus dari riwayat terkirim"}
