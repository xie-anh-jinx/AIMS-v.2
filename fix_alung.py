import json
from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User

db = SessionLocal()

u = db.query(User).filter(User.username == "199911052025105001").first()
adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()

file_path = "plugins/academic-connector/pa_dump_all.json"
data = json.load(open(file_path))
alung_mhs = [str(m if isinstance(m, str) else (m.get("nim") or m.get("id"))) for d in data if "199911052025105001" in str(d) for m in d.get("mahasiswas", d.get("bimbingan", []))]

linked = 0
for nim in alung_mhs:
    st = db.query(Student).filter(Student.nim == nim).first()
    if st:
        st.advisor_id = adv.id
        linked += 1

db.commit()
print(f"Fixed {linked} students for Alung!")
