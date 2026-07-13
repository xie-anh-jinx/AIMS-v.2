import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.models import Student
from packages.database.connection import SessionLocal

db = SessionLocal()
prodis = db.query(Student.prodi).distinct().all()
print("PRODI LIST:")
for p in prodis:
    print("- " + str(p[0]))

s2 = db.query(Student).filter(Student.prodi.ilike('%budaya%')).all()
print(f"\nStudent count with 'budaya' in prodi: {len(s2)}")
