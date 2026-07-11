from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime
from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student, ConsultationLog
from apps.backend.routers.auth import get_current_user
from pydantic import BaseModel
import bcrypt

router = APIRouter(prefix="/advisor", tags=["advisor"])

class AdvisorProfileUpdateRequest(BaseModel):
    username: str = None
    password: str = None
    email: str = None
    whatsapp: str = None
    telegram_username: str = None

@router.get("/consultations", response_model=List[Dict[str, Any]])
def get_consultations(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403, detail="Hanya Advisor yang diizinkan")
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        return []
    
    logs = db.query(ConsultationLog).filter(
        ConsultationLog.advisor_id == advisor.id,
        ConsultationLog.is_archived_by_sender == False
    ).order_by(ConsultationLog.date.desc()).all()
    
    res = []
    for log in logs:
        student = db.query(Student).filter(Student.id == log.student_id).first()
        res.append({
            "id": log.id,
            "nama": student.nama if student else "Mahasiswa Unknown",
            "nim": student.nim if student else "",
            "date": log.date.strftime("%d %b %Y, %H:%M"),
            "type": log.type,
            "status": log.status,
            "notes": log.notes
        })
    return res

@router.post("/consultations")
def add_consultation(
    payload: Dict[str, Any] = Body(...),
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403)
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Profil Advisor tidak ditemukan")
        
    student = db.query(Student).filter(Student.nim == payload.get("nim")).first()
    if not student:
        raise HTTPException(status_code=404, detail="Mahasiswa tidak ditemukan")
        
    log = ConsultationLog(
        student_id=student.id,
        advisor_id=advisor.id,
        type=payload.get("type", "Konsultasi Umum"),
        status=payload.get("status", "Selesai"),
        notes=payload.get("notes", "")
    )
    db.add(log)
    db.commit()
    return {"status": "success"}

@router.patch("/consultations/{log_id}/archive")
def archive_consultation(
    log_id: int,
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403, detail="Hanya Advisor yang diizinkan")
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Profil Advisor tidak ditemukan")
        
    log = db.query(ConsultationLog).filter(ConsultationLog.id == log_id, ConsultationLog.advisor_id == advisor.id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Log tidak ditemukan")
        
    log.is_archived_by_sender = True
    db.commit()
    return {"message": "Catatan berhasil dihapus dari riwayat Anda"}

@router.put("/profile")
def update_advisor_profile(
    payload: AdvisorProfileUpdateRequest, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403, detail="Hanya Advisor yang diizinkan")

    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Profil Advisor tidak ditemukan")

    # Update Advisor Data
    if payload.email is not None:
        advisor.email = payload.email
    if payload.whatsapp is not None:
        advisor.whatsapp = payload.whatsapp
    if payload.telegram_username is not None:
        advisor.telegram_username = payload.telegram_username
        
    # Update linked User credentials
    user = db.query(User).filter(User.id == advisor.user_id).first()
    if user:
        if payload.username and payload.username.strip():
            # Check for conflict
            conflict = db.query(User).filter(User.username == payload.username, User.id != user.id).first()
            if conflict:
                raise HTTPException(status_code=400, detail="Username sudah digunakan oleh akun lain")
            user.username = payload.username
            
        if payload.password and payload.password.strip():
            hashed_pw = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
            user.hashed_password = hashed_pw

    db.commit()
    return {"message": "Profil berhasil diperbarui"}

@router.get("/admin-notes", response_model=List[Dict[str, Any]])
def get_admin_notes(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403, detail="Hanya Advisor yang diizinkan")
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        return []
    
    from packages.database.models import AdminNote
    notes = db.query(AdminNote).filter(
        AdminNote.advisor_id == advisor.id,
        AdminNote.is_archived_by_receiver == False
    ).order_by(AdminNote.date.desc()).all()
    
    res = []
    for note in notes:
        res.append({
            "id": note.id,
            "date": note.date.strftime("%d %b %Y, %H:%M"),
            "type": note.type,
        })
    return res

@router.patch("/admin-notes/{note_id}/archive")
def archive_admin_note(
    note_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADVISOR":
        raise HTTPException(status_code=403, detail="Hanya Advisor yang diizinkan")
    
    advisor = db.query(Advisor).filter(Advisor.user_id == current_user.id).first()
    if not advisor:
        raise HTTPException(status_code=404, detail="Profil Advisor tidak ditemukan")
        
    from packages.database.models import AdminNote
    note = db.query(AdminNote).filter(AdminNote.id == note_id, AdminNote.advisor_id == advisor.id).first()
    if not note:
        raise HTTPException(status_code=404, detail="Catatan admin tidak ditemukan")
        
    if note.status != "Selesai":
        raise HTTPException(status_code=400, detail="Hanya catatan yang sudah 'Selesai' yang bisa dihapus")
        
    note.is_archived_by_receiver = True
    db.commit()
    return {"message": "Catatan admin berhasil dihapus dari riwayat Anda"}
