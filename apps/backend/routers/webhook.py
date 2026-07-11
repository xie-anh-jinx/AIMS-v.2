from fastapi import APIRouter, Header, HTTPException, BackgroundTasks
from pydantic import BaseModel
from services.ai_agent_service.workflow_engine import WorkflowEngine
from sqlalchemy.orm import Session
from packages.database.connection import SessionLocal

router = APIRouter(
    prefix="/webhook",
    tags=["Integration"],
    responses={404: {"description": "Not found"}},
)

class AcademicEventPayload(BaseModel):
    event_type: str        # contoh: "YUDISIUM_FINAL", "NEW_SEMESTER"
    semester_id: str       # contoh: "2023-Gasal"
    target_prodi: str      # opsi spesifik fakultas/prodi

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def execute_agent_evaluator(semester: str, db: Session):
    """Background task to trigger the AI agent evaluation smoothly"""
    engine = WorkflowEngine(db=db)
    # Simulate a full scan logic triggering based on webhook signal
    # This avoids taking down the main thread for the HTTP response
    students_evaluated = 0
    # Custom business logic here...
    print(f"[WEBHOOK] Background Agent Evaluator FINISHED for {semester}")

@router.post("/univ-sync")
async def receive_university_webhook(
    payload: AcademicEventPayload, 
    background_tasks: BackgroundTasks,
    x_aims_secure_token: str = Header(...)
):
    """
    Endpoint Webhook untuk menerima Trigger/Sinyal dari Server IT Universitas.
    Universitas harus mengirim header 'X-AIMS-SECURE-TOKEN' yang valid.
    """
    
    # 1. Validasi Keamanan Lapis Pertama
    EXPECTED_TOKEN = "AIMS-PROD-SECRET-998877"
    if x_aims_secure_token != EXPECTED_TOKEN:
        raise HTTPException(
            status_code=401, 
            detail="Otorisasi ditolak. Token Webhook Universitas tidak valid."
        )
        
    # 2. Proses Berdasarkan Jenis Event
    if payload.event_type == "YUDISIUM_FINAL":
        # Gunakan BackgroundTasks agar API kita segera menjawab "OK" ke server Universitas
        # namun bot / agen kita jalan diam-diam memproses notifikasi
        db_session = SessionLocal()
        background_tasks.add_task(execute_agent_evaluator, payload.semester_id, db_session)
        
        return {
            "status": "success", 
            "message": "Sinyal Yudisium diterima. Background Agent AIMS sedang melakukan evaluasi risiko akademik..."
        }

    return {
        "status": "ignored", 
        "message": f"Event {payload.event_type} diterima namun tidak membutuhkan validasi lanjutan dari AIMS."
    }
