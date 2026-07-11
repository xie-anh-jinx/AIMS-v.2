# Dokumen Kebutuhan Integrasi API AIMS - SIAKAD Universitas

Dokumen ini memuat spesifikasi antarmuka pemrograman aplikasi (API) yang diharapkan dapat disajikan oleh tim DTI / Pengelola SIAKAD Universitas. API ini menggunakan paradigma *RESTful* (alur penarikan data dari AIMS ke server SIAKAD per periode/bulan).

Sistem AIMS hanya bertindak sebagai "Pembaca" *(Read-Only/Pull)* dan tidak akan pernah melakukan tindakan Destruktif (*Update/Delete*) pada server Universitas Anda.

## Basis Informasi Integrasi
- **Protokol:** HTTP/HTTPS REST
- **Metode Pengambilan:** Seluruh rute diharapkan menggunakan metode `GET`.
- **Sistem Autentikasi (Auth):** Diharapkan Universitas memberikan kunci akses berupa statis `API-Key` atau `Bearer Token` yang dilampirkan pada HTTP Headers. (Cth: `Authorization: Bearer <token_rahasia_SIAKAD>`)
- **Format Respon:** JSON (JavaScript Object Notation).

---

## 1. Endpoint: Master Data Mahasiswa Aktif
AIMS membutuhkan data daftar mahasiswa lengkap untuk menyusun hierarki dasbor.

*   **Method & Endpoint:** `GET /ai-integration/v1/students`
*   **Query Parameters yang Diharapkan:**
    *   `fakultas` (String): Filter spesifik fakultas (Cth: "FIB")
    *   `status` (String): Filter status akademik (Cth: "AKTIF")
*   **Contoh Respon (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "nim": "2021401001",
      "nama_lengkap": "Kotaro Miyabi",
      "program_studi": "Sastra Jepang",
      "angkatan": 2021,
      "status_akademik": "AKTIF",
      "no_whatsapp": "08123456789",  // Wajib (Bila ada) untuk Engine Peringatan WA AIMS
      "email_universitas": "kotaro@fib.univ.ac.id"
    }
  ]
}
```

---

## 2. Endpoint: Rekapitulasi Nilai & Transkrip Akademik (Core AI Data)
Ini adalah endpoint yang paling vital. AIMS (*Cronjob Scheduler* di bulan tertentu) akan memanggil endpoint ini untuk setiap mahasiswa demi menilai apakah mereka berada pada zona Drop Out atau tidak.

*   **Method & Endpoint:** `GET /ai-integration/v1/academic-records/{nim}`
*   **Path Variable:** `{nim}` = Nomor Induk Mahasiswa
*   **Contoh Respon (200 OK):**
```json
{
  "status": "success",
  "data": {
    "nim": "2021401001",
    "semester_berjalan": 5,
    "ipk_kumulatif": 1.75,         // Sinyal Peringatan Utama
    "ips_terakhir": 1.50,
    "total_sks_lulus": 64,
    "detail_mengulang": 3          // SKS/Matkul yang tidak lulus (Opsional)
  }
}
```

---

## 3. Endpoint: Relasi Dosen Penasehat Akademik (PA)
Sistem butuh memetakan setiap anak yang terdeteksi AI AIMS, lari ke Dosen mana daftarnya.

*   **Method & Endpoint:** `GET /ai-integration/v1/advisors/mapping`
*   **Query Parameters yang Diharapkan:** `prodi_id` = Sastra Inggris
*   **Contoh Respon (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "nidn": "99332211",
      "nama_dosen": "Dr. Dosen Sastra, M.A.",
      "nomor_telegram": "dosen_fb",
      "anak_wali": [
        "2021401001", 
        "2021401002",
        "2021401005"
      ]
    }
  ]
}
```

---

## 4. Endpoint: Daftar Modul KRS & Jadwal Kuliah Fakultas
Ditujukan agar portal AIMS dapat memvisualisasikan rekomendasi perbaikan paket mata kuliah mahasiswa di menu dasbor mahasiswa.

*   **Method & Endpoint:** `GET /ai-integration/v1/courses/schedule`
*   **Query Parameter (Filters):** `semester_id` (Cth: 2023-Gasal), `fakultas` (Cth: FIB)
*   **Contoh Respon (200 OK):**
```json
{
  "status": "success",
  "data": [
    {
      "kode_mk": "FIB-101",
      "nama_matakuliah": "Metodologi Penelitian Bahasa",
      "sks": 3,
      "tipe": "WAJIB",
      "jadwal": "Selasa, 08:00 - F201"
    }
  ]
}
```

---

### Strategi Eksekusi Pengambilan Data (Scheduler Polling)
Berdasarkan rutinitas penarikan per-bulan:
1. Setiap tanggal yang ditentukan pada pukul 03.00 dini hari (atau melalui tombol *Trigger* Manual di Admin Dasbor AIMS), Mesin Engine berjalan di belakang layar.
2. Pertama, ia menarik seluruh list NIM aktif terbaru (Endpoint 1).
3. Ia berjalan (*looping*) menanyakan profil transkrip setiap anak tersebut ke Endpoint 2 menggunakan metode asinkron *(sangat efisien di jaringan)*.
4. Ketika menemukan adanya angka IPK mendarat di bawah standar kritis, ia membedah rute Endpoint 3 untuk mencari tahu siapa Dosen PA-nya, lalu Bot OpenClaw melontarkan peringatan ganda (WhatsApp Mahasiswa & Telegram Dosen).
