"""
AIMS — Seed Data Lengkap
Fakultas Ilmu Budaya (FIB)
Program Studi: 9 Prodi
"""
import os
import sys
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from packages.database.connection import SessionLocal
from packages.database.models import Student, Advisor, Course, Grade, AcademicRecord, User, AgentLog, NotificationLog, ConsultationLog, Reminder
import bcrypt

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode('utf-8'), salt).decode('utf-8')

# ─────────────────────────────────────────────────────────────────
#  MATA KULIAH (per prodi + MKU bersama)
# ─────────────────────────────────────────────────────────────────
COURSES = [
    # ── MKU Bersama ────────────────────────────────────────────
    {"kode":"MKU101","nama":"Bahasa Indonesia Akademik",         "semester":1,"sks":2},
    {"kode":"MKU102","nama":"Bahasa Inggris Umum",               "semester":1,"sks":2},
    {"kode":"MKU103","nama":"Pendidikan Kewarganegaraan",         "semester":1,"sks":2},
    {"kode":"MKU104","nama":"Pendidikan Agama",                   "semester":1,"sks":2},
    {"kode":"MKU105","nama":"Pengantar Ilmu Budaya",              "semester":1,"sks":3},
    {"kode":"MKU106","nama":"Metodologi Penelitian Humaniora",    "semester":3,"sks":3},
    {"kode":"MKU107","nama":"Filsafat Ilmu",                      "semester":4,"sks":2},
    {"kode":"MKU108","nama":"Skripsi / Tugas Akhir",              "semester":8,"sks":6},

    # ── Sastra Prancis ──────────────────────────────────────────
    {"kode":"FRN101","nama":"Bahasa Prancis Dasar I",             "semester":1,"sks":4},
    {"kode":"FRN102","nama":"Bahasa Prancis Dasar II",            "semester":2,"sks":4},
    {"kode":"FRN103","nama":"Tata Bahasa Prancis",                "semester":2,"sks":3},
    {"kode":"FRN201","nama":"Sastra Prancis Klasik",              "semester":3,"sks":3},
    {"kode":"FRN202","nama":"Linguistik Prancis",                 "semester":3,"sks":3},
    {"kode":"FRN203","nama":"Terjemahan Prancis–Indonesia",        "semester":4,"sks":3},
    {"kode":"FRN301","nama":"Sastra Prancis Modern",              "semester":5,"sks":3},
    {"kode":"FRN302","nama":"Sosiolinguistik Prancis",            "semester":5,"sks":3},
    {"kode":"FRN401","nama":"Penulisan Akademik Bahasa Prancis",  "semester":6,"sks":3},
    {"kode":"FRN402","nama":"Pragmatik Prancis",                  "semester":7,"sks":3},

    # ── Sastra Indonesia ────────────────────────────────────────
    {"kode":"IND101","nama":"Fonologi Bahasa Indonesia",          "semester":1,"sks":3},
    {"kode":"IND102","nama":"Morfologi Bahasa Indonesia",         "semester":2,"sks":3},
    {"kode":"IND103","nama":"Sintaksis Bahasa Indonesia",         "semester":3,"sks":3},
    {"kode":"IND104","nama":"Semantik & Pragmatik",               "semester":3,"sks":3},
    {"kode":"IND201","nama":"Sastra Indonesia Lama",              "semester":4,"sks":3},
    {"kode":"IND202","nama":"Sastra Indonesia Modern",            "semester":4,"sks":3},
    {"kode":"IND203","nama":"Kritik Sastra",                      "semester":5,"sks":3},
    {"kode":"IND204","nama":"Teori Sastra",                       "semester":5,"sks":3},
    {"kode":"IND301","nama":"Penulisan Kreatif",                  "semester":6,"sks":3},
    {"kode":"IND302","nama":"Psikolinguistik",                    "semester":6,"sks":3},

    # ── Sastra Inggris ──────────────────────────────────────────
    {"kode":"ENG101","nama":"English Pronunciation",              "semester":1,"sks":2},
    {"kode":"ENG102","nama":"English Grammar & Composition",      "semester":2,"sks":3},
    {"kode":"ENG103","nama":"Introduction to Literature",         "semester":2,"sks":3},
    {"kode":"ENG201","nama":"British Literature",                 "semester":3,"sks":3},
    {"kode":"ENG202","nama":"American Literature",                "semester":4,"sks":3},
    {"kode":"ENG203","nama":"Translation Studies",                "semester":4,"sks":3},
    {"kode":"ENG301","nama":"Applied Linguistics",                "semester":5,"sks":3},
    {"kode":"ENG302","nama":"Discourse Analysis",                 "semester":5,"sks":3},
    {"kode":"ENG401","nama":"TEFL Methodology",                   "semester":6,"sks":3},
    {"kode":"ENG402","nama":"Sociolinguistics",                   "semester":6,"sks":3},

    # ── Sastra Mandarin ─────────────────────────────────────────
    {"kode":"MAN101","nama":"Hanyu Pinyin & Kosakata Dasar",      "semester":1,"sks":4},
    {"kode":"MAN102","nama":"Tata Bahasa Mandarin Dasar",         "semester":2,"sks":3},
    {"kode":"MAN103","nama":"Membaca & Menulis Hanzi",            "semester":2,"sks":3},
    {"kode":"MAN201","nama":"Percakapan Mandarin Madya",          "semester":3,"sks":3},
    {"kode":"MAN202","nama":"Linguistik Tionghoa",                "semester":3,"sks":3},
    {"kode":"MAN203","nama":"Sastra Tionghoa Klasik",             "semester":4,"sks":3},
    {"kode":"MAN301","nama":"Terjemahan Mandarin–Indonesia",       "semester":5,"sks":3},
    {"kode":"MAN302","nama":"Kebudayaan Tionghoa",                "semester":5,"sks":2},
    {"kode":"MAN401","nama":"Sastra Tionghoa Modern",             "semester":6,"sks":3},

    # ── Sastra Jepang ───────────────────────────────────────────
    {"kode":"JPN101","nama":"Nihongo Dasar I (Hiragana/Katakana)","semester":1,"sks":4},
    {"kode":"JPN102","nama":"Nihongo Dasar II",                   "semester":2,"sks":4},
    {"kode":"JPN103","nama":"Kanji Dasar",                        "semester":2,"sks":2},
    {"kode":"JPN201","nama":"Linguistik Bahasa Jepang",           "semester":3,"sks":3},
    {"kode":"JPN202","nama":"Sastra Jepang Klasik",               "semester":3,"sks":3},
    {"kode":"JPN203","nama":"Sastra Jepang Modern",               "semester":4,"sks":3},
    {"kode":"JPN301","nama":"Terjemahan Jepang–Indonesia",         "semester":5,"sks":3},
    {"kode":"JPN302","nama":"Kebudayaan & Masyarakat Jepang",     "semester":5,"sks":2},
    {"kode":"JPN401","nama":"Kajian Anime & Pop Culture Jepang",  "semester":6,"sks":2},

    # ── Sastra Arab ─────────────────────────────────────────────
    {"kode":"ARB101","nama":"Bahasa Arab Dasar I",                "semester":1,"sks":4},
    {"kode":"ARB102","nama":"Bahasa Arab Dasar II",               "semester":2,"sks":4},
    {"kode":"ARB103","nama":"Nahwu Sharaf Dasar",                 "semester":2,"sks":3},
    {"kode":"ARB201","nama":"Balaghah (Retorika Arab)",           "semester":3,"sks":3},
    {"kode":"ARB202","nama":"Sastra Arab Klasik",                 "semester":3,"sks":3},
    {"kode":"ARB203","nama":"Sastra Arab Modern",                 "semester":4,"sks":3},
    {"kode":"ARB301","nama":"Terjemahan Arab–Indonesia",           "semester":5,"sks":3},
    {"kode":"ARB302","nama":"Linguistik Arab",                    "semester":5,"sks":3},
    {"kode":"ARB401","nama":"Al-Qur'an dan Sastra",               "semester":6,"sks":3},

    # ── Ilmu Sejarah ────────────────────────────────────────────
    {"kode":"SEJ101","nama":"Pengantar Ilmu Sejarah",             "semester":1,"sks":3},
    {"kode":"SEJ102","nama":"Sejarah Indonesia Kuno",             "semester":2,"sks":3},
    {"kode":"SEJ103","nama":"Sejarah Indonesia Modern",           "semester":2,"sks":3},
    {"kode":"SEJ201","nama":"Sejarah Asia Tenggara",              "semester":3,"sks":3},
    {"kode":"SEJ202","nama":"Historiografi Indonesia",            "semester":3,"sks":3},
    {"kode":"SEJ203","nama":"Sejarah Kebudayaan",                 "semester":4,"sks":3},
    {"kode":"SEJ301","nama":"Metode Penelitian Sejarah",          "semester":5,"sks":3},
    {"kode":"SEJ302","nama":"Sejarah Sosial Ekonomi",             "semester":5,"sks":3},
    {"kode":"SEJ401","nama":"Sejarah Lokal & Daerah",             "semester":6,"sks":3},
    {"kode":"SEJ402","nama":"Sejarah Lisan (Oral History)",       "semester":7,"sks":3},

    # ── Arkeologi ───────────────────────────────────────────────
    {"kode":"ARK101","nama":"Pengantar Arkeologi",                "semester":1,"sks":3},
    {"kode":"ARK102","nama":"Prasejarah Indonesia",               "semester":2,"sks":3},
    {"kode":"ARK103","nama":"Arkeologi Hindu-Buddha",             "semester":2,"sks":3},
    {"kode":"ARK201","nama":"Metode Survei Arkeologi",            "semester":3,"sks":3},
    {"kode":"ARK202","nama":"Arkeologi Islam di Indonesia",       "semester":3,"sks":3},
    {"kode":"ARK203","nama":"Analisis Temuan Arkeologis",         "semester":4,"sks":3},
    {"kode":"ARK301","nama":"GIS untuk Arkeologi",                "semester":5,"sks":3},
    {"kode":"ARK302","nama":"Konservasi Warisan Budaya",          "semester":5,"sks":3},
    {"kode":"ARK401","nama":"Etnoarkeologi",                      "semester":6,"sks":3},
    {"kode":"ARK402","nama":"Arkeologi Bawah Air",                "semester":7,"sks":2},

    # ── Sastra Daerah ───────────────────────────────────────────
    {"kode":"DAE101","nama":"Bahasa Daerah Nusantara",            "semester":1,"sks":3},
    {"kode":"DAE102","nama":"Sastra Lisan Nusantara",             "semester":2,"sks":3},
    {"kode":"DAE103","nama":"Folklor Indonesia",                  "semester":2,"sks":3},
    {"kode":"DAE201","nama":"Sastra Jawa Kuno",                   "semester":3,"sks":3},
    {"kode":"DAE202","nama":"Sastra Melayu Lama",                 "semester":3,"sks":3},
    {"kode":"DAE203","nama":"Kebudayaan Etnik Nusantara",         "semester":4,"sks":3},
    {"kode":"DAE301","nama":"Transkripsi Naskah Kuno",            "semester":5,"sks":3},
    {"kode":"DAE302","nama":"Filologi Indonesia",                 "semester":5,"sks":3},
    {"kode":"DAE401","nazwa":"Kajian Manuskrip Lokal",            "semester":6,"sks":3},
    {"kode":"DAE402","nama":"Dokumentasi Budaya Digital",         "semester":7,"sks":3},
]
# fix typo
for c in COURSES:
    if "nazwa" in c:
        c["nama"] = c.pop("nazwa")

