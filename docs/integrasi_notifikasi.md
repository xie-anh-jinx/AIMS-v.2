# Panduan Integrasi WhatsApp & Email (Notification Engine)

Dokumen ini menjelaskan bagaimana arsitektur AIMS (Academic Intelligence Management System) menangani pengiriman pesan pengingat (*reminder*) otomatis melalui WhatsApp dan Email kepada mahasiswa/dosen.

Semua logika *dispatch* notifikasi terpusat pada `NotificationEngine` yang berada di `services/notification_service/notification_engine.py`.

---

## 1. Integrasi WhatsApp (Via OpenClaw)

Untuk WhatsApp, AIMS menggunakan layanan eksternal berbasis CLI bernama **OpenClaw** (yang berjalan di atas Baileys/WhatsApp Web).

### Prasyarat
- Node.js terinstal di sisi *server*.
- CLI `openclaw` terinstal secara global (`npm install -g openclaw`).
- *Gateway* OpenClaw berjalan di latar belakang (dikelola oleh *runner* `npm run dev` pada `package.json` Anda yakni `"openclaw gateway"`).

### Cara Kerja di Backend
Saat modul kecerdasan buatan (*AI Agent*) atau sistem mendeteksi kebutuhan untuk mengirim *reminder* via WhatsApp (misalnya status *High Risk*), sistem akan memanggil fungsi `_send_whatsapp(phone, message)` di *backend*.

Kode ini akan secara dinamis menjalankan `subprocess` CLI berikut:
```bash
openclaw message send --channel whatsapp --target <nohp> --message "<pesan>"
```

### Langkah Menautkan Nomor Pengirim (Sender)
Agar sistem bisa mengirim pesan sungguhan, Anda harus menautkan nomor WhatsApp Anda ke dalam OpenClaw:
1. Buka terminal server.
2. Tambahkan _channel_ WhatsApp ke OpenClaw jika belum ada:
   ```bash
   openclaw channels add --channel whatsapp
   ```
3. Lakukan *login* (scan QR Code dengan aplikasi WhatsApp di HP Anda):
   ```bash
   openclaw channels login --channel whatsapp
   ```
4. Setelah terhubung, sistem otomatis bisa menembak pesan ke mahasiswa mengatasnamakan nomor WhatsApp tersebut.

---

## 2. Integrasi Email (Fase 3)

Saat ini (Fase 2), fitur email masih berjalan dalam mode **Mock (Simulasi)**. Ketika sebuah notifikasi dijadwalkan via email, sistem AIMS hanya akan mencatat (*log*) pesan ke dalam *database* dan mencetaknya di layar (*console*):
`INFO: [EMAIL MOCK] → mahsiswa@unhas.ac.id ...`

### Rencana Implementasi Produksi (Fase 3)
Untuk mengubah Email dari status *Mock* ke *Production*, Anda perlu memperbarui `services/notification_service/notification_engine.py` pada fungsi `_send_email`. 

Ada dua pendekatan paling direkomendasikan untuk menembak email *reminder*:

#### Opsi 2A: Menggunakan protokol SMTP murni (Python `smtplib`)
Sangat cocok jika universitas sudah menyediakan akun email resmi atau Google Workspace (Gmail SMTP).
```python
import smtplib
from email.message import EmailMessage

def _send_email(self, email: str, message: str):
    msg = EmailMessage()
    msg.set_content(message)
    msg['Subject'] = "Peringatan Akademik AIMS"
    msg['From'] = "aims-noreply@kampus.ac.id"
    msg['To'] = email

    # Ganti dengan SMTP relay kampus Anda
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login('akun_pengirim@kampus.ac.id', 'password_app_atau_rahasia')
        smtp.send_message(msg)
```

#### Opsi 2B: Menggunakan Layanan Resend / SendGrid (API Base)
Sangat cocok jika ingin bebas dari masuk *folder Spam* dan butuh analitik siapa saja yang membuka email.
```python
import httpx

def _send_email(self, email: str, message: str):
    # Menggunakan layanan Resend (https://resend.com)
    api_key = "re_123456789"
    headers = {"Authorization": f"Bearer {api_key}"}
    payload = {
        "from": "AIMS Bot <onboarding@resend.dev>",
        "to": [email],
        "subject": "Evaluasi SKS & Konsultasi",
        "html": f"<p>{message}</p>"
    }
    httpx.post("https://api.resend.com/emails", json=payload, headers=headers)
```

### Kesimpulan
- **WhatsApp**: Sepenuhnya bergantung pada utilitas CLI `openclaw`. Pastikan HP Anda selalu *online* jika menggunakan WABeta.
- **Email**: Perlu dipasang (*replace*) modul kodenya menjadi paket peladen surat (SMTP) sesungguhnya ketika siap meluncur.
- **Database**: Kedua jejak pesan ini tetap selalu direkam ke tabel `notification_logs` dengan status `SENT` atau `FAILED` di database utama.
