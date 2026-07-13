import os, sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, ProdiAdmin

db = SessionLocal()

# Dictionary to map Neosia raw names to our internal standardized names
MAPPING = {
    "SASTRA PRANCIS - S1": "Sastra Prancis",
    "SASTRA JEPANG - S1": "Sastra Jepang",
    "SASTRA INGGRIS - S1": "Sastra Inggris",
    "SASTRA INDONESIA - S1": "Sastra Indonesia",
    "ARKEOLOGI - S1": "Arkeologi",
    "ARKEOLOGI - S2": "Arkeologi (S2)",
    "ILMU SEJARAH - S1": "Sejarah",
    "Sejarah - S2": "Sejarah (S2)",
    "SASTRA BUGIS-MAKASSAR - S1": "Sastra Bugis Makassar",
    "SASTRA ASIA BARAT - S1": "Sastra Arab",
    "BAHASA MANDARIN DAN KEBUDAYAAN TIONGKOK": "Bahasa Mandarin & kebudayaan Tiongkok",
    "BAHASA INGGRIS - S2": "Bahasa Inggris (S2)",
    "BAHASA INGGRIS - S3": "Bahasa Inggris (S3)",
    "BAHASA INDONESIA - S2": "Bahasa Indonesia (S2)",
    "SASTRA INDONESIA - S3": "Sastra Indonesia",
    "LINGUISTIK - S2": "Linguistik (S2)",
    "ILMU LINGUISTIK - S3": "Ilmu Linguistik (S3)",
    "KAJIAN BUDAYA - S2": "Kajian Budaya (S2)",
    "PARIWISATA - S1": "Pariwisata"
}

print("Standardizing Student Prodi strings...")
students = db.query(Student).all()
updated_students = 0
for s in students:
    if s.prodi in MAPPING:
        s.prodi = MAPPING[s.prodi]
        updated_students += 1
    elif "KAJIAN BUDAYA" in str(s.prodi).upper():
        s.prodi = "Kajian Budaya (S2)"
        updated_students += 1

print("Standardizing Advisor Prodi strings...")
advisors = db.query(Advisor).all()
updated_advisors = 0
for a in advisors:
    if a.prodi in MAPPING:
        a.prodi = MAPPING[a.prodi]
        updated_advisors += 1

db.commit()
print(f"Update complete! {updated_students} students and {updated_advisors} advisors standardized.")

# Bonus: If Kajian Budaya (S2) kaprodi user doesn't exist, create it so they can login!
from packages.database.models import User
defaultHash = '$2b$12$FCMiEQZ3wTWHR8oa47TE4ODtJUoiI/Tger84vjJsS6GAbAa/m5bVS'
kb_admin = db.query(User).filter(User.username == "kaprodi_kajianbudaya").first()
if not kb_admin:
    kb_admin = User(
        username="kaprodi_kajianbudaya",
        hashed_password=defaultHash,
        role="PRODI"
    )
    db.add(kb_admin)
    db.commit()
    db.refresh(kb_admin)
    
    padm = ProdiAdmin(
        user_id=kb_admin.id,
        prodi_name="Kajian Budaya (S2)",
        nama="Dr. Kepala Kajian Budaya"
    )
    db.add(padm)
    db.commit()
    print("Created kaprodi_kajianbudaya account with password 'password123'!")