# ─────────────────────────────────────────────────────────────────
#  DOSEN PA (2 per prodi, 18 total)
# ─────────────────────────────────────────────────────────────────
ADVISORS = [
    {"username":"PA_FRN1","nama":"Dr. Isabelle Supriyanto, M.Hum",  "email":"isabelle@fib.ac.id",  "whatsapp":"08111000001","prodi":"Sastra Prancis"},
    {"username":"PA_FRN2","nama":"Prof. Luc Haryanto, Ph.D",        "email":"luc@fib.ac.id",        "whatsapp":"08111000002","prodi":"Sastra Prancis"},
    {"username":"PA_IND1","nama":"Dr. Sari Rahayu, M.Hum",          "email":"sari@fib.ac.id",       "whatsapp":"08111000003","prodi":"Sastra Indonesia"},
    {"username":"PA_IND2","nama":"Prof. Bambang Nugroho, M.A",      "email":"bambang@fib.ac.id",    "whatsapp":"08111000004","prodi":"Sastra Indonesia"},
    {"username":"PA_ENG1","nama":"Dr. Anita Susanto, M.A",          "email":"anita@fib.ac.id",      "whatsapp":"08111000005","prodi":"Sastra Inggris"},
    {"username":"PA_ENG2","nama":"Prof. Rizky Pratama, Ph.D",       "email":"rizky@fib.ac.id",      "whatsapp":"08111000006","prodi":"Sastra Inggris"},
    {"username":"PA_MAN1","nama":"Dr. Lin Megawati, M.Hum",         "email":"lin@fib.ac.id",        "whatsapp":"08111000007","prodi":"Sastra Mandarin"},
    {"username":"PA_MAN2","nama":"Prof. Huang Setiawan, M.A",       "email":"huang@fib.ac.id",      "whatsapp":"08111000008","prodi":"Sastra Mandarin"},
    {"username":"PA_JPN1","nama":"Dr. Yuki Rahmawati, M.Hum",       "email":"yuki@fib.ac.id",       "whatsapp":"08111000009","prodi":"Sastra Jepang"},
    {"username":"PA_JPN2","nama":"Prof. Kenji Widodo, Ph.D",        "email":"kenji@fib.ac.id",      "whatsapp":"08111000010","prodi":"Sastra Jepang"},
    {"username":"PA_ARB1","nama":"Dr. Ahmad Fauzi, M.A",            "email":"ahmad@fib.ac.id",      "whatsapp":"08111000011","prodi":"Sastra Arab"},
    {"username":"PA_ARB2","nama":"Prof. Fatimah Zahra, M.Hum",      "email":"fatimah@fib.ac.id",    "whatsapp":"08111000012","prodi":"Sastra Arab"},
    {"username":"PA_SEJ1","nama":"Dr. Budi Santoso, M.Si",          "email":"budi@fib.ac.id",       "whatsapp":"08111000013","prodi":"Ilmu Sejarah"},
    {"username":"PA_SEJ2","nama":"Prof. Siti Aminah, M.Hum",        "email":"siti@fib.ac.id",       "whatsapp":"08111000014","prodi":"Ilmu Sejarah"},
    {"username":"PA_ARK1","nama":"Dr. Wiwit Kusumawati, M.Si",      "email":"wiwit@fib.ac.id",      "whatsapp":"08111000015","prodi":"Arkeologi"},
    {"username":"PA_ARK2","nama":"Prof. Hendra Wijaya, Ph.D",       "email":"hendra@fib.ac.id",     "whatsapp":"08111000016","prodi":"Arkeologi"},
    {"username":"PA_DAE1","nama":"Dr. Purwanti, M.Hum",             "email":"purwanti@fib.ac.id",   "whatsapp":"08111000017","prodi":"Sastra Daerah"},
    {"username":"PA_DAE2","nama":"Prof. Sutrisno Hadiprawiro, M.A", "email":"sutrisno@fib.ac.id",   "whatsapp":"08111000018","prodi":"Sastra Daerah"},
]

