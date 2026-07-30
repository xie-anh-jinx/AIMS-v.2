import os
import re
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func, case, or_
from typing import List, Optional
from packages.database.connection import get_db
from packages.database.models import Student, AcademicRecord, User, Advisor, Course, Grade
from packages.shared.schemas import DashboardOverview, StudentResponse
from apps.backend.routers.auth import get_current_user

router = APIRouter(prefix="/admin", tags=["admin"])

from packages.shared.degree_rules import get_degree_rules

# ─── Batas Risiko Akademik (Referensi: Aturan Akademik Unhas) ──────
IPK_HIGH_RISK  = 2.00   # IPK < 2.00 → Zona Merah
IPK_WARNING    = 2.75   # IPK < 2.75 → Zona Kuning  

def _classify_active_student(angkatan: int, prodi: str = "S1", current_year: int = 2026) -> str:
    """Klasifikasi risiko mahasiswa Aktif tanpa data IPK,
    berdasarkan lama studi sesuai jenjang (S1, S2, S3)."""
    if angkatan >= current_year:
        return "hijau"
    rules = get_degree_rules(prodi)
    years_enrolled = current_year - angkatan
    if years_enrolled >= rules["max_years"]:
        return "merah"
    elif years_enrolled >= rules["warning_years"]:
        return "kuning"
    else:
        return "hijau"

