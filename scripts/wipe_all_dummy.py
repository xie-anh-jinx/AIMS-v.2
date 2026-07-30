import os
import sys
import re
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
load_dotenv(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"))

from packages.database.connection import SessionLocal
from packages.database.models import Student, User

db = SessionLocal()

all_students = db.query(Student).all()
# Find any student whose name contains a digit
dummy_students = [s for s in all_students if any(char.isdigit() for char in s.nama)]
print(f"Students with digits in name: {len(dummy_students)}")
if len(dummy_students) > 0:
    for s in dummy_students:
        print(s.nim, s.nama)

db.close()
