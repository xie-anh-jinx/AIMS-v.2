from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from typing import List
from packages.database.connection import get_db
from packages.database.models import Student, AcademicRecord, User, Advisor
from packages.shared.schemas import DashboardOverview, StudentResponse
from apps.backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

# ─── Batas Risiko Akademik (Referensi: Aturan Akademik Unhas) ──────
IPK_HIGH_RISK  = 2.00   # IPK < 2.00 → Zona Merah
IPK_WARNING    = 2.75   # IPK < 2.75 → Zona Kuning  
MAX_STUDY_YRS  = 5      # Lebih dari 5 tahun aktif (S1) → Zona Kuning

def _classify_active_student(angkatan: int, current_year: int = 2026) -> str:
    """Klasifikasi risiko mahasiswa Aktif tanpa data IPK,
    berdasarkan lama studi (indikator awal yang valid secara akademis)."""
    years_enrolled = current_year - angkatan
    if years_enrolled >= 7:    # > 7 tahun = potensi DO sangat tinggi
        return "merah"
    elif years_enrolled >= MAX_STUDY_YRS:  # > 5 tahun = peringatan
        return "kuning"
    else:
        return "hijau"  # Belum melewati batas normal

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

    total_students       = db.query(Student).count()
    total_active_students = db.query(Student).filter(Student.status == "Aktif").count()

    # Mahasiswa dengan AcademicRecord → gunakan status kolom dulu atau IPK asli
    query_hr = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        Student.status != "Lulus",
        or_(AcademicRecord.status == "HIGH_RISK", AcademicRecord.ipk < IPK_HIGH_RISK)
    )
    query_warn = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        Student.status != "Lulus",
        AcademicRecord.status != "HIGH_RISK",
        or_(AcademicRecord.status == "Warning", (AcademicRecord.ipk >= IPK_HIGH_RISK) & (AcademicRecord.ipk < IPK_WARNING))
    )
    query_safe = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        AcademicRecord.status != "HIGH_RISK",
        AcademicRecord.status != "Warning",
        or_(AcademicRecord.status == "Aman", AcademicRecord.ipk >= IPK_WARNING)
    )

    high_risk_base = query_hr.count()
    warning_base   = query_warn.count()
    safe_base      = query_safe.count()

    # Mahasiswa Aktif tanpa AcademicRecord → estimasi dari lama studi
    rec_ids = db.query(AcademicRecord.student_id).distinct().subquery()
    active_no_rec = db.query(Student).filter(
        Student.status == "Aktif",
        ~Student.id.in_(db.query(rec_ids.c.student_id))
    ).all()

    for s in active_no_rec:
        z = _classify_active_student(s.angkatan)
        if z == "merah":   high_risk_base += 1
        elif z == "kuning": warning_base   += 1
        else:               safe_base      += 1

    return DashboardOverview(
        total_students        = total_students,
        total_active_students = total_active_students,
        high_risk_students    = high_risk_base,
        warning_students      = warning_base,
        safe_students         = safe_base,
        total_reminders_sent  = 0
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

@router.get("/stats/risk-per-prodi")
def get_risk_status_per_prodi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")

    subq = db.query(
        AcademicRecord.student_id,
        func.max(AcademicRecord.semester).label("max_semester")
    ).group_by(AcademicRecord.student_id).subquery()
    
    prodi_counts = {}

    # ── 1. Mahasiswa dengan AcademicRecord (IPK asli dari status Neosia) ──
    students_rec = db.query(
        Student.prodi,
        Student.status,
        AcademicRecord.ipk,
        AcademicRecord.status.label("status_rec")
    ).join(
        AcademicRecord, Student.id == AcademicRecord.student_id
    ).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).filter(Student.status != "Lulus").all()

    for s in students_rec:
        prodi = s.prodi or "Tidak Diketahui"
        if prodi not in prodi_counts:
            prodi_counts[prodi] = {"merah": 0, "kuning": 0, "hijau": 0}
        ipk = s.ipk or 0.0
        status_rec = s.status_rec
        if status_rec == "HIGH_RISK" or ipk < IPK_HIGH_RISK:
            prodi_counts[prodi]["merah"]  += 1
        elif status_rec == "Warning" or (ipk < IPK_WARNING and status_rec != "HIGH_RISK"):
            prodi_counts[prodi]["kuning"] += 1
        else:
            prodi_counts[prodi]["hijau"]  += 1

    # ── 2. Mahasiswa Aktif tanpa AcademicRecord → klasifikasi lama studi ──
    rec_ids = db.query(AcademicRecord.student_id).distinct().subquery()
    active_no_rec = db.query(Student).filter(
        Student.status == "Aktif",
        ~Student.id.in_(db.query(rec_ids.c.student_id))
    ).all()

    for s in active_no_rec:
        prodi = s.prodi or "Tidak Diketahui"
        if prodi not in prodi_counts:
            prodi_counts[prodi] = {"merah": 0, "kuning": 0, "hijau": 0}
        z = _classify_active_student(s.angkatan)
        prodi_counts[prodi][z] += 1

    # Eksklusi prodi tidak relevan & urutkan berdasarkan total
    out = [
        {"prodi": k, "Merah": v["merah"], "Kuning": v["kuning"], "Hijau": v["hijau"]}
        for k, v in prodi_counts.items()
        if v["merah"] + v["kuning"] + v["hijau"] > 0
    ]
    out.sort(key=lambda x: x["Merah"] + x["Kuning"] + x["Hijau"], reverse=True)
    return out

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
    
    # Mahasiswa dengan AcademicRecord (IPK dari status Neosia)
    query = db.query(
        Student, 
        AcademicRecord.ipk, 
        AcademicRecord.status.label("rec_status"),
        Advisor.nama.label("advisor_name")
    ).join(
        AcademicRecord, Student.id == AcademicRecord.student_id
    ).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) & 
        (AcademicRecord.semester   == subq.c.max_semester)
    ).outerjoin(Advisor, Student.advisor_id == Advisor.id)
    
    if zone == "merah":
        query = query.filter(
            Student.status != "Lulus",
            or_(AcademicRecord.status == "HIGH_RISK", AcademicRecord.ipk < IPK_HIGH_RISK)
        )
    elif zone == "kuning":
        query = query.filter(
            Student.status != "Lulus",
            AcademicRecord.status != "HIGH_RISK",
            or_(AcademicRecord.status == "Warning", (AcademicRecord.ipk >= IPK_HIGH_RISK) & (AcademicRecord.ipk < IPK_WARNING))
        )
    elif zone == "hijau":
        query = query.filter(
            AcademicRecord.status != "HIGH_RISK",
            AcademicRecord.status != "Warning",
            or_(AcademicRecord.status == "Aman", AcademicRecord.ipk >= IPK_WARNING)
        )
        
    results = query.order_by(Student.nama).limit(200).all()
    out = []
    for st, ipk, rec_status, adv_name in results:
        out.append({
            "id": st.id,
            "nama": st.nama,
            "nim": st.nim,
            "prodi": st.prodi,
            "semester": st.semester,
            "status": st.status,
            "angkatan": st.angkatan,
            "ipk": round(ipk, 2) if ipk else None,
            "status_evaluasi": rec_status or "Aman",
            "advisor_name": adv_name or "Belum Ditentukan",
            "sumber_data": "Neosia Status"
        })

    # Mahasiswa Aktif tanpa AcademicRecord yang masuk zona ini
    if zone in ("merah", "kuning", "hijau"):
        rec_ids = db.query(AcademicRecord.student_id).distinct().subquery()
        active_no_rec = db.query(Student).outerjoin(Advisor, Student.advisor_id == Advisor.id).filter(
            Student.status == "Aktif",
            ~Student.id.in_(db.query(rec_ids.c.student_id))
        ).order_by(Student.angkatan).all()
        for s in active_no_rec:
            z = _classify_active_student(s.angkatan)
            if z != zone:
                continue
            adv = db.query(Advisor).filter(Advisor.id == s.advisor_id).first()
            out.append({
                "id": s.id,
                "nama": s.nama,
                "nim": s.nim,
                "prodi": s.prodi,
                "semester": s.semester,
                "status": s.status,
                "angkatan": s.angkatan,
                "ipk": None,
                "advisor_name": adv.nama if adv else "Belum Ditentukan",
                "sumber_data": "Estimasi Lama Studi"
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

# --- Admin Profile Management ---
from pydantic import BaseModel
from typing import Optional

class AdminProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None

@router.get("/profile")
def get_admin_profile(
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
    return {
        "username": current_user.username,
        "email": current_user.email or "",
        "whatsapp": current_user.whatsapp or "",
        "profile_picture": current_user.profile_picture or ""
    }

@router.put("/profile")
def update_admin_profile(
    payload: AdminProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    import bcrypt
    
    if payload.username and payload.username.strip():
        conflict = db.query(User).filter(User.username == payload.username, User.id != current_user.id).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Username sudah digunakan oleh akun lain")
        current_user.username = payload.username
        
    if payload.password and payload.password.strip():
        hashed_pw = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        current_user.hashed_password = hashed_pw
        
    if payload.email is not None:
        current_user.email = payload.email
        
    if payload.whatsapp is not None:
        current_user.whatsapp = payload.whatsapp
        
    db.commit()
    return {"status": "success", "message": "Profil Admin berhasil diperbarui"}
