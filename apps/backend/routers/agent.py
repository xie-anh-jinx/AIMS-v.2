from typing import List
from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from packages.database.connection import get_db
from packages.database.models import AgentLog, NotificationLog, User
from services.ai_agent_service.workflow_engine import WorkflowEngine
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
