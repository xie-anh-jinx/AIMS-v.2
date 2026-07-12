from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from apps.backend.routers import students, admin, auth, agent, webhook, advisor, prodi
from services.scheduler_service.scheduler import start_scheduler

app = FastAPI(
    title="AIMS Backend API",
    description="Academic Intelligence Management System API Gateway",
    version="1.0.0",
    lifespan=None
)

# Start APScheduler on App start
@app.on_event("startup")
def startup_event():
    start_scheduler()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(students.router)
app.include_router(admin.router)
app.include_router(advisor.router)
app.include_router(agent.router)
app.include_router(webhook.router)
app.include_router(prodi.router)

@app.get("/")
def read_root():
    return {"message": "Welcome to AIMS Backend API"}

@app.get("/health")
def health_check():
    return {"status": "ok"}
