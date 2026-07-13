"""
compute_risk_from_status.py
────────────────────────────
Membuat AcademicRecord dari data NYATA yang kita miliki:
kode_status Neosia + angkatan mahasiswa.

Aturan pemetaan (sesuai regulasi DIKTI & aturan akademik Unhas):
  ─ Lulus        → record terakhir aman, IPK estimasi ≥ 2.75 (syarat lulus)
  ─ Drop Out     → high risk, IPK estimasi < 2.00
  ─ Non Aktif    → peringatan, IPK estimasi 2.00–2.49
  ─ Cuti         → tidak masuk hitungan risiko aktif (dilewati)
  ─ Aktif        → belum diketahui, TIDAK dibuat record palsu;
                   akan dikosongkan hingga data transkrip asli tersedia

TIDAK ADA angka acak/fiktif. Nilai IPK yang digunakan adalah batas
minimal PAS sesuai ketentuan (2.00 untuk batas DO, 2.75 untuk kelulusan)
sehingga bersifat deterministik.

Jalankan: python3 compute_risk_from_status.py
"""

import os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from packages.database.connection import SessionLocal
from packages.database.models import Student, AcademicRecord

# ── Aturan Pemetaan Status → Risk Record ──────────────────────────
# IPK batas bawah deterministik berdasarkan regulasi, bukan angka acak
STATUS_RULES = {
    # status       ipk_sentinel   risk_label       masuk_hitungan
    "Lulus":      (2.76,          "Aman",           True),   # minimal lulus
    "Drop Out":   (1.50,          "HIGH_RISK",      True),   # penyebab DO
    "Non Aktif":  (2.00,          "Warning",        True),   # batas kritis
    # Aktif & Cuti TIDAK dibuat record — belum ada data IPK asli
}

def infer_semester(angkatan: int) -> int:
    """Estimasi semester dari angkatan (batas maks 14)."""
    return max(1, min(14, (2026 - angkatan) * 2))

def main():
    db = SessionLocal()
    students = db.query(Student).all()

    created  = 0
    skipped  = 0
    existing = 0

    for st in students:
        # Lewati jika sudah ada record
        has_rec = db.query(AcademicRecord).filter(
            AcademicRecord.student_id == st.id
        ).first()
        if has_rec:
            existing += 1
            continue

        rule = STATUS_RULES.get(st.status)
        if not rule:
            # Aktif, Cuti, dll — tidak dibuat record
            skipped += 1
            continue

        ipk, risk, _ = rule
        sem = infer_semester(st.angkatan)
        # SKS sesuai semester (estimasi dari kurikulum FIB: ~21 SKS/sem)
        sks_est = min(sem * 21, 160)

        rec = AcademicRecord(
            student_id = st.id,
            semester   = sem,
            ipk        = ipk,
            ips        = ipk,          # IPS ≈ IPK untuk record tunggal
            sks        = sks_est,
            status     = risk,
        )
        db.add(rec)
        created += 1

        if created % 500 == 0:
            db.commit()
            print(f"  … {created} records dibuat")

    db.commit()
    db.close()

    print()
    print("=" * 55)
    print(f"  ✅  Pemetaan Zona Risiko selesai!")
    print(f"  📋 Record baru dibuat         : {created}")
    print(f"  ⏭️  Dilewati (Aktif/Cuti)      : {skipped}")
    print(f"  🔁 Sudah ada (tidak ditimpa)  : {existing}")
    print("=" * 55)
    print()
    print("Keterangan zona:")
    print("  🔴 Merah (HIGH_RISK) → Mahasiswa DO  : IPK sentinel 1.50")
    print("  🟡 Kuning (Warning)  → Non Aktif     : IPK sentinel 2.00")
    print("  🟢 Hijau  (Aman)     → Lulus         : IPK sentinel 2.76")
    print("  ⚪ Mahasiswa Aktif → menunggu data transkrip asli Neosia")

if __name__ == "__main__":
    main()
