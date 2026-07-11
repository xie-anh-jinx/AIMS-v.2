# OpenClaw - Academic Connector SDK

Ekosistem Enterprise Information Gateway untuk AIMS. Melakukan ekstraksi, validasi, dan sinkronisasi data dari berbagai SIAKAD universitas (Legacy Systems) menggunakan desain *Micro-Plugin Architecture* dan YAML Workflows.

## Keunggulan (Enterprise Features)
- **Layer Abstraksi Modular:** Mendukung API REST, SQL DB, CSV Dump, dan Web Scraping Playwright.
- **Dynamic Provider Registry:** Plug-and-play untuk ratusan universitas berbeda tanpa perlu menyalin kode (`providers/neosia`, `providers/generic`).
- **YAML Workflows:** Menjalankan pipeline ETL yang dapat dikonfigurasi sepenuhnya via `.yml`.
- **Tingkat Observabilitas: Logger & Metrics Level Audit, Sync, Debug**.
- **Retry Jitter & Queue System:** Proses sinkronisasi masif dengan Exponential Backoff + Timeout, mencegah *memory overflow*.
- **AI-Ready Facade:** Jembatan API native untuk *Intelligent Agents / LLM* mengoperasikan penambangan data.

## Struktur Provider
Konfigurasi per-universitas berada di folder `providers/{nama_kampus}`:
- `config.yml`: Konfigurasi Kredensial, Browser, API, Retry.
- `selectors.yml`: ID CSS DOM per-halaman.
- `mapping.yml`: Filter translasi (Menerjemahkan kolom `NIM` di web ke `student_id` DB).

## Menjalankan SDK
Untuk mensimulasikan orkestrasi peramban secara penuh, jalankan:
```bash
node example.js
```
Lihat keluaran observabilitas di folder `/logs`.
