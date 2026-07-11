# Academic Intelligence Management System (AIMS)

Academic Intelligence Management System (AIMS) adalah platform sistem informasi akademik terintegrasi yang dirancang untuk institusi pendidikan tinggi (dengan studi kasus purwarupa Fakultas Ilmu Budaya). Platform ini berfokus pada manajemen data akademik (berbasis *Role-Based Access Control*), pemantauan berkala, dan implementasi Sistem Peringatan Dini Akademik (*Academic Early-Warning System*).

---

## 📌 Deskripsi Sistem

Berbeda dengan sistem informasi akademik konvensional yang mencatat data secara pasif, AIMS dirancang secara proaktif. Sistem melakukan pemantauan performa mahasiswa (Indeks Prestasi Kumulatif/IPK) secara otomatis dan berkala. Apabila sistem mendeteksi indikasi penurunan prestasi akademik atau risiko putus studi (*drop-out*), modul kecerdasan (*Rule Engine*) akan secara otomatis memicu pengiriman notifikasi peringatan kepada mahasiswa maupun pemberitahuan kepada Dosen Penasehat Akademik (PA).

Sistem ini dikembangkan menggunakan kerangka arsitektur *Microservices* mandiri pada repositori tunggal (*monorepo*). Secara teknis, platform ini memisahkan layanan pengolahan data (backend), penyajian antarmuka (frontend mahasiswa dan dosen, serta dasbor administrator), dan modul otomatisasi evaluasi.

---

## 📋 Fitur Fungsional Saat Ini

### 1. Dasbor Administrator Center
Antarmuka sentral untuk pemangku kebijakan akademik tingkat perguruan tinggi.
*   **Manajemen Data Mahasiswa:** Tabel inventarisasi data akademik mahasiswa dari seluruh program studi.
*   **Analisis Profil Risiko:** Klasifikasi dan visualisasi statistik mahasiswa (menggunakan *Pie Chart* dan *Bar Chart*) ke dalam metrik zona risiko (Kritis, Peringatan, Stabil) berdasarkan IPK.
*   **Konfigurasi Batas Evaluasi:** Formulir pengaturan batasan toleransi nilai (contoh: IPK < 2.00) dan pengaktifan modul integrasi notifikasi (Webhook OpenClaw).

### 2. Dasbor Dosen Penasehat Akademik (PA)
Fasilitas monitoring untuk Dosen PA atas mahasiswa perwalian.
*   **Visualisasi Kinerja Individu:** Identifikasi cepat mahasiswa yang berada pada kategori berisiko agar tindakan preventif dapat segera dilakukan.
*   **Perekaman Konsultasi Peringatan:** Modul (tahap *mockup*) untuk mencatat tindak lanjut terhadap panggilan *High-Risk* dan status persetujuan KRS.
*   **Push Notification System:** Menerima rekaman pemberitahuan tindakan otomatis dari *Agent Service* secara spesifik untuk mahasiswa bimbingannya.

### 3. Portal Mahasiswa
Sistem informasi akses personal yang transparan.
*   **Pemantauan Kelulusan:** Visualisasi grafik indikator perolehan SKS dan tren capaian IPS/IPK per semester.
*   **Kotak Masuk Notifikasi Terpadu:** Modul pusat notifikasi peringatan akademis (contoh: *warning* IPK menurun) ataupun aktivitas administratif lainnya.
*   **Simulasi Kartu Rencana Studi (KRS):** Tampilan daftar penyusunan KRS mahasiswa berdasarkan penawaran semester berjalan tingkat fakultas.

### 4. Background Job & Notifikasi Agentik (OpenClaw Engine)
*   **Modul Evaluasi (Python APScheduler):** Sub-sistem otomatis yang memicu proses komputasi terhadap kinerja akademik seluruh mahasiswa pada satuan waktu yang dikonfigurasi.
*   **Rule/Workflow Engine:** Logika pemeriksa standar akademik (*business logic*).
*   **OpenClaw Node.js Automation:** Gateway *headless* atau penggerak untuk sistem eksternal, dieksekusi melalui perintah CLI yang berpotensi terkoneksi melalui saluran WhatsApp atau Telegram API.

---

## 🚀 Opsi Pengembangan Sistem Lanjutan (Future Work)

Sistem AIMS telah memiliki modul dasar yang kuat untuk memperluas fungsionalitasnya. Berikut adalah ruang pengembangan potensial yang dapat diimplementasikan selanjutnya:

1.  **Integrasi AI Chatbot Dua Arah (Large Language Model)**  
    Fasilitas integrasi API model bahasa (seperti OpenAI atau Groq LLM) pada tautan penerima (*webhook*) saluran WhatsApp yang dimandatkan ke OpenClaw. Modul ini memungkinkan mahasiswa membalas pesan peringatan IPK dan berkonsultasi mengenai strategi peningkatan nilai kepada *Chatbot AI*, yang mana bot memiliki konteks terhadap transkrip KRS mahasiswa.
2.  **Sistem Prediksi berbasis *Machine Learning***  
    Meningkatkan logika *Rule Engine* yang kini menggunakan aturan kaku (if/else threshold IPK) menjadi model regresi/ML murni (*Random Forest/Neural Network*), untuk dapat memprediksi risiko kegagalan studi di semester pertama berdasarkan nilai portofolio dan kecepatan pengumpulan SKS.
3.  **Digitalisasi KRS Melalui Scraping Sistem *Legacy***  
    Penggunaan ekstensi *headless browser* (fitur bawaan kerangka OpenClaw) untuk mengotomatisasi interaksi dengan portal lama (*Legacy* SIAKAD) demi mengambil jadwal matakuliah aktual dan memindahkannya ke sistem baru jika infrastruktur *API Restful* institutsi masih terbatas.
4.  **Otomatisasi Laporan Administratif PDF**  
    Pencetakan laporan berkala atas status mahasiswa D.O. langsung berformat PDF menuju basis data Universitas (Dinas Kependidikan Pusat).

---

## ⚙️ Petunjuk Sistem (Local Development)

Proyek AIMS terkonfigurasi berbasis `concurrently`, sehingga seluruh lapisan pelayanan dan antarmuka aktif dari satu terminal *root*.

### Prasyarat
*   `Node.js` (Versi 18 ke atas)
*   `Python` 3.12 (Aktivasi pada *virtual environment `venv`*)
*   `PostgreSQL` dipastikan menyala pada port 5432 di jaringan lokal

### Menjalankan Infrastruktur Repositori

Memulai instalasi, migrasi, hingga menjalankan lima kluster mikro secara serempak (Backend FastAPI, Frontend Next.js, Admin Next.js, Polling Telegram, OpenClaw):
```bash
npm run dev
```

(Opsional) Menginisialisasi Ulang Data Simulasi Purwarupa Fakultas:
```bash
npm run db:seed
```

### Panduan Tautan Lokal
*   🔗 **Backend API & Swagger Docs:** `http://localhost:8000/docs`
*   🔗 **Portal Terpadu (Mahasiswa & Dosen):** `http://localhost:3000`
*   🔗 **Dasbor Manajemen Admin:** `http://localhost:3002`

*(Data akun demonstran terlampir dan tervalidasi pada UI Login antarmuka masing-masing).*