@router.get("/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
        Student.angkatan < 2026,
        AcademicRecord.status == "HIGH_RISK"
    )
    query_warn = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        Student.status != "Lulus",
        Student.angkatan < 2026,
        AcademicRecord.status == "Warning"
    )
    query_safe = db.query(AcademicRecord).join(
        subq,
        (AcademicRecord.student_id == subq.c.student_id) &
        (AcademicRecord.semester   == subq.c.max_semester)
    ).join(Student, Student.id == AcademicRecord.student_id).filter(
        Student.status != "Lulus",
        AcademicRecord.status == "Aman"
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
        z = _classify_active_student(s.angkatan, s.prodi)
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(
        Student.semester,
        func.count(Student.id).label("count")
    ).filter(Student.status == "Aktif").group_by(Student.semester).order_by(Student.semester).all()
    return [{"name": f"Sem {r.semester}", "value": r.count} for r in rows]

@router.get("/stats/angkatan")
def get_angkatan_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(
        Student.angkatan,
        func.count(Student.id).label("count")
    ).group_by(Student.angkatan).order_by(Student.angkatan.desc()).all()
    # Or just returning raw angkatan mapping
    return [{"name": str(r.angkatan), "value": r.count} for r in rows]

@router.get("/stats/status")
def get_status_distribution(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    
    # Tampilkan semua status yang ada agar tidak ada mahasiswa yang "hilang"
    # Status keaktifan NeoSIA: Aktif, Cuti, Lulus, Drop Out, Keluar, Non Aktif, Pindah
    rows = db.query(
        Student.status,
        func.count(Student.id).label("count")
    ).group_by(Student.status).order_by(func.count(Student.id).desc()).all()
    
    return [{"name": r.status, "value": r.count} for r in rows]

@router.get("/stats/risk-per-prodi")
def get_risk_status_per_prodi(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
        if s.status_rec == "HIGH_RISK":
            prodi_counts[prodi]["merah"]  += 1
        elif s.status_rec == "Warning":
            prodi_counts[prodi]["kuning"] += 1
        elif s.status_rec == "Aman":
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
        z = _classify_active_student(s.angkatan, s.prodi)
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    rows = db.query(Student.prodi).distinct().order_by(Student.prodi).all()
    return [r.prodi for r in rows]

@router.get("/students/angkatan-list")
def get_angkatan_list(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
            Student.angkatan < 2026,
            AcademicRecord.status == "HIGH_RISK"
        )
    elif zone == "kuning":
        query = query.filter(
            Student.status != "Lulus",
            Student.angkatan < 2026,
            AcademicRecord.status == "Warning"
        )
    elif zone == "hijau":
        query = query.filter(
            AcademicRecord.status == "Aman"
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
            z = _classify_active_student(s.angkatan, s.prodi)
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
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

# --- Agent Monitor Sync ---

class AgentSyncConfig(BaseModel):
    auto_sync: bool
    interval: str
    neosia_token: Optional[str] = None

# Mocked config storage (in production, save to DB)
_AGENT_CONFIG = {
    "auto_sync": False,
    "interval": "Tiap 2 Minggu"
}

@router.get("/agent/config")
def get_agent_config(current_user: User = Depends(get_current_user)):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    token = os.getenv("NEOSIA_TOKEN", "")
    # Return only first/last 20 chars for display
    token_preview = f"{token[:20]}...{token[-10:]}" if len(token) > 40 else "(belum diset)"
    return {**_AGENT_CONFIG, "neosia_token_preview": token_preview, "neosia_token_set": bool(token)}

@router.post("/agent/config")
def update_agent_config(
    payload: AgentSyncConfig,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    _AGENT_CONFIG["auto_sync"] = payload.auto_sync
    _AGENT_CONFIG["interval"] = payload.interval
    # If token provided, update .env
    if payload.neosia_token:
        _update_neosia_token(payload.neosia_token)
    return {"status": "success", "message": "Konfigurasi Agent berhasil disimpan"}


@router.post("/agent/neosia-token")
def update_neosia_token(
    payload: dict,
    current_user: User = Depends(get_current_user)
):
    """Update NEOSIA_TOKEN in .env file."""
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    token = payload.get("token", "").strip()
    if not token or len(token) < 50:
        raise HTTPException(status_code=400, detail="Token tidak valid")
    try:
        _update_neosia_token(token)
        return {"status": "success", "message": "Token Neosia berhasil diperbarui"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


def _update_neosia_token(token: str):
    """Update NEOSIA_TOKEN value in .env file and reload env var."""
    env_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))), ".env")
    if os.path.exists(env_path):
        with open(env_path, "r") as f:
            content = f.read()
        if "NEOSIA_TOKEN=" in content:
            content = re.sub(r"NEOSIA_TOKEN=.*", f"NEOSIA_TOKEN={token}", content)
        else:
            content += f"\nNEOSIA_TOKEN={token}\n"
        with open(env_path, "w") as f:
            f.write(content)
    # Also update live environment so workers pick it up immediately
    os.environ["NEOSIA_TOKEN"] = token


def run_sync_script():
    """Run real Neosia transcript sync in background."""
    import time
    import httpx
    import logging
    from packages.database.connection import SessionLocal

    logger = logging.getLogger("aims.agent_sync")
    logger.info("[Agent] Neosia sync dimulai...")

    NEOSIA_TOKEN = os.getenv("NEOSIA_TOKEN", "")
    NEOSIA_API_BASE = os.getenv("NEOSIA_API_BASE", "https://api.neosia.unhas.ac.id")
    STATUS_MAP = {"A": "Aktif", "C": "Cuti", "L": "Lulus", "D": "Drop Out", "K": "Keluar", "P": "Pindah", "N": "Non Aktif"}

    if not NEOSIA_TOKEN:
        logger.error("[Agent] NEOSIA_TOKEN kosong, sync dibatalkan")
        return

    db = SessionLocal()
    try:
        students = db.query(Student).all()
        course_cache = {c.kode: c.id for c in db.query(Course).all()}
        headers = {"Authorization": f"Bearer {NEOSIA_TOKEN}", "Accept": "application/json"}
        total_ok = 0
        total_fail = 0

        with httpx.Client(timeout=15.0) as client:
            for idx, student in enumerate(students, 1):
                if idx % 100 == 0:
                    logger.info(f"[Agent] Progress: {idx}/{len(students)} | OK:{total_ok} ERR:{total_fail}")
                try:
                    url = f"{NEOSIA_API_BASE}/api/admin/transkrip/getTranskripMahasiswa?nim={student.nim}"
                    r = client.get(url, headers=headers)
                    if r.status_code == 404:
                        continue
                    r.raise_for_status()
                    data = r.json()
                    transkrips = data.get("transkrips", [])
                    ipk_dict = data.get("current_indeks_prestasi", {})
                    ipk = float(ipk_dict.get("indeks_prestasi_kumulatif", 0.0) or 0.0)
                    # Deduplicate is_used == 1 items by highest nilai_angka / bobot
                    valid_map = {}
                    for t in transkrips:
                        if t.get("is_used") != 1:
                            continue
                        kode = t.get("kode_mata_kuliah")
                        if not kode:
                            continue
                        bobot_val = float(t.get("nilai_angka") or 0.0)
                        if kode not in valid_map or bobot_val >= float(valid_map[kode].get("nilai_angka") or 0.0):
                            valid_map[kode] = t

                    valid_transkrips = list(valid_map.values())
                    total_sks = sum(int(t.get("sks", 0) or 0) for t in valid_transkrips)

                    db.query(Grade).filter(Grade.student_id == student.id).delete()
                    grades_to_add = []
                    max_semester = 1

                    for t in valid_transkrips:
                        kode = t.get("kode_mata_kuliah")
                        sks = int(t.get("sks", 0) or 0)
                        nama = t.get("nama_mata_kuliah") or (t.get("mata_kuliah") or {}).get("nama_resmi") or "Unknown"
                        try:
                            sem_val = int((t.get("mata_kuliah") or {}).get("semester") or 1)
                        except Exception:
                            sem_val = 1
                        bobot = float(t.get("nilai_angka") or 0.0)
                        nilai_huruf = t.get("nilai_huruf") or "E"

                        course_id = course_cache.get(kode)
                        if not course_id:
                            c = Course(kode=kode, nama=nama, sks=sks, semester=sem_val)
                            db.add(c)
                            db.flush()
                            db.refresh(c)
                            course_id = c.id
                            course_cache[kode] = course_id

                        if sem_val > max_semester:
                            max_semester = sem_val
                        grades_to_add.append(Grade(student_id=student.id, course_id=course_id, semester=sem_val, grade=nilai_huruf, bobot=bobot))

                    db.add_all(grades_to_add)

                    deg_rules = get_degree_rules(student.prodi)
                    max_sem_limit = deg_rules["max_semesters"]
                    semester_calc = max(1, min(max_sem_limit, (2026 - student.angkatan) * 2)) if student.angkatan else max_semester

                    from packages.shared.degree_rules import evaluate_academic_risk
                    risk = evaluate_academic_risk(student.prodi, semester_calc, total_sks, ipk)
                    db.query(AcademicRecord).filter(AcademicRecord.student_id == student.id).delete()
                    db.add(AcademicRecord(student_id=student.id, semester=semester_calc, ips=ipk, ipk=ipk, sks=total_sks, status=risk))

                    mhs_data = data.get("mahasiswa", {})
                    kode_status = mhs_data.get("kode_status", "A")
                    student.semester = semester_calc
                    student.status = STATUS_MAP.get(kode_status, "Aktif")
                    db.commit()
                    total_ok += 1
                except Exception as e:
                    logger.warning(f"[Agent] Error {student.nim}: {e}")
                    db.rollback()
                    total_fail += 1

                time.sleep(2.0)

        logger.info(f"[Agent] Sync selesai. OK: {total_ok} | GAGAL: {total_fail}")
    finally:
        db.close()


@router.post("/agent/sync")
def trigger_agent_sync(
    background_tasks: BackgroundTasks,
    current_user: User = Depends(get_current_user)
):
    if current_user.role not in ["ADMIN", "DEKAN", "WD1", "KASUBAG_AKADEMIK"]:
        raise HTTPException(status_code=403, detail="Not authorized")
    token = os.getenv("NEOSIA_TOKEN", "")
    if not token:
        raise HTTPException(status_code=400, detail="NEOSIA_TOKEN belum diset. Perbarui token di Agent Monitor terlebih dahulu.")
    background_tasks.add_task(run_sync_script)
    return {"status": "success", "message": "Sinkronisasi Neosia telah dijalankan di latar belakang. Proses ini memakan waktu beberapa jam."}

