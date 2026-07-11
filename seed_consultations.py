from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student, ConsultationLog
from datetime import datetime, timedelta

db = next(get_db())

nip = "197911172010122002"
user = db.query(User).filter(User.username == nip).first()
advisor = db.query(Advisor).filter(Advisor.user_id == user.id).first()

# Get 2 students bound to this advisor
students = db.query(Student).filter(Student.advisor_id == advisor.id).limit(2).all()

if len(students) >= 2:
    log1 = ConsultationLog(
        student_id=students[0].id,
        advisor_id=advisor.id,
        type="Validasi KRS Luring",
        status="Selesai",
        date=datetime.utcnow() - timedelta(days=2),
        notes="Mahasiswa sudah memenuhi SKS wajib."
    )
    
    log2 = ConsultationLog(
        student_id=students[1].id,
        advisor_id=advisor.id,
        type="Konsultasi Nilai E",
        status="Follow up",
        date=datetime.utcnow() - timedelta(hours=5),
        notes="Harus mengulang mata kuliah semester depan."
    )
    
    db.add(log1)
    db.add(log2)
    db.commit()
    print("Seeded 2 real consultations!")
else:
    print("Not enough students bound.")