# ─────────────────────────────────────────────────────────────────
#  MAHASISWA (4-6 per prodi, ~45 total)
# ─────────────────────────────────────────────────────────────────
# NIM format: TAHUN + KODE_PRODI + NOMOR (3 digit)
# Prodi: FRN=401, IND=402, ENG=403, MAN=404, JPN=405, ARB=406, SEJ=407, ARK=408, DAE=409

STUDENTS = [
    # ── Sastra Prancis ──────────────────────────────────────────
    {"nim":"2021401001","nama":"Aurélie Ratnasari",    "angkatan":2021,"semester":7,"prodi":"Sastra Prancis",    "email":"aurelie@mhs.fib.ac.id", "nomor_whatsapp":"0812000001","status":"Aktif",   "ipk":3.65,"ips":3.50},
    {"nim":"2022401001","nama":"Pierre Cahyono",        "angkatan":2022,"semester":5,"prodi":"Sastra Prancis",    "email":"pierre@mhs.fib.ac.id",  "nomor_whatsapp":"0812000002","status":"Aktif",   "ipk":3.20,"ips":3.10},
    {"nim":"2022401002","nama":"Marie Priyandari",      "angkatan":2022,"semester":5,"prodi":"Sastra Prancis",    "email":"marie@mhs.fib.ac.id",   "nomor_whatsapp":"0812000003","status":"Aktif",   "ipk":2.10,"ips":1.90},  # Warning
    {"nim":"2023401001","nama":"Jean Kurniawan",        "angkatan":2023,"semester":3,"prodi":"Sastra Prancis",    "email":"jean@mhs.fib.ac.id",    "nomor_whatsapp":"0812000004","status":"Aktif",   "ipk":3.80,"ips":3.85},
    {"nim":"2020401001","nama":"Delphine Saputri",      "angkatan":2020,"semester":9,"prodi":"Sastra Prancis",    "email":"delphine@mhs.fib.ac.id","nomor_whatsapp":"0812000005","status":"Aktif",   "ipk":1.75,"ips":1.50},  # HIGH_RISK

    # ── Sastra Indonesia ────────────────────────────────────────
    {"nim":"2021402001","nama":"Slamet Riyadi",         "angkatan":2021,"semester":7,"prodi":"Sastra Indonesia",  "email":"slamet@mhs.fib.ac.id",  "nomor_whatsapp":"0812001001","status":"Aktif",   "ipk":3.45,"ips":3.30},
    {"nim":"2022402001","nama":"Nurul Hidayah",         "angkatan":2022,"semester":5,"prodi":"Sastra Indonesia",  "email":"nurul@mhs.fib.ac.id",   "nomor_whatsapp":"0812001002","status":"Aktif",   "ipk":3.70,"ips":3.60},
    {"nim":"2022402002","nama":"Bagas Pramono",         "angkatan":2022,"semester":5,"prodi":"Sastra Indonesia",  "email":"bagas@mhs.fib.ac.id",   "nomor_whatsapp":"0812001003","status":"Aktif",   "ipk":2.40,"ips":2.20},  # Warning
    {"nim":"2023402001","nama":"Rizka Amalia",          "angkatan":2023,"semester":3,"prodi":"Sastra Indonesia",  "email":"rizka@mhs.fib.ac.id",   "nomor_whatsapp":"0812001004","status":"Aktif",   "ipk":3.90,"ips":3.95},
    {"nim":"2021402002","nama":"Arya Darmawan",         "angkatan":2021,"semester":7,"prodi":"Sastra Indonesia",  "email":"arya@mhs.fib.ac.id",    "nomor_whatsapp":"0812001005","status":"Cuti",    "ipk":2.85,"ips":2.70},
    {"nim":"2020402001","nama":"Fitri Lestari",         "angkatan":2020,"semester":9,"prodi":"Sastra Indonesia",  "email":"fitri@mhs.fib.ac.id",   "nomor_whatsapp":"0812001006","status":"Aktif",   "ipk":1.90,"ips":1.80},  # HIGH_RISK

    # ── Sastra Inggris ──────────────────────────────────────────
    {"nim":"2021403001","nama":"Aldrian Putra",         "angkatan":2021,"semester":7,"prodi":"Sastra Inggris",    "email":"aldrian@mhs.fib.ac.id", "nomor_whatsapp":"0812002001","status":"Aktif",   "ipk":3.55,"ips":3.40},
    {"nim":"2022403001","nama":"Rachel Wulandari",      "angkatan":2022,"semester":5,"prodi":"Sastra Inggris",    "email":"rachel@mhs.fib.ac.id",  "nomor_whatsapp":"0812002002","status":"Aktif",   "ipk":3.85,"ips":3.90},
    {"nim":"2022403002","nama":"Dylan Santoso",         "angkatan":2022,"semester":5,"prodi":"Sastra Inggris",    "email":"dylan@mhs.fib.ac.id",   "nomor_whatsapp":"0812002003","status":"Aktif",   "ipk":2.05,"ips":1.95},  # Warning
    {"nim":"2023403001","nama":"Syifa Nuraeni",         "angkatan":2023,"semester":3,"prodi":"Sastra Inggris",    "email":"syifa@mhs.fib.ac.id",   "nomor_whatsapp":"0812002004","status":"Aktif",   "ipk":3.75,"ips":3.80},
    {"nim":"2020403001","nama":"Kevin Hermawan",        "angkatan":2020,"semester":9,"prodi":"Sastra Inggris",    "email":"kevin@mhs.fib.ac.id",   "nomor_whatsapp":"0812002005","status":"Aktif",   "ipk":1.70,"ips":1.60},  # HIGH_RISK
    {"nim":"2021403002","nama":"Tania Putri Dewi",     "angkatan":2021,"semester":7,"prodi":"Sastra Inggris",    "email":"tania@mhs.fib.ac.id",   "nomor_whatsapp":"0812002006","status":"Aktif",   "ipk":3.20,"ips":3.00},

    # ── Sastra Mandarin ─────────────────────────────────────────
    {"nim":"2021404001","nama":"Chen Widyaningsih",     "angkatan":2021,"semester":7,"prodi":"Sastra Mandarin",   "email":"chen@mhs.fib.ac.id",    "nomor_whatsapp":"0812003001","status":"Aktif",   "ipk":3.60,"ips":3.55},
    {"nim":"2022404001","nama":"Li Rahmawati",          "angkatan":2022,"semester":5,"prodi":"Sastra Mandarin",   "email":"li@mhs.fib.ac.id",      "nomor_whatsapp":"0812003002","status":"Aktif",   "ipk":3.30,"ips":3.20},
    {"nim":"2022404002","nama":"Wang Prasetyo",         "angkatan":2022,"semester":5,"prodi":"Sastra Mandarin",   "email":"wang@mhs.fib.ac.id",    "nomor_whatsapp":"0812003003","status":"Aktif",   "ipk":2.15,"ips":2.00},  # Warning
    {"nim":"2023404001","nama":"Mei Kusuma Dewi",       "angkatan":2023,"semester":3,"prodi":"Sastra Mandarin",   "email":"mei@mhs.fib.ac.id",     "nomor_whatsapp":"0812003004","status":"Aktif",   "ipk":3.95,"ips":4.00},
    {"nim":"2020404001","nama":"Zhang Hendra",          "angkatan":2020,"semester":9,"prodi":"Sastra Mandarin",   "email":"zhang@mhs.fib.ac.id",   "nomor_whatsapp":"0812003005","status":"Aktif",   "ipk":1.85,"ips":1.75},  # HIGH_RISK

    # ── Sastra Jepang ───────────────────────────────────────────
    {"nim":"2021405001","nama":"Yuna Permatasari",      "angkatan":2021,"semester":7,"prodi":"Sastra Jepang",     "email":"yuna@mhs.fib.ac.id",    "nomor_whatsapp":"0812004001","status":"Aktif",   "ipk":3.78,"ips":3.70},
    {"nim":"2022405001","nama":"Hiro Sulistyo",         "angkatan":2022,"semester":5,"prodi":"Sastra Jepang",     "email":"hiro@mhs.fib.ac.id",    "nomor_whatsapp":"0812004002","status":"Aktif",   "ipk":3.50,"ips":3.45},
    {"nim":"2022405002","nama":"Sakura Andini",         "angkatan":2022,"semester":5,"prodi":"Sastra Jepang",     "email":"sakura@mhs.fib.ac.id",  "nomor_whatsapp":"0812004003","status":"Aktif",   "ipk":2.25,"ips":2.10},  # Warning
    {"nim":"2023405001","nama":"Riku Fadillah",         "angkatan":2023,"semester":3,"prodi":"Sastra Jepang",     "email":"riku@mhs.fib.ac.id",    "nomor_whatsapp":"0812004004","status":"Aktif",   "ipk":3.85,"ips":3.90},
    {"nim":"2020405001","nama":"Hana Kusumawardani",    "angkatan":2020,"semester":9,"prodi":"Sastra Jepang",     "email":"hana@mhs.fib.ac.id",    "nomor_whatsapp":"0812004005","status":"Aktif",   "ipk":1.95,"ips":1.85},  # HIGH_RISK

    # ── Sastra Arab ─────────────────────────────────────────────
    {"nim":"2021406001","nama":"Umar Hakim",            "angkatan":2021,"semester":7,"prodi":"Sastra Arab",       "email":"umar@mhs.fib.ac.id",    "nomor_whatsapp":"0812005001","status":"Aktif",   "ipk":3.55,"ips":3.40},
    {"nim":"2022406001","nama":"Maryam Sholihah",       "angkatan":2022,"semester":5,"prodi":"Sastra Arab",       "email":"maryam@mhs.fib.ac.id",  "nomor_whatsapp":"0812005002","status":"Aktif",   "ipk":3.72,"ips":3.65},
    {"nim":"2022406002","nama":"Khalid Setiawan",       "angkatan":2022,"semester":5,"prodi":"Sastra Arab",       "email":"khalid@mhs.fib.ac.id",  "nomor_whatsapp":"0812005003","status":"Aktif",   "ipk":2.30,"ips":2.15},  # Warning
    {"nim":"2023406001","nama":"Zainab Nurfadila",      "angkatan":2023,"semester":3,"prodi":"Sastra Arab",       "email":"zainab@mhs.fib.ac.id",  "nomor_whatsapp":"0812005004","status":"Aktif",   "ipk":3.88,"ips":3.92},
    {"nim":"2020406001","nama":"Ibrahim Pratama",       "angkatan":2020,"semester":9,"prodi":"Sastra Arab",       "email":"ibrahim@mhs.fib.ac.id", "nomor_whatsapp":"0812005005","status":"Aktif",   "ipk":1.65,"ips":1.55},  # HIGH_RISK

    # ── Ilmu Sejarah ────────────────────────────────────────────
    {"nim":"2021407001","nama":"Hendro Wibowo",         "angkatan":2021,"semester":7,"prodi":"Ilmu Sejarah",      "email":"hendro@mhs.fib.ac.id",  "nomor_whatsapp":"0812006001","status":"Aktif",   "ipk":3.40,"ips":3.25},
    {"nim":"2022407001","nama":"Dewi Ratnawati",        "angkatan":2022,"semester":5,"prodi":"Ilmu Sejarah",      "email":"dewi@mhs.fib.ac.id",    "nomor_whatsapp":"0812006002","status":"Aktif",   "ipk":3.60,"ips":3.55},
    {"nim":"2022407002","nama":"Eko Wahyudi",           "angkatan":2022,"semester":5,"prodi":"Ilmu Sejarah",      "email":"eko@mhs.fib.ac.id",     "nomor_whatsapp":"0812006003","status":"Aktif",   "ipk":2.20,"ips":2.05},  # Warning
    {"nim":"2023407001","nama":"Putri Handayani",       "angkatan":2023,"semester":3,"prodi":"Ilmu Sejarah",      "email":"putri@mhs.fib.ac.id",   "nomor_whatsapp":"0812006004","status":"Aktif",   "ipk":3.82,"ips":3.88},
    {"nim":"2020407001","nama":"Galih Permana",         "angkatan":2020,"semester":9,"prodi":"Ilmu Sejarah",      "email":"galih@mhs.fib.ac.id",   "nomor_whatsapp":"0812006005","status":"Aktif",   "ipk":1.80,"ips":1.70},  # HIGH_RISK
    {"nim":"2021407002","nama":"Leslie Apriani",        "angkatan":2021,"semester":7,"prodi":"Ilmu Sejarah",      "email":"leslie@mhs.fib.ac.id",  "nomor_whatsapp":"0812006006","status":"Cuti",    "ipk":2.95,"ips":2.80},

    # ── Arkeologi ───────────────────────────────────────────────
    {"nim":"2021408001","nama":"Pradipta Kusuma",       "angkatan":2021,"semester":7,"prodi":"Arkeologi",         "email":"pradipta@mhs.fib.ac.id","nomor_whatsapp":"0812007001","status":"Aktif",   "ipk":3.50,"ips":3.35},
    {"nim":"2022408001","nama":"Sinta Maharani",        "angkatan":2022,"semester":5,"prodi":"Arkeologi",         "email":"sinta@mhs.fib.ac.id",   "nomor_whatsapp":"0812007002","status":"Aktif",   "ipk":3.65,"ips":3.58},
    {"nim":"2022408002","nama":"Dimas Ariyanto",        "angkatan":2022,"semester":5,"prodi":"Arkeologi",         "email":"dimas@mhs.fib.ac.id",   "nomor_whatsapp":"0812007003","status":"Aktif",   "ipk":2.35,"ips":2.20},  # Warning
    {"nim":"2023408001","nama":"Amanda Puspita",        "angkatan":2023,"semester":3,"prodi":"Arkeologi",         "email":"amanda@mhs.fib.ac.id",  "nomor_whatsapp":"0812007004","status":"Aktif",   "ipk":3.90,"ips":3.95},
    {"nim":"2020408001","nama":"Rendra Sasmita",        "angkatan":2020,"semester":9,"prodi":"Arkeologi",         "email":"rendra@mhs.fib.ac.id",  "nomor_whatsapp":"0812007005","status":"Aktif",   "ipk":1.72,"ips":1.65},  # HIGH_RISK

    # ── Sastra Daerah ───────────────────────────────────────────
    {"nim":"2021409001","nama":"Wahyu Prabowo",         "angkatan":2021,"semester":7,"prodi":"Sastra Daerah",     "email":"wahyu@mhs.fib.ac.id",   "nomor_whatsapp":"0812008001","status":"Aktif",   "ipk":3.35,"ips":3.20},
    {"nim":"2022409001","nama":"Sri Wahyuni",           "angkatan":2022,"semester":5,"prodi":"Sastra Daerah",     "email":"sri@mhs.fib.ac.id",     "nomor_whatsapp":"0812008002","status":"Aktif",   "ipk":3.55,"ips":3.48},
    {"nim":"2022409002","nama":"Anton Surya",           "angkatan":2022,"semester":5,"prodi":"Sastra Daerah",     "email":"anton@mhs.fib.ac.id",   "nomor_whatsapp":"0812008003","status":"Aktif",   "ipk":2.28,"ips":2.12},  # Warning
    {"nim":"2023409001","nama":"Indah Pertiwi",         "angkatan":2023,"semester":3,"prodi":"Sastra Daerah",     "email":"indah@mhs.fib.ac.id",   "nomor_whatsapp":"0812008004","status":"Aktif",   "ipk":3.87,"ips":3.92},
    {"nim":"2020409001","nama":"Teguh Sarwono",         "angkatan":2020,"semester":9,"prodi":"Sastra Daerah",     "email":"teguh@mhs.fib.ac.id",   "nomor_whatsapp":"0812008005","status":"Aktif",   "ipk":1.88,"ips":1.78},  # HIGH_RISK
]

