from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime, Text, Boolean
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True) # nim, email, or admin
    hashed_password = Column(String)
    role = Column(String) # ADMIN, ADVISOR, STUDENT, PRODI
    profile_picture = Column(Text, nullable=True)

class ProdiAdmin(Base):
    __tablename__ = 'prodi_admins'
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    nama = Column(String)
    prodi_name = Column(String) # Tracks which prodi this admin manages

class Student(Base):
    __tablename__ = 'students'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    advisor_id = Column(Integer, ForeignKey('advisors.id'), nullable=True)
    nim = Column(String, unique=True, index=True)
    nama = Column(String)
    angkatan = Column(Integer)
    semester = Column(Integer)
    prodi = Column(String)
    email = Column(String)
    nomor_whatsapp = Column(String)
    phone_number_wa = Column(String, nullable=True)
    telegram_username = Column(String, nullable=True)
    status = Column(String)

class AcademicRecord(Base):
    __tablename__ = 'academic_records'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    semester = Column(Integer)
    ips = Column(Float)
    ipk = Column(Float)
    sks = Column(Integer)
    status = Column(String)

class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True, index=True)
    kode = Column(String, unique=True, index=True)
    nama = Column(String)
    semester = Column(Integer)
    sks = Column(Integer)

class Grade(Base):
    __tablename__ = 'grades'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    course_id = Column(Integer, ForeignKey('courses.id'))
    semester = Column(Integer)
    grade = Column(String)
    bobot = Column(Float)
    
    course = relationship("Course")

class Advisor(Base):
    __tablename__ = 'advisors'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=True)
    nama = Column(String)
    email = Column(String)
    whatsapp = Column(String)
    telegram_username = Column(String, nullable=True)
    prodi = Column(String, nullable=True) # To link Advisor to a specific Prodi

    mahasiswa_bimbingan = relationship("Student", backref="advisor")

class Reminder(Base):
    __tablename__ = 'reminders'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    type = Column(String)
    deadline = Column(DateTime)
    status = Column(String)
    sent_at = Column(DateTime, nullable=True)

# ─── Agent Engine Models ───────────────────────────────────────────

class AgentLog(Base):
    __tablename__ = 'agent_logs'

    id = Column(Integer, primary_key=True, index=True)
    event_type = Column(String, index=True)   # RULE_TRIGGERED, WORKFLOW_RUN, SCHEDULER_RUN
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    rule_name = Column(String, nullable=True)  # e.g. HIGH_RISK_IPK, CONSECUTIVE_DROP
    action = Column(String)                   # e.g. NOTIFY_ADVISOR, SEND_REMINDER
    status = Column(String, default='SUCCESS') # SUCCESS, FAILED, SKIPPED
    message = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class NotificationLog(Base):
    __tablename__ = 'notification_logs'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'), nullable=True)
    channel = Column(String)     # WHATSAPP, EMAIL, TELEGRAM, SYSTEM
    recipient = Column(String)   # phone/email address
    message = Column(Text)
    status = Column(String, default='SENT')  # SENT, FAILED, PENDING
    sent_at = Column(DateTime, default=datetime.utcnow)

class ConsultationLog(Base):
    __tablename__ = 'consultation_logs'

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey('students.id'))
    advisor_id = Column(Integer, ForeignKey('advisors.id'))
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String) 
    status = Column(String) 
    notes = Column(Text, nullable=True)
    is_archived_by_sender = Column(Boolean, default=False)
    is_archived_by_receiver = Column(Boolean, default=False)

    student = relationship("Student")
    advisor = relationship("Advisor")

class AdminNote(Base):
    __tablename__ = 'admin_notes'

    id = Column(Integer, primary_key=True, index=True)
    advisor_id = Column(Integer, ForeignKey('advisors.id'))
    date = Column(DateTime, default=datetime.utcnow)
    type = Column(String) 
    status = Column(String) 
    notes = Column(Text, nullable=True)
    is_archived_by_sender = Column(Boolean, default=False)
    is_archived_by_receiver = Column(Boolean, default=False)

    advisor = relationship("Advisor")
