# Dokumentasi Arsitektur Teknis & Pengembang AIMS (Academic Integrated Management System)

Dokumen ini ditujukan bagi pengembang dan administrator sistem untuk memahami arsitektur kode, integrasi skema basis data, pemetaan API, serta cara mengoperasikan dan mengembangkan platform AIMS.

---

## 🏗️ 1. Arsitektur Umum & Direktori Proyek

AIMS menggunakan struktur monorepo terorganisir yang memisahkan logika backend (Python FastAPI), frontend (Next.js), modul basis data, serta komponen notifikasi/bot:

```text
├── apps/
│   ├── backend/             # Server API utama (FastAPI, Uvicorn)
│   │   ├── main.py          # Titik masuk backend & CORS configuration
│   │   └── routers/         # Endpoint modular (auth, admin, prodi, advisor, students)
│   ├── frontend/            # Aplikasi Client (Next.js App Router, Tailwind CSS, Lucide)
│   │   └── src/app/         # Halaman layout per role (admin, prodi, advisor, student)
│   └── telegram_bot/        # Layanan bot Telegram untuk siaran notifikasi mahasiswa
├── packages/
│   └── database/            # Kkoneksi PostgreSQL & model tabel SQLAlchemy
│       ├── connection.py    # Lokasi Engine & Sessionmaker SessionLocal
│       └── models.py        # Definisi struktur Relasional SQLAlchemy (ORM)
├── plugins/
│   └── academic-connector/  # Integrasi Scraper & Sync API NeoSIA (Node.js & Python)
├── services/
│   ├── ai_agent_service/     # Rule Engine untuk deteksi dini risiko mahasiswa
│   └── notification_service/ # Notification Engine (penyalur WhatsApp/Telegram/Email)
├── alembic/                 # Folder migrasi skema basis data
└── aims-cli.sh              # Wrapper CLI untuk mengontrol OpenClaw & simulator webhook
```

---

## 🗄️ 2. Skema Relasional Database (PostgreSQL)

Berikut adalah entitas utama yang disimpan dalam basis data utama `aims_db` (Port: `5435`):

```mermaid
erDiagram
    users ||--o| students : "user_id"
    users ||--o| advisors : "user_id"
    users ||--o| prodi_admins : "user_id"
    students ||--o{ academic_records : "student_id"
    students ||--o{ consultation_logs : "student_id"
    advisors ||--o{ consultation_logs : "advisor_id"
    advisors ||--o{ students : "membimbing (advisor_id)"
    
    users {
        int id PK
        string username
        string hashed_password
        string role "ADMIN | PRODI | ADVISOR | STUDENT"
        string email
        string whatsapp
        string profile_picture
    }
    students {
        int id PK
        string nim UNIQUE
        string nama
        string prodi
        string angkatan
        string status "Aktif | Lulus | Drop Out | Cuti | Non Aktif"
        string phone_number_wa
        string nomor_whatsapp
        string telegram_username
        int advisor_id FK
        int user_id FK
    }
    advisors {
        int id PK
        string nip UNIQUE
        string nama
        string prodi
        string email
        string whatsapp
        string telegram_username
        int user_id FK
    }
    prodi_admins {
        int id PK
        string prodi_name UNIQUE
        string nama
        string email
        string whatsapp
        int user_id FK
    }
    academic_records {
        int id PK
        int student_id FK
        string semester "2023-Gasal etc"
        float ips
        float ipk
        int sks
        string status "Aman | Warning | HIGH_RISK"
    }
```

### Sinkronisasi Kontak Kredensial
Untuk menghindari degradasi integritas data, kolom kontak disinkronkan secara konsisten:
- **Mahasiswa**: Perubahan `phone_number_wa` pada portal mahasiswa secara otomatis menyematkan nilai yang sama ke dalam kolom `nomor_whatsapp` di tabel `Student` (digunakan oleh Notification Rule Engine).
- **Admin & Prodi**: Data email dan whatsapp dihubungkan langsung dari endpoint `/profile` ke kolom model terkait.

---

## 🔌 3. Pemetaan Endpoint API (API Endpoints Map)

### Auth (`Router: auth.py`)
- `POST /auth/login` → Menerima form login, menelusuri data, menerbitkan Bearer JWT Token.
- `PUT /auth/profile-picture` → Unggah data image Base64 untuk foto profil.

