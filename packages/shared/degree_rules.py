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

def evaluate_academic_risk(prodi: str, semester: int, total_sks: int, ipk: float) -> str:
    """
    Mengevaluasi status risiko akademik (HIGH_RISK, Warning, Aman)
    berdasarkan aturan jenjang studi, semester, total SKS, dan IPK.
    """
    level = get_degree_level(prodi)
    rules = DEGREE_RULES.get(level, DEGREE_RULES["S1"])
    
    # 1. Aturan Khusus Zona Merah berdasarkan jenjang
    if level == "S1":
        # S1 yang telah semester 14, namun belum mencapai 144 SKS dan IPK dibawah 2.5
        if semester >= 14 and (total_sks < 144 or ipk < 2.5):
            return "HIGH_RISK"
    elif level == "S2":
        # S2 yang sudah 6 semester atau lebih tapi belum mencapai 46 SKS
        if semester >= 6 and total_sks < 46:
            return "HIGH_RISK"
    elif level == "S3":
        # S3 yang sudah semester 10 atau lebih tapi belum mencapai 65 SKS
        if semester >= 10 and total_sks < 65:
            return "HIGH_RISK"
            
    # 2. Aturan Umum (Fail-safe)
    if ipk < 2.0:
        return "HIGH_RISK"
        
    # Perhatikan: kita mengubah aturan max semester lama agar tidak conflict.
    # Jika dia sudah di semester maksimal TAPI memenuhi syarat di atas (SKS & IPK cukup),
    # dia akan lolos dari block khusus di atas. Kita asumsikan dia masuk masa evaluasi/warning.
    if semester > rules["max_semesters"]:
        # Lewat batas waktu -> DO / High Risk
        return "HIGH_RISK"
        
    # 3. Warning (Zona Kuning)
    if ipk < 2.75 or semester >= rules["warning_semesters"]:
        return "Warning"
        
    # 4. Aman (Zona Hijau)
    return "Aman"
