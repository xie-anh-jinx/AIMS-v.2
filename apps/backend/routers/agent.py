from typing import List, Optional
from pydantic import BaseModel
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from sqlalchemy import func
from packages.database.connection import get_db
from packages.database.models import AgentLog, NotificationLog, User, Student, AcademicRecord
from services.ai_agent_service.workflow_engine import WorkflowEngine
from services.notification_service.notification_engine import NotificationEngine
from apps.backend.routers.auth import get_current_user

router = APIRouter(prefix="/agent", tags=["agent"])

@router.post("/evaluate-all")
def trigger_full_evaluation(
    background_tasks: BackgroundTasks, 
    current_user: User = Depends(get_current_user)
):
    """Admin triggers a full manual evaluation of all students."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    engine = WorkflowEngine()
    # Run in background so request returns immediately
    background_tasks.add_task(engine.run_full_evaluation)
    return {"status": "SUCCESS", "message": "Evaluation job started in the background."}

@router.post("/evaluate-student/{student_id}")
def trigger_student_evaluation(
    student_id: int, 
    current_user: User = Depends(get_current_user)
):
    """Trigger evaluation for a specific student."""
    if current_user.role not in ["ADMIN", "ADVISOR"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    engine = WorkflowEngine()
    result = engine.evaluate_single_student(student_id)
    return {"status": "SUCCESS", "triggered_rules": result}

@router.get("/logs/activity")
def get_agent_logs(
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Retrieve agent decision logs (Admin only)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    logs = db.query(AgentLog).order_by(AgentLog.created_at.desc()).limit(limit).all()
    # Serialize securely
    return [
        {
            "id": l.id,
            "event_type": l.event_type,
            "student_id": l.student_id,
            "rule_name": l.rule_name,
            "action": l.action,
            "status": l.status,
            "message": l.message,
            "created_at": l.created_at
        } for l in logs
    ]

@router.get("/logs/notifications")
def get_notification_logs(
    limit: int = 100, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    """Retrieve outbound notification logs (Admin only)."""
    if current_user.role != "ADMIN":
        raise HTTPException(status_code=403, detail="Not authorized")
        
    logs = db.query(NotificationLog).order_by(NotificationLog.sent_at.desc()).limit(limit).all()
    return [
        {
            "id": l.id,
            "student_id": l.student_id,
            "channel": l.channel,
            "recipient": l.recipient,
            "message": l.message,
            "status": l.status,
            "sent_at": l.sent_at
        } for l in logs
    ]
class BroadcastRequest(BaseModel):
    target: str # 'ALL', 'RED_ZONE', 'YELLOW_ZONE', 'RED_ZONE_ADVISORS', 'YELLOW_ZONE_ADVISORS', 'ADVISORS_RISK_ZONE', 'ALL_ADVISORS'
    channel: str # 'WHATSAPP', 'TELEGRAM', 'EMAIL'
    message: str

@router.post("/broadcast")
def trigger_manual_broadcast(
    payload: BroadcastRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    from packages.database.models import Advisor

    if current_user.role not in ["ADMIN", "WD1", "DEKAN", "KASUBAG"]:
        raise HTTPException(status_code=403, detail="Not authorized")
        
    notifier = NotificationEngine(db)
    sent_count = 0
    total_target = 0

    # 1. Target is Dosen PA specific
    if payload.target in ["ALL_ADVISORS", "RED_ZONE_ADVISORS", "YELLOW_ZONE_ADVISORS", "ADVISORS_RISK_ZONE"]:
        advisors = []
        if payload.target == "ALL_ADVISORS":
            advisors = db.query(Advisor).all()
        else:
            subq = db.query(
                AcademicRecord.student_id,
                func.max(AcademicRecord.semester).label("max_semester")
            ).group_by(AcademicRecord.student_id).subquery()

            query = db.query(Advisor).join(Student, Student.advisor_id == Advisor.id).join(
                AcademicRecord, Student.id == AcademicRecord.student_id
            ).join(
                subq,
                (AcademicRecord.student_id == subq.c.student_id) & 
                (AcademicRecord.semester == subq.c.max_semester)
            ).filter(Student.status == "Aktif")

            if payload.target == "RED_ZONE_ADVISORS":
                query = query.filter(AcademicRecord.status == "HIGH_RISK")
            elif payload.target == "YELLOW_ZONE_ADVISORS":
                query = query.filter(AcademicRecord.status == "Warning")
            elif payload.target == "ADVISORS_RISK_ZONE":
                query = query.filter(AcademicRecord.status.in_(["HIGH_RISK", "Warning"]))

            advisors = list(set(query.all()))

        total_target = len(advisors)
        for adv in advisors:
            recipient = adv.whatsapp or adv.email
            if recipient:
                wa_msg = f"📣 *SIARAN KAMPUS UNTUK DOSEN PA*\n\nYth. Bapak/Ibu *{adv.nama}*,\n\n{payload.message}"
                success = notifier.send(payload.channel, recipient, wa_msg)
                if success: sent_count += 1

        return {"status": "SUCCESS", "message": f"Broadcast sent via {payload.channel} to {sent_count}/{total_target} Dosen PA."}

    # 2. Target is Students (ALL, RED_ZONE, YELLOW_ZONE)
    students = []
    if payload.target == "ALL":
        students = db.query(Student).filter(Student.status == "Aktif").all()
    else:
        subq = db.query(
            AcademicRecord.student_id,
            func.max(AcademicRecord.semester).label("max_semester")
        ).group_by(AcademicRecord.student_id).subquery()
        
        query = db.query(Student).join(
            AcademicRecord, Student.id == AcademicRecord.student_id
        ).join(
            subq,
            (AcademicRecord.student_id == subq.c.student_id) & 
            (AcademicRecord.semester == subq.c.max_semester)
        ).filter(Student.status == "Aktif")
        
        if payload.target == "RED_ZONE":
            query = query.filter(AcademicRecord.status == "HIGH_RISK")
        elif payload.target == "YELLOW_ZONE":
            query = query.filter(AcademicRecord.status == "Warning")
            
        students = query.all()

    if not students:
        return {"status": "SUCCESS", "message": "No active students found matching target criteria."}
        
    total_target = len(students)
    notified_advisors = set()

    for s in students:
        # Determine recipient based on channel
        recipient = None
        if payload.channel == "WHATSAPP":
            recipient = s.nomor_whatsapp
        elif payload.channel == "EMAIL":
            recipient = getattr(s, 'email', None)
        elif payload.channel == "TELEGRAM":
            recipient = s.nomor_whatsapp

        if recipient:
            success = notifier.send(payload.channel, recipient, payload.message, student_id=s.id)
            if success: sent_count += 1

        # ALSO send WhatsApp via OpenClaw to student's Dosen PA
        if payload.channel == "WHATSAPP" and s.advisor and s.advisor.whatsapp and s.advisor.id not in notified_advisors:
            adv_msg = (
                f"🚨 *SIARAN MONITORING OPENCLAW DOSEN PA*\n\n"
                f"Yth. Bapak/Ibu Dosen PA *{s.advisor.nama}*,\n"
                f"Pesan siaran otomatis telah dikirimkan ke mahasiswa bimbingan Anda ({s.nama} - {s.nim}):\n\n"
                f"\"{payload.message}\"\n\n"
                f"Mohon dapat ditinjau pada portal AIMS UNHAS."
            )
            notifier.send("WHATSAPP", s.advisor.whatsapp, adv_msg, student_id=s.id)
            notified_advisors.add(s.advisor.id)

    return {"status": "SUCCESS", "message": f"Broadcast sent via {payload.channel} to {sent_count}/{total_target} students (serta tembusan WA ke Dosen PA terkait)."}
