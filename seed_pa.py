from packages.database.connection import get_db
from packages.database.models import User, Advisor
from sqlalchemy.orm import Session

# Generate DB session
db_generator = get_db()
db: Session = next(db_generator)

NIP = "197911172010122002"
defaultHash = "$2b$12$A/zQ1D6vR8aC2H2q9YQZzOQ3qQ5q0W3q5"

# 1. UPSERT USER
user = db.query(User).filter(User.username == NIP).first()
if not user:
    user = User(username=NIP, hashed_password=defaultHash, role="ADVISOR")
    db.add(user)
    db.commit()
    db.refresh(user)
    print("User inserted!")
else:
    print("User already exists!")

# 2. UPSERT ADVISOR
advisor = db.query(Advisor).filter(Advisor.user_id == user.id).first()
if not advisor:
    advisor = Advisor(user_id=user.id, nama=f"Dr. {NIP}", email="", whatsapp="")
    db.add(advisor)
    db.commit()
    print("Advisor inserted!")
else:
    print("Advisor already exists!")
