# Academic Intelligence Management System (AIMS)

Academic Intelligence Management System (AIMS) adalah platform sistem informasi akademik inovatif yang dirancang untuk membantu pimpinan perguruan tinggi, pimpinan program studi, dan Dosen Penasihat Akademik (PA) dalam memantau secara proaktif perkembangan dan performa mahasiswa.

> [!IMPORTANT]
> **Kebijakan Integritas & Kedaulatan Data (Satu Arah dari NeoSIA)**
> Seluruh agregat data akademik mahasiswa, status pembayaran (UKT/SPP), rencana studi (KRS), dan nilai historis (KHS) yang ditampilkan di aplikasi AIMS **bersumber secara langsung (sinkronisasi satu arah)** dari Data Warehouse Induk universitas, yaitu sistem **NeoSIA**.
> 
> Aplikasi AIMS **TIDAK memiliki fungsi untuk menambah, mengubah, memanipulasi, atau mengedit** data riil apapun pada NeoSIA. AIMS didedikasikan sepenuhnya sebagai *alat bantu pendukung koordinasi akademik* yang menitikberatkan pada tiga fungsi utama:
> 1. Fasilitas **Pemantauan (Monitoring)** proaktif.
> 2. Perekaman **Koordinasi Log** antara dosen PA dan mahasiswa.
> 3. Fasilitas broadcast **Pengingat / Notifikasi (Reminder)**.

---

## 📌 Signifikansi Program & Keunggulan AIMS

Berbeda dengan antarmuka sistem akademik konvensional, AIMS dirumuskan untuk menjemput dan menangani isu akademis sedini mungkin:
1. **Pemantauan Dini Potensi Putus Studi (D.O.):** Sistem mengklasifikasikan mahasiswa ke dalam zona risiko secara *real-time* (Aman, Kuning, Merah) menyederhanakan upaya intervensi oleh pengelola Program Studi.
2. **Pusat Resolusi Konseling Akademik:** Mengkurasi dan memastikan instruksi pimpinan terhadap mahasiswa bermasalah dieksekusi secara nyata oleh Dosen PA (dilengkapi tombol validasi penutupan masa konseling). 
3. **Otomatisasi Penyiaran Pesan (Agent-Driven):** Implementasi robot cerdas berbasis *Artificial Intelligence Agent* *(OpenClaw)* yang terus mengawasi status mahasiswa di balik layar 24/7.

---

## 🤖 Agen AI Notifikasi (OpenClaw Engine)
Sistem AIMS dilengkapi dengan pilar asisten virtual cerdas yang bekerja di latar belakang (backend) yang disebut **OpenClaw Agent**. Modul ini mengambil alih tugas pemantauan manual yang membebani staf administrasi pendidikan.

**Mekanisme Kerja Agen OpenClaw:**
* **Evaluasi Berkala Secara Independen:** Menggunakan fasilitas penjadwalan (*scheduler*), bot secara periodik mengunjungi *database* untuk meninjau *Ruleset* batasan IPK/IPS atau hambatan pendaftaran KRS semester saat ini.
* **Otomasi Pengumpulan Keputusan (Workflow Engine):** Saat agen mendeteksi mahasiswa A sudah memenuhi syarat berstatus kritis, OpenClaw merumuskan peringatan. 
* **Distribusi Paralel ke Perangkat Ponsel (*Multi-Channel Dispatcher*):** Fitur utama dari OpenClaw adalah kemampuannya menembakkan pesan notifikasi yang *actionable* langsung menuju gawai pintar (*smartphone*) Mahasiswa atau Dosen via **WhatsApp Web/CLI maupun bot Telegram** sehingga esensi kecepatan tanggap sistem *early warning* tercapai.

---

## 📋 Ekosistem Portal Pengguna

Platform AIMS menyediakan portal akses (*Dashboard*) spesifik dengan privasi berlapis sesuai hierarki jabatan akademik:

