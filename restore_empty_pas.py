import json
from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, User
from collections import defaultdict

db = SessionLocal()

file_path = "plugins/academic-connector/pa_dump_all.json"
with open(file_path, "r") as f:
    data = json.load(f)

pa_initial = defaultdict(list)
pa_names = {}
for paObj in data:
    d = paObj.get("dosen") or paObj
    nip = str(d.get("nip") or d.get("id_pegawai") or d.get("username") or "")
    if not nip: continue
    
    nama = d.get("nama_dosen") or d.get("nama") or f"Dosen {nip}"
    pa_names[nip] = nama
    
    mhs_list = paObj.get("mahasiswas") or paObj.get("bimbingan") or []
    for mhs in mhs_list:
        nim_mhs = str(mhs if isinstance(mhs, str) else (mhs.get("nim") or mhs.get("id") or ""))
        if nim_mhs:
            pa_initial[nip].append(nim_mhs)

# We know the empty PAs (including Alung which I already fixed, but this is idempotent)
# Let's find all PAs who currently have 0 students in the database
all_advisors = db.query(Advisor).all()
fixed_count = 0

for adv in all_advisors:
    u = db.query(User).filter(User.id == adv.user_id).first()
    if not u: continue
    nip = u.username
    
    # How many students currently in DB?
    db_count = db.query(Student).filter(Student.advisor_id == adv.id).count()
    if db_count == 0:
        # DB says 0. Did they have students in JSON?
        intended_mhs = list(set(pa_initial.get(nip, [])))
        if len(intended_mhs) > 0:
            print(f"Restoring {len(intended_mhs)} students for empty PA: {adv.nama} (NIP: {nip})")
            for nim in intended_mhs:
                st = db.query(Student).filter(Student.nim == nim).first()
                if st:
                    st.advisor_id = adv.id
                    fixed_count += 1

db.commit()
print(f"Done! Restored {fixed_count} student-PA links for completely empty PAs.")
