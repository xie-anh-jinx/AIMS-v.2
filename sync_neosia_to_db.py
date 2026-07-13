"""
sync_neosia_to_db.py
────────────────────
Sinkronisasi AMAN (hanya UPSERT, TIDAK PERNAH DELETE) data asli Neosia
ke database AIMS lokal sebagai cadangan permanen.

Sumber data  : plugins/academic-connector/pa_dump_all.json  (654 PA, ~24.000 mhs)
Filter        : angkatan 2019-2025 saja
Prodi rules   : mapping dari nama_resmi Neosia → nama standar AIMS

Jalankan sekali; aman dijalankan berulang (idempotent).
"""

import os, sys, json, bcrypt, traceback
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import User, Advisor, Student, ProdiAdmin

# ──────────────────────────────────────────────
# Mapping: nama_resmi Neosia → label AIMS baku
# ──────────────────────────────────────────────
PRODI_MAP = {
    "SASTRA JEPANG - S1":                              "Sastra Jepang",
    "SASTRA PRANCIS - S1":                             "Sastra Prancis",
    "PARIWISATA - S1":                                 "Pariwisata",
    "ILMU SEJARAH - S1":                               "Ilmu Sejarah",
    "SASTRA BUGIS-MAKASSAR - S1":                      "Sastra Daerah",
    "SASTRA INGGRIS - S1":                             "Sastra Inggris",
    "SASTRA INDONESIA - S1":                           "Sastra Indonesia",
    "SASTRA ARAB - S1":                                "Sastra Arab",
    "SASTRA ASIA BARAT - S1":                          "Sastra Arab",
    "ARKEOLOGI - S1":                                  "Arkeologi",
    "SASTRA MANDARIN - S1":                            "Sastra Mandarin",
    "BAHASA MANDARIN & KEBUDAYAAN TIONGKOK - S1":      "Sastra Mandarin",
    "BAHASA MANDARIN DAN KEBUDAYAAN TIONGKOK - S1":    "Sastra Mandarin",
    "KAJIAN BUDAYA - S2":                              "Kajian Budaya (S2)",
    "LINGUISTIK - S2":                                 "Linguistik (S2)",
    "BAHASA INGGRIS - S2":                             "Sastra Inggris",
    "BAHASA INDONESIA - S2":                           "Sastra Indonesia",
    "SEJARAH - S2":                                    "Ilmu Sejarah",
    "SASTRA INGGRIS - S3":                             "Sastra Inggris",
    "BAHASA INGGRIS - S3":                             "Bahasa Inggris (S3)",
    "ILMU LINGUISTIK - S3":                            "Ilmu Linguistik (S3)",
    "SASTRA INDONESIA - S3":                           "Sastra Indonesia (S3)",
}

STATUS_MAP = {
    "A": "Aktif",
    "L": "Lulus",
    "D": "Drop Out",
    "K": "Cuti",
    "H": "Non Aktif",
    "N": "Non Aktif",
    "C": "Non Aktif",
}

ANGKATAN_MIN = 2019
ANGKATAN_MAX = 2025

# Gunakan dump terbaru jika tersedia
_FULL_DUMP  = "plugins/academic-connector/pa_dump_all_full.json"
_OLD_DUMP   = "plugins/academic-connector/pa_dump_all.json"
DUMP_PATH   = _FULL_DUMP if os.path.exists(_FULL_DUMP) else _OLD_DUMP

DEFAULT_PW_HASH = bcrypt.hashpw(b"password123", bcrypt.gensalt(rounds=12)).decode()

def get_or_create_user(db, username: str, role: str) -> User:
    u = db.query(User).filter(User.username == username).first()
    if not u:
        u = User(username=username, hashed_password=DEFAULT_PW_HASH, role=role)
        db.add(u)
        db.flush()
    elif u.role != role:
        u.role = role
    return u

def upsert_advisor(db, dosen: dict) -> int | None:
    """Insert-or-update satu dosen PA, kembalikan advisor.id."""
    nip   = str(dosen.get("nip") or dosen.get("nidn") or dosen.get("id") or "").strip()
    nidn  = str(dosen.get("nidn") or "").strip()
    nama  = (dosen.get("nama") or f"Dosen {nip}").strip()

    if not nip:
        return None

    username = nip or nidn
    u = get_or_create_user(db, username, "ADVISOR")

    adv = db.query(Advisor).filter(Advisor.user_id == u.id).first()
    if not adv:
        adv = Advisor(user_id=u.id, nama=nama)
        db.add(adv)
        db.flush()
    else:
        # Update nama jika berubah
        if adv.nama != nama:
            adv.nama = nama

    return adv.id

def resolve_prodi_name(raw_prodi) -> str:
    """Normalisasi nama prodi dari objek dict atau string Neosia."""
    if isinstance(raw_prodi, dict):
        nama_resmi = raw_prodi.get("nama_resmi", "")
    else:
        nama_resmi = str(raw_prodi or "")

    # Coba exact match dulu
    mapped = PRODI_MAP.get(nama_resmi.upper())
    if mapped:
        return mapped

    # Fallback: coba partial match
    upper = nama_resmi.upper()
    for key, val in PRODI_MAP.items():
        if key in upper or upper in key:
            return val

    # Fallback ultimate: title-case dari nama_resmi tanpa kode jenjang
    clean = nama_resmi.replace(" - S1", "").replace(" - S2", "").strip()
    return clean.title() if clean else "Tidak Diketahui"

