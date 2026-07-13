from packages.database.connection import SessionLocal
from packages.database.models import Advisor

db = SessionLocal()
advisors = db.query(Advisor).filter(Advisor.prodi != None).order_by(Advisor.prodi, Advisor.nama).all()

current_prodi = ""
for adv in advisors:
    if adv.prodi != current_prodi:
        print(f"\n[{adv.prodi}]")
        current_prodi = adv.prodi
    print(f" - {adv.nama}")

