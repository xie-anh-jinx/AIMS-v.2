from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from typing import List
from packages.database.connection import get_db
from packages.database.models import Student, AcademicRecord, User
from packages.shared.schemas import DashboardOverview, StudentResponse
from apps.backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    subq = db.query(
        AcademicRecord.student_id,
        func.max(AcademicRecord.semester).label("max_semester")
    ).group_by(AcademicRecord.student_id).subquery()
        
    query_student = db.query(Student)
    query_active = db.query(Student).filter(Student.status == "Aktif")
    query_hr = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) & 
        (AcademicRecord.semester == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        AcademicRecord.ipk < 2.0, Student.status != "Lulus"
    )
    
    query_warn = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) & 
        (AcademicRecord.semester == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        AcademicRecord.ipk >= 2.0, AcademicRecord.ipk < 2.75, Student.status != "Lulus"
    )
    
    query_safe = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) & 
        (AcademicRecord.semester == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        AcademicRecord.ipk >= 2.75
    )
        
    total_students = query_student.count()
    total_active_students = query_active.count()
    high_risk_students = query_hr.count()
    warning_students = query_warn.count()
    safe_students = query_safe.count()
    
    total_reminders_sent = 0
    return DashboardOverview(
        total_students=total_students,
        total_active_students=total_active_students,
        high_risk_students=high_risk_students,
        warning_students=warning_students,
        safe_students=safe_students,
        total_reminders_sent=total_reminders_sent
    )

@router.get("/stats/semester")
def get_semester_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(
        Student.semester,
        func.count(Student.id).label("count")
    ).filter(Student.status == "Aktif").group_by(Student.semester).order_by(Student.semester).all()
    return [{"name": f"Sem {r.semester}", "value": r.count} for r in rows]

@router.get("/stats/status")
def get_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(
        Student.status,
        func.count(Student.id).label("count")
    ).group_by(Student.status).all()
    return [{"name": r.status, "value": r.count} for r in rows]

@router.get("/students/prodi-list")
def get_prodi_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(Student.prodi).distinct().order_by(Student.prodi).all()
    return [r.prodi for r in rows]

@router.get("/students/angkatan-list")
def get_angkatan_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(Student.angkatan).distinct().order_by(Student.angkatan.desc()).all()
    return [r.angkatan for r in rows]

@router.get("/students", response_model=List[StudentResponse])
def get_all_students_admin(
    skip: int = 0,
    limit: int = 100,
    prodi: str = None,
    angkatan: int = None,
    status: str = None,
    search: str = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    query = db.query(Student)
    if prodi:
        query = query.filter(Student.prodi == prodi)
    if angkatan:
        query = query.filter(Student.angkatan == angkatan)
    if status:
        query = query.filter(Student.status == status)
    if search:
        query = query.filter(
            (Student.nama.ilike(f"%{search}%")) | (Student.nim.ilike(f"%{search}%"))
        )
    return query.order_by(Student.nama).offset(skip).limit(limit).all()

@router.get("/risk-students", response_model=List[dict])
def get_risk_students(
    zone: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    subq = db.query(
        AcademicRecord.student_id,
        func.max(AcademicRecord.semester).label("max_semester")
    ).group_by(AcademicRecord.student_id).subquery()
    
    # We need to SELECT Student, AcademicRecord.ipk, and Advisor.nama
    from packages.database.models import Advisor
    
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

@router.get("/advisors")
def get_all_advisors(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    from packages.database.models import Advisor
    advisors = db.query(Advisor).all()
    return [{"id": a.id, "nama": a.nama} for a in advisors]

from pydantic import BaseModel
class AdminNoteCreate(BaseModel):
    advisor_id: int
    type: str
    status: str
    notes: str

@router.post("/advisor-notes")
def create_admin_note(
    payload: AdminNoteCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    from packages.database.models import AdminNote
    note = AdminNote(
        advisor_id=payload.advisor_id,
        type=payload.type,
        status=payload.status,
        notes=payload.notes
    )
    db.add(note)
    db.commit()
    return {"message": "Admin note created"}

@router.get("/advisor-notes/sent")
def get_sent_admin_notes(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    from packages.database.models import AdminNote, Advisor
    notes = db.query(AdminNote, Advisor).join(Advisor, AdminNote.advisor_id == Advisor.id).filter(
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
            "date": n.date.strftime("%Y-%m-%d %H:%M:%S")
        })
    return out

@router.delete("/advisor-notes/{note_id}")
def delete_admin_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    from packages.database.models import AdminNote
    note = db.query(AdminNote).filter(AdminNote.id == note_id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    
    # Soft delete for sender
    note.is_archived_by_sender = True
    db.commit()
    return {"message": "Note deleted"}