### Admin Dashboard (`Router: admin.py`)
- `GET /admin/overview` → Mengembalikan rekap agregasi jumlah dosen, mahasiswa, tingkat risiko, dan logs.
- `GET /admin/stats/risk-per-prodi` → Mengembalikan data JSON perbandingan risiko antar prodi untuk Stacked Bar Chart.
- `GET /admin/profile` & `PUT /admin/profile` → Pengambilan & perubahan kredensial/kontak Admin.

### Program Studi (`Router: prodi.py`)
- `GET /prodi/overview` → Statistik jumlah mahasiswa per kategori risiko sesuai departemen Kaprodi yang login.
- `GET /prodi/students` → Mengambil data mahasiswa prodi (dukungan filter angkatan 2019-2025, search, status, paginasi).
- `GET /prodi/advisors` → Daftar dosen pembimbing akademik prodi pendamping.
- `GET /prodi/profile` & `PUT /prodi/profile` → Pengambilan & perubahan data profil Kaprodi.

### Dosen Wali / Advisor (`Router: advisor.py`)
- `GET /advisor/students` → Laporan deteksi mahasiswa asuhan di bawah naungan NIP Dosen PA.
- `GET /advisor/consultations` & `POST /advisor/consultations` → CRUD riwayat catatan bimbingan akademik.
- `GET /advisor/profile` & `PUT /advisor/profile` → Pengambilan & perubahan profil Dosen PA.

### Portal Mahasiswa (`Router: students.py`)
- `GET /students/{nim}/records` → Mengambil nilai IPS/IPK per semester dari database lokal.
- `GET /students/{nim}/transcript` → Rincian transkrip mata kuliah NeoSIA.
- `PUT /students/{nim}/profile` → Perubahan email, WhatsApp, Telegram, username, dan Password mahasiswa.

---

## ⚙️ 4. Logika Rule Engine & Skema Notifikasi

### Rule Engine (`services/ai_agent_service/rule_engine.py`)
Mesin ini memindai data evaluasi mahasiswa menggunakan parameter hirarki untuk menetapkan tindakan:
1. Aturan `EXPLICIT_HIGH_RISK` $\rightarrow$ Mengecek apakah `AcademicRecord.status == "HIGH_RISK"`.
2. Aturan `EXPLICIT_WARNING` $\rightarrow$ Mengecek apakah `AcademicRecord.status == "Warning"`.
3. Aturan `LOW_IPK` $\rightarrow$ Jika IPK aktif $> 0.0$ dan $< 2.0$.
4. Aturan `STUDY_DURATION_LIMIT` $\rightarrow$ Jika angkatan mahasiswa $\le 2019$ (Semester $\ge 13$).

### Notification Dispatcher (`services/notification_service/notification_engine.py`)
Saluran notifikasi diarahkan secara konkruen:
- **WhatsApp**: Backend menjalan utilitas CLI `openclaw` via `subprocess` untuk mengirim pesan melalui API Baileys WA Web yang terhubung.
- **Telegram**: Menggunakan API HTTP Telegram untuk menembak pesan siaran ke ID Obrolan yang terdaftar pada token bot.
- **Email**: Saat ini mengeksekusi Mock Log. Pendapatan SMTP terencana (smtplib Python) siap diimplementasikan untuk versi rilis penuh.

---

## 🛠️ 5. Cara Menjalankan Lingkungan Pengembangan Lokal

Pastikan Anda memiliki Node.js, Python 3.12, PostgreSQL, dan Redis terinstal.

1. **Docker Servis (Database & Cache)**:
   Hidupkan penampung docker postgres dan redis:
   ```bash
   docker compose up -d
   ```
2. **Setup virtualenv Python & dependensi backend**:
   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt   # Atau api requirements
   ```
3. **Database Migration (Alembic)**:
   Jalankan migrasi skema tabel terbaru:
   ```bash
   npm run db:migrate
   ```
4. **Menjalankan Program Secara Bersamaan**:
   Eksekusi runner concurrently di root workspace untuk memicu port backend (8000), frontend (3000), telegram bot, dan gateway OpenClaw sekaligus:
   ```bash
   npm run dev
   ```
5. **Menghentikan Layanan**:
   ```bash
   npm run stop
   ```
