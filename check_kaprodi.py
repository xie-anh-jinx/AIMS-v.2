import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import User, ProdiAdmin, Student

db = SessionLocal()
kaprodi = db.query(User).filter(User.username == 'kaprodi_sastraprancis').first()
if kaprodi:
    padm = db.query(ProdiAdmin).filter(ProdiAdmin.user_id == kaprodi.id).first()
    print(f"Kaprodi Sastra Prancis is mapped to Prodi: '{padm.prodi_name}'")
    
    count = db.query(Student).filter(Student.prodi == padm.prodi_name).count()
    print(f"Number of students exactly matching '{padm.prodi_name}': {count}")
    
    # Also let's see what Neosia actually named "Sastra Prancis"
    close_matches = db.query(Student.prodi).filter(Student.prodi.ilike('%prancis%')).distinct().all()
    print(f"Prodis in DB matching 'prancis': {[m[0] for m in close_matches]}")
    for m in close_matches:
        c = db.query(Student).filter(Student.prodi == m[0]).count()
        print(f" - {m[0]}: {c} students")
else:
    print("User kaprodi_sastraprancis not found")
