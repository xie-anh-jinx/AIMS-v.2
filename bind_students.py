from packages.database.connection import get_db
from packages.database.models import User, Advisor, Student
from sqlalchemy.orm import Session

db = next(get_db())

nip = "197911172010122002"
user = db.query(User).filter(User.username == nip).first()
if not user:
    print("USER NOT FOUND")
    exit(1)

advisor = db.query(Advisor).filter(Advisor.user_id == user.id).first()
if not advisor:
    print("ADVISOR NOT FOUND")
    exit(1)

# Pick exactly these 5 students
target_nims = ["F061181002", "F071241071", "F051181330", "F051181501", "F061181001"]
students = db.query(Student).filter(Student.nim.in_(target_nims)).all()

for s in students:
    s.advisor_id = advisor.id

db.commit()
print(f"Successfully bound {len(students)} students to Advisor {advisor.nama}!")
