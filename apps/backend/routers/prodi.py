from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func, or_
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

# ─── Batas Risiko Akademik ──────
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

def get_associated_prodi_names(prodi_name: str) -> List[str]:
    name_lower = prodi_name.lower().strip()
    aliases = [prodi_name]
    if "mandarin" in name_lower or "tiongkok" in name_lower:
        aliases.extend(["Bahasa Mandarin & kebudayaan Tiongkok", "Sastra Mandarin"])
    elif "bugis" in name_lower or "daerah" in name_lower:
        aliases.extend(["Sastra Bugis Makassar", "Sastra Daerah"])
    elif "sejarah" in name_lower:
        aliases.extend(["Sejarah", "Ilmu Sejarah"])
    return list(set(aliases))

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
    students_with_rec = set()
    for uid, r in latest_records.items():
        student = next((s for s in students if s.id == uid), None)
        if not student or student.status == "Lulus":
            continue
            
        students_with_rec.add(uid)
        if r.status == "HIGH_RISK": high_risk += 1
        elif r.status == "Warning": warning += 1
        elif r.status == "Aman": safe += 1
    # Analyze active students without AcademicRecord
    for s in students:
        if s.status == "Aktif" and s.id not in students_with_rec:
            z = _classify_active_student(s.angkatan)
            if z == "merah":   high_risk += 1
            elif z == "kuning": warning += 1
            else:               safe += 1

    return {
        "total_students": len(students),
        "total_active_students": active_count,
        "high_risk_students": high_risk,
        "warning_students": warning,
        "safe_students": safe,
        "total_advisors": db.query(Advisor).filter(Advisor.prodi.in_(get_associated_prodi_names(prodi_admin.prodi_name))).count()
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
    advisors = db.query(Advisor).filter(Advisor.prodi.in_(get_associated_prodi_names(prodi_admin.prodi_name))).all()
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
    subq = db.query(
        AcademicRecord.student_id,
        func.max(AcademicRecord.semester).label("max_semester")
    ).group_by(AcademicRecord.student_id).subquery()
    
    all_recs = db.query(
        Student.status,
        AcademicRecord.status.label("rec_status"),
        func.count(Student.id)
    ).outerjoin(
        subq, Student.id == subq.c.student_id
    ).outerjoin(
        AcademicRecord, 
        (AcademicRecord.student_id == subq.c.student_id) & (AcademicRecord.semester == subq.c.max_semester)
    ).filter(
        Student.prodi == prodi_admin.prodi_name
    ).group_by(Student.status, AcademicRecord.status).all()
    
    stats_map = {
        "Zona Merah": 0,
        "Zona Kuning": 0,
        "Zona Hijau": 0,
        "Aktif": 0
    }
    
    for s_status, r_status, c in all_recs:
        # Tentukan apakah benar-benar inaktif
        if s_status in ["Drop Out", "Lulus", "Keluar", "Cuti", "Non Aktif"]:
            stats_map[s_status] = stats_map.get(s_status, 0) + c
        else:
            # Jika aktif (atau data error bertuliskan 'Warning'/'Aman'), klasifikasikan berdasar rekaman
            if r_status == "HIGH_RISK":
                stats_map["Zona Merah"] += c
            elif r_status == "Warning":
                stats_map["Zona Kuning"] += c
            elif r_status == "Aman":
                stats_map["Zona Hijau"] += c
            else:
                stats_map["Aktif"] += c
                
    # Buang yg jumlahnya 0 agar bersih
    return [{"name": k, "value": v} for k, v in stats_map.items() if v > 0]

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
        AcademicRecord.status.label("rec_status"),
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
        query = query.filter(
            Student.status != "Lulus",
            AcademicRecord.status == "HIGH_RISK"
        )
    elif zone == "kuning":
        query = query.filter(
            Student.status != "Lulus",
            AcademicRecord.status == "Warning"
        )
    elif zone == "hijau":
        query = query.filter(
            Student.status != "Lulus",
            AcademicRecord.status == "Aman"
        )
        
    results = query.all()
    out = []
    students_with_rec = set()
    for st, ipk, rec_status, adv_name in results:
        students_with_rec.add(st.id)
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
        
    # Active students without AcademicRecord in this prodi
    if zone in ("merah", "kuning", "hijau"):
        active_no_rec = db.query(Student).outerjoin(
            Advisor, Student.advisor_id == Advisor.id
        ).filter(
            Student.prodi == prodi_admin.prodi_name,
            Student.status == "Aktif",
            ~Student.id.in_(db.query(AcademicRecord.student_id).distinct().subquery())
        ).order_by(Student.angkatan).all()
        
        for s in active_no_rec:
            if s.id in students_with_rec:
                continue
            z = _classify_active_student(s.angkatan)
            if z == zone:
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
    advisor = db.query(Advisor).filter(Advisor.id == payload.advisor_id, Advisor.prodi.in_(get_associated_prodi_names(prodi_admin.prodi_name))).first()
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
        Advisor.prodi.in_(get_associated_prodi_names(prodi_admin.prodi_name)),
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
        Advisor.prodi.in_(get_associated_prodi_names(prodi_admin.prodi_name))
    ).first()
    if not note:
        raise HTTPException(status_code=404, detail="Catatan tidak ditemukan")
    
    note.is_archived_by_sender = True
    db.commit()
    return {"message": "Catatan dihapus dari riwayat terkirim"}

# --- Prodi Profile Management ---
from pydantic import BaseModel
from typing import Optional

class ProdiProfileUpdateRequest(BaseModel):
    username: Optional[str] = None
    password: Optional[str] = None
    email: Optional[str] = None
    whatsapp: Optional[str] = None

@router.get("/profile")
def get_prodi_profile(
    current_user: User = Depends(get_current_user),
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    return {
        "username": current_user.username,
        "email": prodi_admin.email or "",
        "whatsapp": prodi_admin.whatsapp or "",
        "profile_picture": current_user.profile_picture or ""
    }

@router.put("/profile")
def update_prodi_profile(
    payload: ProdiProfileUpdateRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
    prodi_admin: ProdiAdmin = Depends(get_prodi_user)
):
    import bcrypt
    
    # Update linked User credentials
    if payload.username and payload.username.strip():
        conflict = db.query(User).filter(User.username == payload.username, User.id != current_user.id).first()
        if conflict:
            raise HTTPException(status_code=400, detail="Username sudah digunakan oleh akun lain")
        current_user.username = payload.username
        
    if payload.password and payload.password.strip():
        hashed_pw = bcrypt.hashpw(payload.password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        current_user.hashed_password = hashed_pw
        
    # Update ProdiAdmin columns
    if payload.email is not None:
        prodi_admin.email = payload.email
        
    if payload.whatsapp is not None:
        prodi_admin.whatsapp = payload.whatsapp
        
    db.commit()
    return {"status": "success", "message": "Profil Prodi berhasil diperbarui"}