### 1. Dasbor Administrator & Pimpinan (Prodi/Fakultas)
*   **Auditorium Analisis Risiko:** Peta distribusi persentase mahasiswa berdasarkan tingkat keamanan studi mereka per prodi atau per angkatan.
*   **Manajemen Tugas Eksekutif:** Fasilitas Pimpinan mengomunikasikan instruksi bimbingan secara internal melalui aplikasi AIMS yang di-*forward* ke halaman antarmuka Dosen PA bersangkutan.
*   **Modul Woro-Woro (Manual Broadcast Agent):** Eksekutif berhak memakai antarmuka AIMS untuk mendelegasikan tugas pada agen OpenClaw agar seketika (`Force Trigger`) menembak "Pesan Broadcast Peringatan SPP / Status Belajar" kepada parameter target khusus (contoh: Hanya kepada golongan batas Zona Merah di angkatan `2024`).

### 2. Dasbor Dosen Penasehat Akademik (PA)
*   **Inventarisasi Mahasiswa Bimbingan:** Melihat rangkuman IPK perwalian tanpa perlu repot menggali log per mahasiswa secara terpisah di platform NeoSIA yang padat.
*   **Gembok Log Resolusi (Audit Trail Konsultasi):** Jika dosen telah memegang permohonan bimbingan (akibat panggilan pimpinan), dosen diwajibkan menuliskan catatan observasi lalu mengganti status dari *Tertunda* menjadi *Selesai* guna melaporkan tindak lanjut aman. Resolusi ini tidak dapat dimanipulasi (*Soft-delete*).

### 3. Portal Mahasiswa
*   **Eksekutif Resume Kelulusan:** Visualisasi performa IP/IPK (Grafik fluktuasi garis) dilengkapi tabel agregasi simulasi transkrip sisa dan pemenuhan syarat minimal sks.
*   **Sinkronisasi Peringatan NeoSIA Terpadu:** Modul proaktif (*Reminder Box*) yang mendengarkan API validasi dari pusat tentang prasyarat pengisian kalender KRS atau teguran dari pihak fakultas.

---

## ⚙️ Petunjuk Instalasi Khusus (Bagi Divisi IT / Pengembang)

Proyek AIMS terkonfigurasi berbasis `concurrently`, yang bekerja sebagai perpaduan platform arsitektur modern (*monorepo* FastAPI & NextJS).

### Kebutuhan Server (Prasyarat)
*   `Node.js` (Versi 18 ke atas)
*   `Python` 3.12 (Memerlukan pembuatan *virtual environment `venv`* sebelum instalasi modul internal)
*   Dapur pacu rdbms `PostgreSQL` dipastikan siap huni (*running*) pada pelabuhan 5432 di jaringan *cluster* institusi/lokal.

### Menjalankan Infrastruktur Repositori
Jalankan satu skrip di bawah pada CLI pusat (/root/AIMS) untuk mereplikasi *environment backend* (API Gateway), kerangka UI *Next.js*, serta Modul Otomasi Evaluator secara berbarengan:
```bash
npm run dev
```

### Panduan Tautan Eksekusi Dasar
*   🔗 **Backend API & Swagger REST Docs:** `http://localhost:8000/docs`
*   🔗 **Dashboard(Mahasiswa & Dosen):** `http://localhost:3000`
*   🔗 **Pengaturan Admin:** `http://localhost:3002`

---

## 🚀 Peta Jalan Pengembangan Berkelanjutan (Future Work)
Sistem logikal dasar milik AIMS berkapabilitas masif untuk terus dimajukan menjadi model Kampus Pintar (*Smart Edu*):
1. **Layanan Interaktif LLM (AI Chatbot AIMS):** Pembaruan agen bot Telegram/WhatsApp kampus agar tak sekadar pasif melempar peringatan statis, tapi menjadi sarana tanyajawab di mana AI mampu membalas pertanyaan seperti, *"Dokumen syarat apa saja jika IPS saya < 1.0 kelak?"* dan merancang jadwal belajar proaktif menelisik dokumen kurikulum prodi.
2. **Kalkulator Kegagalan (Machine Learning Predictions):** Bertransformasi dari pengecekan kondisi konvensional IF/ELSE ruleset *threshold* SPP—menjadi penerapan rumusan algoritma prediktif, di mana mesin mampu membaca tendensi data dari profil lulusan sepuluh (10) tahun terakhir guna meraba apakah maba *(mahasiswa baru)* berpeluang drop-out hanya bermodal capaian KHS semester pertamanya.

*Hak Cipta (c) Digiweave.*
