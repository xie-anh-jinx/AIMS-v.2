#!/bin/bash
# ==========================================================
# AIMS - OpenClaw WhatsApp Setup Script
# Jalankan file ini untuk menghubungkan AIMS ke WhatsApp Anda
# ==========================================================

set -e

echo ""
echo "╔══════════════════════════════════════════════════════╗"
echo "║     AIMS - OpenClaw WhatsApp Integration Setup      ║"
echo "╚══════════════════════════════════════════════════════╝"
echo ""

# 1. Check Node.js
if ! command -v node &>/dev/null; then
  echo "❌ Node.js tidak ditemukan. Install terlebih dahulu:"
  echo "   curl -fsSL https://deb.nodesource.com/setup_20.x | sudo bash - && sudo apt install -y nodejs"
  exit 1
fi
echo "✅ Node.js: $(node -v)"

# 2. Check npm
if ! command -v npm &>/dev/null; then
  echo "❌ npm tidak ditemukan."
  exit 1
fi

# 3. Install OpenClaw jika belum ada
if ! command -v openclaw &>/dev/null; then
  echo ""
  echo "📦 Menginstall OpenClaw..."
  npm install -g openclaw
  echo "✅ OpenClaw berhasil diinstall"
else
  echo "✅ OpenClaw: $(openclaw --version 2>/dev/null || echo 'installed')"
fi

# 4. Tambahkan channel WhatsApp
echo ""
echo "📱 Menambahkan channel WhatsApp (akan menginstall plugin Baileys)..."
openclaw channels add --channel whatsapp

# 5. Login WhatsApp (scan QR)
echo ""
echo "🔗 Login WhatsApp via QR Code:"
echo "   → Buka WhatsApp di HP Anda"
echo "   → Tap: ⋮ Menu → Linked Devices → Link a Device"
echo "   → Scan QR code yang akan muncul di bawah ini"
echo ""
openclaw channels login --channel whatsapp

# 6. Start gateway di background
echo ""
echo "🚀 Menjalankan OpenClaw Gateway di background..."
nohup openclaw gateway > /tmp/openclaw-gateway.log 2>&1 &
GATEWAY_PID=$!
echo "   Gateway PID: $GATEWAY_PID"
echo "   Log: /tmp/openclaw-gateway.log"

# 7. Tunda sebentar dan cek status
sleep 3
if openclaw channels status 2>/dev/null | grep -q "whatsapp"; then
  echo ""
  echo "╔══════════════════════════════════════════════════════╗"
  echo "║  ✅ OpenClaw WhatsApp AKTIF!                        ║"
  echo "║  AIMS kini bisa mengirim notifikasi ke WhatsApp     ║"
  echo "╚══════════════════════════════════════════════════════╝"
else
  echo ""
  echo "⚠️  Gateway mungkin perlu waktu beberapa detik."
  echo "   Cek status dengan: openclaw channels status"
  echo "   Log gateway: tail -f /tmp/openclaw-gateway.log"
fi

echo ""
echo "💡 Untuk menjalankan gateway ulang setelah reboot:"
echo "   openclaw gateway"
echo ""