def upsert_student(db, mhs: dict, advisor_id: int | None) -> int | None:
    """Insert-or-update satu mahasiswa, kembalikan student.id."""
    nim       = str(mhs.get("nim") or "").strip()
    nama      = (mhs.get("nama_mahasiswa") or mhs.get("nama") or "").strip()
    angkatan  = mhs.get("angkatan")
    kode_stat = mhs.get("kode_status", "A")
    wa        = str(mhs.get("whatsapp") or "").strip()
    raw_prodi = mhs.get("prodi")

    if not nim or not angkatan:
        return None

    angkatan = int(angkatan)
    if angkatan < ANGKATAN_MIN or angkatan > ANGKATAN_MAX:
        return None  # Lewati di luar range

    status = STATUS_MAP.get(str(kode_stat).upper(), "Aktif")
    prodi  = resolve_prodi_name(raw_prodi)

    # Estimasi semester dari angkatan
    semester = max(1, min(14, (2026 - angkatan) * 2))

    # User login untuk mahasiswa (username = nim)
    u = get_or_create_user(db, nim, "STUDENT")

    st = db.query(Student).filter(Student.nim == nim).first()
    if not st:
        st = Student(
            user_id        = u.id,
            nim            = nim,
            nama           = nama,
            angkatan       = angkatan,
            semester       = semester,
            prodi          = prodi,
            email          = "",
            nomor_whatsapp = wa,
            status         = status,
            advisor_id     = advisor_id,
        )
        db.add(st)
        db.flush()
        return st.id
    else:
        # Update field-field yang mungkin berubah — JANGAN overwrite data yang lebih lengkap
        if nama and st.nama != nama:
            st.nama = nama
        if wa and not st.nomor_whatsapp:
            st.nomor_whatsapp = wa
        if status and st.status != status:
            st.status = status
        if prodi and prodi != "Tidak Diketahui":
            st.prodi = prodi
        if advisor_id and not st.advisor_id:
            st.advisor_id = advisor_id
        return st.id

# ───────── MAIN ─────────
def main():
    if not os.path.exists(DUMP_PATH):
        print(f"[ERROR] Dump tidak ditemukan: {DUMP_PATH}")
        sys.exit(1)

    print(f"[{datetime.now():%H:%M:%S}] Membaca dump Neosia …")
    with open(DUMP_PATH, "r", encoding="utf-8") as f:
        pa_list = json.load(f)

    print(f"[{datetime.now():%H:%M:%S}] Total record PA dalam dump : {len(pa_list)}")

    db = SessionLocal()
    total_advisors  = 0
    total_students  = 0
    skipped_angkatan = 0
    errors          = 0

    BATCH = 500  # commit per batch agar tidak OOM

    try:
        for idx, pa_rec in enumerate(pa_list, 1):
            dosen     = pa_rec.get("dosen") or {}
            mhs_list  = pa_rec.get("mahasiswas") or []

            # 1. Upsert Dosen PA
            try:
                adv_id = upsert_advisor(db, dosen)
                if adv_id:
                    total_advisors += 1
            except Exception as e:
                adv_id = None
                errors += 1
                print(f"  [WARN] Dosen skip: {e}")

            # 2. Upsert tiap Mahasiswa
            for mhs in mhs_list:
                try:
                    ang = mhs.get("angkatan")
                    if ang and not (ANGKATAN_MIN <= int(ang) <= ANGKATAN_MAX):
                        skipped_angkatan += 1
                        continue
                    
                    sid = upsert_student(db, mhs, adv_id)
                    if sid:
                        total_students += 1
                except Exception as e:
                    errors += 1
                    # Jangan print setiap error agar tidak banjir
                    if errors <= 10:
                        print(f"  [WARN] Mahasiswa skip ({mhs.get('nim')}): {e}")

            # Commit per batch
            if idx % BATCH == 0:
                db.commit()
                pct = idx / len(pa_list) * 100
                print(f"  [{datetime.now():%H:%M:%S}] Progress: {idx}/{len(pa_list)} PA ({pct:.1f}%) "
                      f"| Dosen: {total_advisors} | Mhs: {total_students}")

        # Final commit
        db.commit()

    except Exception as e:
        db.rollback()
        print(f"[FATAL] {e}")
        traceback.print_exc()
    finally:
        db.close()

    print()
    print("=" * 55)
    print(f"  ✅  Sinkronisasi Neosia → AIMS selesai!")
    print(f"  👨‍🏫 Dosen PA terimport  : {total_advisors}")
    print(f"  🎓 Mahasiswa 2019-2025 : {total_students}")
    print(f"  ⏭️  Lewati (luar range) : {skipped_angkatan}")
    print(f"  ⚠️  Error kecil         : {errors}")
    print("=" * 55)

if __name__ == "__main__":
    main()
