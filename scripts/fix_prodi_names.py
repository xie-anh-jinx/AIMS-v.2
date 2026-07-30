import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student

db = SessionLocal()

updates = {
    "Sastra Perancis": "Sastra Prancis",
    "Bahasa Mandarin & kebudayaan Tiongkok": "Sastra Mandarin",
    "Sastra Bugis Makassar": "Sastra Daerah",
    "Sejarah": "Ilmu Sejarah"
}

for old_name, new_name in updates.items():
    students = db.query(Student).filter(Student.prodi == old_name).all()
    if students:
        print(f"Updating {len(students)} students from '{old_name}' to '{new_name}'")
        for s in students:
            s.prodi = new_name
        db.commit()

# Print current distinct prodis
print("Current Prodis:")
print([p[0] for p in db.query(Student.prodi).distinct().all()])
db.close()
