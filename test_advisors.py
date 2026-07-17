from packages.database.connection import SessionLocal
from packages.database.models import Advisor
db = SessionLocal()
advisors = db.query(Advisor).all()
print(f"Total advisors in DB: {len(advisors)}")
for a in advisors[:3]:
    print(f"- {a.id}: {a.nama}")