# ─────────────────────────────────────────────────────────────────
#  HELPER: compute status from IPK
# ─────────────────────────────────────────────────────────────────
def compute_status(ipk: float, semester: int) -> str:
    if ipk < 2.0 or (semester >= 8 and ipk < 2.5):
        return "HIGH_RISK"
    elif ipk < 2.5:
        return "Warning"
    return "Aman"

# ─────────────────────────────────────────────────────────────────
#  SEED FUNCTION
# ─────────────────────────────────────────────────────────────────
def run_seed():
    db = SessionLocal()

    # ── Wipe existing data (order matters for FK constraints) ──
    print("🗑  Clearing existing data...")
    db.query(AgentLog).delete()
    db.query(NotificationLog).delete()
    db.query(ConsultationLog).delete()
    db.query(Reminder).delete()
    db.query(Grade).delete()
    db.query(AcademicRecord).delete()
    db.query(Student).delete()
    db.query(Course).delete()
    db.query(Advisor).delete()
    db.query(User).delete()
    db.commit()

    hashed_pw = get_password_hash("password123")

    # ── Admin ──────────────────────────────────────────────────
    print("👤 Creating admin users...")
    admin_user = User(username="admin", hashed_password=hashed_pw, role="ADMIN")
    db.add(admin_user)
    db.commit()

    # ── Mata Kuliah ───────────────────────────────────────────
    print(f"📚 Creating {len(COURSES)} courses...")
    course_models = []
    for c in COURSES:
        cm = Course(kode=c["kode"], nama=c["nama"], semester=c["semester"], sks=c["sks"])
        db.add(cm)
        course_models.append(cm)
    db.commit()

    # Build lookup: kode → Course model
    course_map = {c.kode: c for c in db.query(Course).all()}

    # ── Dosen PA ──────────────────────────────────────────────
    print(f"👨‍🏫 Creating {len(ADVISORS)} advisors...")
    advisor_models = []
    for adv in ADVISORS:
        u = User(username=adv["username"], hashed_password=hashed_pw, role="ADVISOR")
        db.add(u)
        db.commit()
        a = Advisor(
            user_id=u.id,
            nama=adv["nama"],
            email=adv["email"],
            whatsapp=adv["whatsapp"],
        )
        db.add(a)
        advisor_models.append(a)
    db.commit()

    # ── Mahasiswa + Academic Records + Grades ─────────────────
    print(f"🎓 Creating {len(STUDENTS)} students...")

    # Prodi → course kode prefix map
    prodi_course_prefix = {
        "Sastra Prancis":    ["MKU","FRN"],
        "Sastra Indonesia":  ["MKU","IND"],
        "Sastra Inggris":    ["MKU","ENG"],
        "Sastra Mandarin":   ["MKU","MAN"],
        "Sastra Jepang":     ["MKU","JPN"],
        "Sastra Arab":       ["MKU","ARB"],
        "Ilmu Sejarah":      ["MKU","SEJ"],
        "Arkeologi":         ["MKU","ARK"],
        "Sastra Daerah":     ["MKU","DAE"],
    }

    import random
    random.seed(42)

    for std in STUDENTS:
        u = User(username=std["nim"], hashed_password=hashed_pw, role="STUDENT")
        db.add(u)
        db.commit()

        status = compute_status(std["ipk"], std["semester"])

        s = Student(
            user_id=u.id,
            nim=std["nim"],
            nama=std["nama"],
            angkatan=std["angkatan"],
            semester=std["semester"],
            prodi=std["prodi"],
            email=std["email"],
            nomor_whatsapp=std["nomor_whatsapp"],
            status=std["status"],
        )
        db.add(s)
        db.commit()

        # Academic record (current semester)
        sks_total = std["semester"] * 20  # approx
        rec = AcademicRecord(
            student_id=s.id,
            semester=std["semester"],
            ips=std["ips"],
            ipk=std["ipk"],
            sks=min(sks_total, 144),
            status=status,
        )
        db.add(rec)

        # Additional older records for trend simulation
        if std["semester"] >= 3:
            for sem in range(1, std["semester"]):
                delta = random.uniform(-0.15, 0.15)
                old_ips = max(1.0, min(4.0, std["ipk"] + delta))
                db.add(AcademicRecord(
                    student_id=s.id,
                    semester=sem,
                    ips=round(old_ips, 2),
                    ipk=round(std["ipk"] + random.uniform(-0.1, 0.1), 2),
                    sks=sem * 20,
                    status=compute_status(std["ipk"], sem),
                ))

        # Grades for relevant courses up to current semester
        prefixes = prodi_course_prefix.get(std["prodi"], ["MKU"])
        relevant = [
            c for kode, c in course_map.items()
            if any(kode.startswith(p) for p in prefixes)
            if c.semester <= std["semester"]
        ]
        for course in relevant:
            # Generate grade based on IPK
            base = std["ipk"]
            grade_val = max(0.0, min(4.0, base + random.uniform(-0.5, 0.5)))
            # Map to letter
            if grade_val >= 3.7:   letter = "A"
            elif grade_val >= 3.3: letter = "A-"
            elif grade_val >= 3.0: letter = "B+"
            elif grade_val >= 2.7: letter = "B"
            elif grade_val >= 2.3: letter = "B-"
            elif grade_val >= 2.0: letter = "C+"
            elif grade_val >= 1.7: letter = "C"
            elif grade_val >= 1.3: letter = "D"
            else:                  letter = "E"

            db.add(Grade(
                student_id=s.id,
                course_id=course.id,
                grade=letter,
                bobot=round(grade_val, 2),
            ))

        db.commit()

    total_students = db.query(Student).count()
    total_courses  = db.query(Course).count()
    total_advisors = db.query(Advisor).count()
    high_risk      = db.query(AcademicRecord).filter(AcademicRecord.status == "HIGH_RISK").count()
    warning        = db.query(AcademicRecord).filter(AcademicRecord.status == "Warning").count()

    print("\n✅ Seed selesai!")
    print(f"   👥 Mahasiswa   : {total_students}")
    print(f"   📚 Mata Kuliah : {total_courses}")
    print(f"   👨‍🏫 Dosen PA    : {total_advisors}")
    print(f"   🚨 HIGH RISK   : {high_risk} mahasiswa")
    print(f"   ⚠️  Warning     : {warning} mahasiswa")
    db.close()


if __name__ == "__main__":
    run_seed()
