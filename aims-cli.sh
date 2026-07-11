#!/bin/bash

# ==========================================
# AIMS (Academic AI System) - OpenClaw CLI Wrapper
# ==========================================

show_help() {
    echo "=========================================="
    echo " 🤖 AIMS OpenClaw Control CLI"
    echo "=========================================="
    echo "Penggunaan: ./aims-cli.sh [perintah] [opsi]"
    echo ""
    echo "Perintah Tersedia:"
    echo "  status            : Mengecek status OpenClaw Gateway di latar belakang."
    echo "  wa-login          : Menampilkan QR Code untuk menautkan nomor WhatsApp agen Bot."
    echo "  wa-logout         : Memutuskan tautan sesi WhatsApp saat ini."
    echo "  send-wa [No] [Pesan] : Mengirim pesan WhatsApp percobaan secara instan."
    echo "  trigger-webhook   : Mengirim sinyal simulasi Yudisium ke Webhook AIMS (localhost:8000)."
    echo ""
    echo "Contoh:"
    echo "  ./aims-cli.sh send-wa 62812345678 \"Halo Mahasiswa, IPK anda 1.54\""
    echo "=========================================="
}

case "$1" in
    status)
        echo "🔍 Menelusuri daemon OpenClaw..."
        if pgrep -f "openclaw" > /dev/null; then
            echo "✅ OpenClaw Gateway saat ini SEDANG BERJALAN."
        else
            echo "❌ OpenClaw Gateway TIDAK BERJALAN."
            echo "   (Jalankan 'npm run dev' di terminal lain untuk menghidupkan)."
        fi
        ;;
        
    wa-login)
        echo "📱 Memanggil Modul WhatsApp OpenClaw..."
        # Membuka terminal interaktif untuk scan QR
        openclaw channel add whatsapp --interact
        ;;
        
    wa-logout)
        echo "🔌 Memutuskan sesi WhatsApp..."
        openclaw channel remove whatsapp
        echo "✅ Sesi terhapus."
        ;;
        
    send-wa)
        if [ -z "$2" ] || [ -z "$3" ]; then
            echo "❌ Galat: Format salah."
            echo "✅ Benar: ./aims-cli.sh send-wa 62812345 \"pesan\""
            exit 1
        fi
        echo "🚀 Mengirim pesan ke $2 via OpenClaw..."
        openclaw message send --channel whatsapp --to "$2" "$3"
        echo "✅ Perintah eksekusi selesai."
        ;;
        
    trigger-webhook)
        echo "📡 Menembakkan Sinyal Simulasi POST ke Webhook AIMS (Port: 8000)..."
        curl -X POST http://localhost:8000/webhook/univ-sync \
             -H "Content-Type: application/json" \
             -H "x-aims-secure-token: AIMS-PROD-SECRET-998877" \
             -d '{
                   "event_type": "YUDISIUM_FINAL",
                   "semester_id": "2023-Gasal",
                   "target_prodi": "FIB"
                 }'
        echo ""
        echo "✅ Sinyal Webhook Terkirim!"
        ;;
        
    *)
        show_help
        ;;
esac
