"""
degree_rules.py — Definisi Aturan Akademik Berdasarkan Jenjang (S1, S2, S3)

Aturan Akademik Unhas & AIMS:
- S1: Syarat SKS Lulus = 144, Maksimal Semester = 14 (7 Tahun)
- S2: Syarat SKS Lulus = 46,  Maksimal Semester = 6  (3 Tahun)
- S3: Syarat SKS Lulus = 65,  Maksimal Semester = 10 (5 Tahun)
"""

DEGREE_RULES = {
    "S1": {
        "min_sks": 144,
        "max_semesters": 14,
        "max_years": 7,
        "warning_semesters": 8,
        "warning_years": 5
    },
    "S2": {
        "min_sks": 46,
        "max_semesters": 6,
        "max_years": 3,
        "warning_semesters": 4,
        "warning_years": 2
    },
    "S3": {
        "min_sks": 65,
        "max_semesters": 10,
        "max_years": 5,
        "warning_semesters": 6,
        "warning_years": 3
    }
}

def get_degree_level(prodi: str) -> str:
    """Deteksi jenjang studi (S1, S2, S3) dari nama Program Studi."""
    if not prodi:
        return "S1"
    p = str(prodi).upper()
    if "(S3)" in p or "DOKTOR" in p or "S3" in p or "(S-3)" in p:
        return "S3"
    if "(S2)" in p or "MAGISTER" in p or "S2" in p or "(S-2)" in p:
        return "S2"
    return "S1"

def get_degree_rules(prodi: str) -> dict:
    """Ambil aturan SKS dan semester berdasarkan jenjang prodi."""
    level = get_degree_level(prodi)
    return DEGREE_RULES.get(level, DEGREE_RULES["S1"])

def evaluate_academic_risk(prodi: str, semester: int, total_sks: int, ipk: float, status: str = "Aktif") -> str:
    """
    Mengevaluasi status risiko akademik (HIGH_RISK, Warning, Aman)
    berdasarkan aturan jenjang studi, semester, total SKS, IPK, dan status keaktifan mahasiswa.
    """
    if status:
        st_lower = str(status).lower()
        if any(kw in st_lower for kw in ["pindah", "keluar", "drop", "lulus", "non aktif", "non-aktif", "henti"]):
            return "Aman"

    level = get_degree_level(prodi)
    rules = DEGREE_RULES.get(level, DEGREE_RULES["S1"])
    
    # 1. Mahasiswa Baru (Semester 1 / IPK 0.0) -> Aman (Zona Hijau)
    if semester <= 1 or (ipk == 0.0 and total_sks == 0):
        return "Aman"
        
    # 2. Mahasiswa yang sudah tuntas SKS target & IPK memadai -> Aman (Zona Hijau)
    if total_sks >= rules["min_sks"] and ipk >= 2.00:
        return "Aman"

    # 3. ZONA MERAH (HIGH_RISK / DO Kritis)
    # a. Mahasiswa S1 Semester >= 14 OTOMATIS masuk Zona Merah
    if level == "S1" and semester >= 14:
        return "HIGH_RISK"

    # b. IPK Kritis (< 2.00) setelah menempuh minimal 1 semester
    if 0.0 < ipk < 2.00:
        return "HIGH_RISK"
        
    # c. Kriteria DO Kritis S2 / S3
    if level == "S2":
        if semester >= 6 and (total_sks < 30 or ipk < 2.50):
            return "HIGH_RISK"
        if semester > 6 and (total_sks < 36 or ipk < 2.75):
            return "HIGH_RISK"
    elif level == "S3":
        if semester >= 10 and (total_sks < 40 or ipk < 2.75):
            return "HIGH_RISK"
        if semester > 10 and (total_sks < 50 or ipk < 3.00):
            return "HIGH_RISK"

    # 4. ZONA KUNING (Warning / Perhatian Akademik)
    # Aturan Khusus S1: Mahasiswa S1 di atas 2.74 TIDAK BOLEH masuk Zona Kuning.
    # Zona Kuning S1 hanya untuk IPK 2.00 - 2.74 (selama semester < 14).
    if level == "S1":
        if 2.00 <= ipk <= 2.74 and semester < 14:
            return "Warning"
        return "Aman"

    # Zona Kuning S2 / S3:
    if 2.00 <= ipk < 2.75:
        return "Warning"
    if level == "S2" and semester >= 5 and total_sks < 46:
        return "Warning"
    if level == "S3" and semester >= 7 and total_sks < 65:
        return "Warning"

    # 5. Default -> Aman (Zona Hijau)
    return "Aman"
