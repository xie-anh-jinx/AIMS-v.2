from pydantic import BaseModel
from typing import List, Optional

# --- Student Schemas ---
class StudentBase(BaseModel):
    nim: str
    nama: str
    angkatan: int
    semester: int
    prodi: str
    email: str
    nomor_whatsapp: str
    status: str

class StudentCreate(StudentBase):
    pass

class StudentResponse(StudentBase):
    id: int
    class Config:
        from_attributes = True

# --- Academic Record Schemas ---
class AcademicRecordBase(BaseModel):
    semester: int
    ips: Optional[float] = None
    ipk: Optional[float] = None
    sks: Optional[int] = None
    status: str

class AcademicRecordResponse(AcademicRecordBase):
    id: int
    student_id: int
    class Config:
        from_attributes = True

class CourseResponse(BaseModel):
    id: int
    kode: str
    nama: str
    sks: int
    semester: int
    class Config:
        from_attributes = True

class GradeResponse(BaseModel):
    id: int
    student_id: int
    course_id: int
    semester: Optional[int] = None
    grade: str
    bobot: float
    course: CourseResponse
    class Config:
        from_attributes = True

# --- Dashboard Schemas ---
class DashboardOverview(BaseModel):
    total_students: int
    total_active_students: int
    high_risk_students: int
    warning_students: int
    safe_students: int
    total_reminders_sent: int
