import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import ProdiAdmin, Student, Advisor

db = SessionLocal()
admins = db.query(ProdiAdmin).all()
print("CURRENT PRODI ADMINS:")
for a in admins:
    print(f"- {a.prodi_name}")

# Also replace exact prodi string in Student and Advisor where it makes sense
db.commit()
